#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Move service for series between collections and/or root folders.

Phase 1: DB-only collection reassignment.
Phase 2: Physical folder migration with dry-run.
"""
from typing import Dict, Optional, List
import os
import shutil
from pathlib import Path

from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from backend.features.collection import get_collection_by_id
from backend.base.helpers import get_safe_folder_name


def _get_series(series_id: int) -> Optional[Dict]:
    rows = execute_query("SELECT * FROM series WHERE id = ?", (series_id,))
    return rows[0] if rows else None


def _get_series_collections(series_id: int) -> List[Dict]:
    return execute_query(
        """
        SELECT c.* FROM collections c
        JOIN series_collections sc ON sc.collection_id = c.id
        WHERE sc.series_id = ?
        ORDER BY c.content_type, c.name
        """,
        (series_id,),
    )


def move_series_db_only(
    series_id: int,
    target_collection_id: Optional[int] = None,
) -> Dict:
    """
    Reassign a series to a target collection (DB-only).

    - Ensures the target collection exists and is in a compatible content_type bucket.
    - Removes existing series_collections links for collections of the same bucket.
    - Adds link to the target collection.

    Returns summary dict with before/after collection memberships.
    """
    series = _get_series(series_id)
    if not series:
        raise ValueError(f"Series with id {series_id} not found")

    before = _get_series_collections(series_id)

    if target_collection_id is None:
        LOGGER.info("No target_collection_id provided; returning current memberships")
        return {"series_id": series_id, "before": before, "after": before, "changed": False}

    target = get_collection_by_id(int(target_collection_id))
    if not target:
        raise ValueError(f"Target collection {target_collection_id} not found")

    # Enforce same bucket as the series' content_type
    series_bucket = (series.get("content_type") or "MANGA").upper()
    target_bucket = (target.get("content_type") or "MANGA").upper()
    if series_bucket != target_bucket:
        raise ValueError(
            f"Bucket mismatch: series bucket {series_bucket} != target collection bucket {target_bucket}"
        )

    # Remove existing links within the same bucket
    execute_query(
        """
        DELETE FROM series_collections
        WHERE series_id = ? AND collection_id IN (
            SELECT id FROM collections WHERE UPPER(COALESCE(content_type,'MANGA')) = ?
        )
        """,
        (series_id, series_bucket),
        commit=True,
    )

    # Add link to target
    execute_query(
        "INSERT INTO series_collections (collection_id, series_id) VALUES (?, ?)",
        (int(target_collection_id), series_id),
        commit=True,
    )

    after = _get_series_collections(series_id)
    return {"series_id": series_id, "before": before, "after": after, "changed": True}


def _pick_collection_root_path(collection_id: int) -> Optional[Path]:
    rows = execute_query(
        """
        SELECT rf.path FROM root_folders rf
        JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
        WHERE crf.collection_id = ?
        ORDER BY rf.name ASC
        """,
        (collection_id,),
    )
    if rows:
        return Path(rows[0]["path"])  # first by name
    return None


def _get_root_path_by_id(root_folder_id: int) -> Optional[Path]:
    rows = execute_query("SELECT path FROM root_folders WHERE id = ?", (root_folder_id,))
    if rows:
        return Path(rows[0]["path"])  # type: ignore
    return None


def _current_series_dir(series: Dict, collection_root_path: Optional[Path]) -> Path:
    # Prefer custom_path if set
    custom_path = series.get("custom_path")
    if custom_path:
        return Path(custom_path)

    # Fall back to computed path from collection root (or best-effort)
    safe_title = get_safe_folder_name(series.get("title") or f"series_{series['id']}")
    if collection_root_path:
        return collection_root_path / safe_title

    # Last resort: attempt from any configured root folder of same bucket
    rows = execute_query(
        """
        SELECT rf.path FROM root_folders rf
        WHERE UPPER(COALESCE(rf.content_type,'MANGA')) = ?
        ORDER BY rf.name ASC
        LIMIT 1
        """,
        ((series.get("content_type") or "MANGA").upper(),),
    )
    if rows:
        return Path(rows[0]["path"]) / safe_title

    # Default to data ebooks directory-like fallback (do not import here to avoid side effects)
    return Path(os.getcwd()) / safe_title


def plan_series_move(
    series_id: int,
    target_collection_id: Optional[int] = None,
    target_root_folder_id: Optional[int] = None,
    move_files: bool = False,
    clear_custom_path: bool = False,
    dry_run: bool = False,
) -> Dict:
    """Plan and optionally execute a series move.

    Returns a plan dict. If not dry_run and move_files or collection change requested,
    applies the DB changes and file moves.
    """
    series = _get_series(series_id)
    if not series:
        raise ValueError(f"Series with id {series_id} not found")

    series_bucket = (series.get("content_type") or "MANGA").upper()

    # Determine before state
    before_memberships = _get_series_collections(series_id)

    # Resolve target collection
    target_collection = None
    if target_collection_id is not None:
        target_collection = get_collection_by_id(int(target_collection_id))
        if not target_collection:
            raise ValueError(f"Target collection {target_collection_id} not found")
        target_bucket = (target_collection.get("content_type") or "MANGA").upper()
        if target_bucket != series_bucket:
            raise ValueError(
                f"Bucket mismatch: series bucket {series_bucket} != target collection bucket {target_bucket}"
            )

    # Determine source and target directories
    source_collection_path: Optional[Path] = None
    # Try to infer current collection id within same bucket for computing source dir
    current_bucket_collection = next((c for c in before_memberships if (c.get("content_type") or "MANGA").upper() == series_bucket), None)
    if current_bucket_collection:
        source_collection_path = _pick_collection_root_path(current_bucket_collection["id"])  # type: ignore

    source_dir = _current_series_dir(series, source_collection_path)

    target_root_path: Optional[Path] = None
    if target_root_folder_id is not None:
        target_root_path = _get_root_path_by_id(int(target_root_folder_id))
        if target_root_path is None:
            raise ValueError(f"Target root folder {target_root_folder_id} not found")
    elif target_collection is not None:
        target_root_path = _pick_collection_root_path(target_collection["id"])  # type: ignore

    # Compute target directory only if we have a target root path and files move
    safe_title = get_safe_folder_name(series.get("title") or f"series_{series['id']}")
    target_dir = target_root_path / safe_title if target_root_path else None

    # Build plan
    plan: Dict = {
        "series_id": series_id,
        "series_bucket": series_bucket,
        "move_files": bool(move_files and target_dir is not None),
        "clear_custom_path": bool(clear_custom_path),
        "source_dir": str(source_dir) if source_dir else None,
        "target_dir": str(target_dir) if target_dir else None,
        "before_collections": before_memberships,
        "target_collection_id": int(target_collection_id) if target_collection_id is not None else None,
    }

    # If dry run, attempt to calculate approximate size and conflicts
    if plan["move_files"]:
        exists = source_dir.exists()
        conflict = target_dir.exists() if target_dir else False
        total_bytes = 0
        total_files = 0
        if exists:
            for root, _, files in os.walk(source_dir):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        total_bytes += os.path.getsize(fp)
                        total_files += 1
                    except Exception:
                        pass
        plan.update({
            "source_exists": exists,
            "target_exists": conflict,
            "estimated_bytes": total_bytes,
            "estimated_files": total_files,
        })

    if dry_run:
        plan["changed"] = False
        return plan

    # Apply DB collection reassignment if requested
    if target_collection_id is not None:
        _ = move_series_db_only(series_id=series_id, target_collection_id=target_collection_id)

    # Apply file move if requested and target is resolved
    if plan["move_files"] and target_dir is not None:
        target_dir_parent = target_dir.parent
        try:
            target_dir_parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Failed to prepare target parent directory: {target_dir_parent} ({e})")

        # If target exists, abort to avoid destructive merge in MVP
        if target_dir.exists():
            raise ValueError(f"Target directory already exists: {target_dir}")

        try:
            LOGGER.info(f"Moving series folder from '{source_dir}' to '{target_dir}'")
            shutil.move(str(source_dir), str(target_dir))
        except Exception as e:
            raise ValueError(f"Failed to move folder: {e}")

        # Optionally clear custom_path if we physically moved under managed root
        if clear_custom_path:
            execute_query(
                "UPDATE series SET custom_path = NULL, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (series_id,),
                commit=True,
            )

    plan["changed"] = True
    plan["after_collections"] = _get_series_collections(series_id)
    return plan
