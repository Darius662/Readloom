#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration 0011: Fix lingering references to collections_old

Some databases may still have relationship tables or other objects referencing
'collections_old' after previous migrations. This migration scans sqlite_master
and, if any object SQL contains 'collections_old', it rebuilds the dependent
relationship tables to refresh foreign keys to the current 'collections' table.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def _schema_mentions_collections_old() -> bool:
    rows = execute_query(
        "SELECT name, type, sql FROM sqlite_master WHERE sql LIKE '%collections_old%'"
    )
    return len(rows) > 0


def _table_exists(name: str) -> bool:
    return bool(
        execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    )


def migrate():
    LOGGER.info("Running migration 0011: Fix lingering references to collections_old")

    # If collections doesn't exist, nothing to do
    if not _table_exists("collections"):
        LOGGER.info("Collections table not found; skipping migration 0011")
        return

    if not _schema_mentions_collections_old():
        LOGGER.info("No references to collections_old found; migration 0011 not needed")
        return

    LOGGER.info("References to collections_old detected; rebuilding relationship tables")

    # Rebuild collection_root_folders if present
    if _table_exists("collection_root_folders"):
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
        LOGGER.info("Rebuilt collection_root_folders with refreshed foreign keys")

    # Rebuild series_collections if present
    if _table_exists("series_collections"):
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
        LOGGER.info("Rebuilt series_collections with refreshed foreign keys")

    LOGGER.info("Migration 0011 completed: references to collections_old resolved")
