#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Schema setup for collections and their relationships with root folders.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def setup_collections_tables():
    """Set up the collections tables if they don't exist."""
    try:
        # Create collections table
        execute_query("""
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            is_default INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_default CHECK (is_default = 0 OR is_default = 1)
        )
        """, commit=True)
        
        # Create collection_root_folders table for many-to-many relationship
        execute_query("""
        CREATE TABLE IF NOT EXISTS collection_root_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id INTEGER NOT NULL,
            root_folder_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(collection_id, root_folder_id),
            FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
        )
        """, commit=True)
        
        # Create root_folders table
        execute_query("""
        CREATE TABLE IF NOT EXISTS root_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            name TEXT NOT NULL,
            content_type TEXT DEFAULT 'MANGA',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(path)
        )
        """, commit=True)
        
        # Create series_collection table for many-to-many relationship
        execute_query("""
        CREATE TABLE IF NOT EXISTS series_collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_id INTEGER NOT NULL,
            collection_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(series_id, collection_id),
            FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
            FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
        )
        """, commit=True)
        
        # No longer automatically creating a default collection
        # Users will create their own collections through the UI
        LOGGER.info("Collections tables ready for user-created collections")
        
        LOGGER.info("Collections tables set up successfully")
    except Exception as e:
        LOGGER.error(f"Error setting up collections tables: {e}")
        raise
