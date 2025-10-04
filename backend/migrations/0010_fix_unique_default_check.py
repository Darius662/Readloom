#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration 0010: Force-remove legacy 'unique_default' CHECK constraint tied to name
and replace it with a simple boolean check plus a partial unique index to ensure
only one default collection.

This migration fixes cases where 0006 added a CHECK that allowed default only
when name = 'Default Collection', and 0007 failed to remove it due to using
PRAGMA table_info which does not expose CHECK constraints. As a result, updates
like setting 'Manga' as default would fail with:
  CHECK constraint failed: unique_default
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def _has_legacy_unique_default_check() -> bool:
    """Detect if the collections table has the legacy CHECK constraint.

    We inspect sqlite_master SQL since PRAGMA table_info does not list CHECKs.
    """
    try:
        rows = execute_query(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='collections'"
        )
        if not rows:
            return False
        sql = rows[0].get("sql", "") or ""
        # Heuristics: look for the constraint name or the name-based condition
        return (
            "CONSTRAINT unique_default" in sql
            and "name = 'Default Collection'" in sql
        )
    except Exception:
        # If detection fails, be conservative and return False
        return False


def migrate():
    LOGGER.info("Running migration 0010: Fix legacy unique_default CHECK on collections")

    # If table doesn't exist, nothing to do
    tables = execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='collections'")
    if not tables:
        LOGGER.info("Collections table not found; skipping migration 0010")
        return

    # If legacy constraint not present, ensure index exists and exit
    if not _has_legacy_unique_default_check():
        LOGGER.info("No legacy unique_default CHECK found; ensuring unique index exists")
        try:
            execute_query(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_default
                ON collections(is_default) WHERE is_default = 1
                """,
                commit=True,
            )
        except Exception as e:
            LOGGER.info(f"Index create note (may already exist): {e}")
        LOGGER.info("Migration 0010 completed (no changes needed)")
        return

    LOGGER.info("Legacy unique_default CHECK detected; recreating collections table")

    # Read all rows to migrate
    rows = execute_query("SELECT * FROM collections")

    # Move aside the old table safely
    execute_query("DROP TABLE IF EXISTS collections_old", commit=True)
    execute_query("ALTER TABLE collections RENAME TO collections_old", commit=True)

    # Create new collections table with correct constraint
    execute_query(
        """
        CREATE TABLE collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            is_default INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CHECK (is_default IN (0, 1))
        )
        """,
        commit=True,
    )

    # Create partial unique index to enforce single default
    execute_query(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_default
        ON collections(is_default) WHERE is_default = 1
        """,
        commit=True,
    )

    # Migrate data, allowing only the first default to remain
    default_seen = False
    for r in rows:
        is_def = r.get("is_default", 0) or 0
        if is_def == 1:
            if default_seen:
                is_def = 0
            else:
                default_seen = True
        execute_query(
            """
            INSERT INTO collections (id, name, description, is_default, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                r.get("id"),
                r.get("name"),
                r.get("description"),
                is_def,
                r.get("created_at"),
                r.get("updated_at"),
            ),
            commit=True,
        )

    # IMPORTANT: Recreate dependent tables to refresh foreign keys to point to 'collections'
    # Recreate collection_root_folders
    execute_query(
        """
        CREATE TABLE IF NOT EXISTS collection_root_folders_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id INTEGER NOT NULL,
            root_folder_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(collection_id, root_folder_id),
            FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
        )
        """,
        commit=True,
    )
    execute_query(
        "INSERT INTO collection_root_folders_new SELECT * FROM collection_root_folders",
        commit=True,
    )
    execute_query("DROP TABLE collection_root_folders", commit=True)
    execute_query(
        "ALTER TABLE collection_root_folders_new RENAME TO collection_root_folders",
        commit=True,
    )

    # Recreate series_collections
    execute_query(
        """
        CREATE TABLE IF NOT EXISTS series_collections_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_id INTEGER NOT NULL,
            collection_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(series_id, collection_id),
            FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
            FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
        )
        """,
        commit=True,
    )
    execute_query(
        "INSERT INTO series_collections_new SELECT * FROM series_collections",
        commit=True,
    )
    execute_query("DROP TABLE series_collections", commit=True)
    execute_query(
        "ALTER TABLE series_collections_new RENAME TO series_collections",
        commit=True,
    )

    # Drop the old collections table last
    execute_query("DROP TABLE collections_old", commit=True)

    LOGGER.info("Recreated collections table without legacy CHECK; migration 0010 done")
