#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration 0012: Add content_type to collections and enforce one default per content_type.

Changes:
- Add collections.content_type TEXT DEFAULT 'MANGA'.
- Drop legacy unique default index if present (idx_unique_default).
- Create partial unique index on (content_type, is_default=1): idx_unique_default_per_type.
- Backfill content_type for existing rows using heuristics:
  * If a collection has linked root_folders, copy the most common content_type among its root folders; else 'MANGA'.
- Normalize defaults: ensure at most one default per content_type.
"""

from collections import Counter
from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def _table_exists(name: str) -> bool:
    return bool(
        execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    )


essential_sql = {
    "add_column": "ALTER TABLE collections ADD COLUMN content_type TEXT DEFAULT 'MANGA'",
    "drop_old_index": "DROP INDEX IF EXISTS idx_unique_default",
    "create_new_index": (
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_default_per_type "
        "ON collections(content_type, is_default) WHERE is_default = 1"
    ),
}


def _has_column(table: str, column: str) -> bool:
    rows = execute_query(f"PRAGMA table_info({table})")
    return any(r.get("name") == column for r in rows)


def _backfill_content_type():
    rows = execute_query("SELECT id FROM collections")
    for r in rows:
        cid = r["id"]
        # Find linked root folders and their content types
        rf = execute_query(
            """
            SELECT rf.content_type
            FROM root_folders rf
            JOIN collection_root_folders crf ON crf.root_folder_id = rf.id
            WHERE crf.collection_id = ?
            """,
            (cid,),
        )
        ctype = "MANGA"
        if rf:
            cnt = Counter([x.get("content_type") or "MANGA" for x in rf])
            ctype = cnt.most_common(1)[0][0] or "MANGA"
        execute_query(
            "UPDATE collections SET content_type = ? WHERE id = ?",
            (ctype, cid),
            commit=True,
        )


def _normalize_defaults_per_type():
    # Get all content types present in collections
    types = execute_query("SELECT DISTINCT COALESCE(content_type, 'MANGA') AS ct FROM collections")
    for t in types:
        ct = t.get("ct") or "MANGA"
        defs = execute_query(
            "SELECT id FROM collections WHERE COALESCE(content_type, 'MANGA') = ? AND is_default = 1",
            (ct,),
        )
        if len(defs) > 1:
            # Keep the first, unset others
            keep_id = defs[0]["id"]
            execute_query(
                "UPDATE collections SET is_default = 0 WHERE COALESCE(content_type, 'MANGA') = ? AND is_default = 1 AND id != ?",
                (ct, keep_id),
                commit=True,
            )


def migrate():
    LOGGER.info("Running migration 0012: typed default collections")

    if not _table_exists("collections"):
        LOGGER.info("collections table not found; skipping 0012")
        return

    # 1) Add content_type column if missing
    if not _has_column("collections", "content_type"):
        try:
            execute_query(essential_sql["add_column"], commit=True)
            LOGGER.info("Added collections.content_type column")
        except Exception as e:
            LOGGER.error(f"Failed adding content_type column: {e}")
            raise
    else:
        LOGGER.info("collections.content_type already exists; skipping add")

    # 2) Backfill values
    try:
        _backfill_content_type()
        LOGGER.info("Backfilled collections.content_type values")
    except Exception as e:
        LOGGER.error(f"Error backfilling content_type: {e}")
        raise

    # 3) Replace unique index
    try:
        execute_query(essential_sql["drop_old_index"], commit=True)
    except Exception as e:
        LOGGER.info(f"Note dropping old index: {e}")

    try:
        execute_query(essential_sql["create_new_index"], commit=True)
        LOGGER.info("Created idx_unique_default_per_type partial unique index")
    except Exception as e:
        LOGGER.error(f"Error creating per-type default index: {e}")
        raise

    # 4) Normalize defaults per type (unset extra defaults)
    try:
        _normalize_defaults_per_type()
        LOGGER.info("Normalized defaults per content_type")
    except Exception as e:
        LOGGER.error(f"Error normalizing defaults: {e}")
        raise

    LOGGER.info("Migration 0012 completed successfully")
