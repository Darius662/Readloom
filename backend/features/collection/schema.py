#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Schema setup for collection tracking.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def setup_collection_tables():
    """Set up the collection tracking tables if they don't exist."""
    try:
        # Create collection items table
        execute_query("""
        CREATE TABLE IF NOT EXISTS collection_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_id INTEGER NOT NULL,
            volume_id INTEGER NULL,
            chapter_id INTEGER NULL,
            item_type TEXT NOT NULL CHECK(item_type IN ('SERIES', 'VOLUME', 'CHAPTER')),
            ownership_status TEXT NOT NULL CHECK(ownership_status IN ('OWNED', 'WANTED', 'ORDERED', 'LOANED', 'NONE')),
            read_status TEXT NOT NULL CHECK(read_status IN ('READ', 'READING', 'UNREAD', 'NONE')),
            format TEXT CHECK(format IN ('PHYSICAL', 'DIGITAL', 'BOTH', 'NONE')),
            condition TEXT CHECK(condition IN ('NEW', 'LIKE_NEW', 'VERY_GOOD', 'GOOD', 'FAIR', 'POOR', 'NONE')),
            purchase_date TEXT,
            purchase_price REAL,
            purchase_location TEXT,
            notes TEXT,
            custom_tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
            FOREIGN KEY (volume_id) REFERENCES volumes(id) ON DELETE CASCADE,
            FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
        )
        """, commit=True)
        
        # Create collection stats table
        execute_query("""
        CREATE TABLE IF NOT EXISTS collection_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            total_series INTEGER DEFAULT 0,
            total_volumes INTEGER DEFAULT 0,
            total_chapters INTEGER DEFAULT 0,
            owned_series INTEGER DEFAULT 0,
            owned_volumes INTEGER DEFAULT 0,
            owned_chapters INTEGER DEFAULT 0,
            read_volumes INTEGER DEFAULT 0,
            read_chapters INTEGER DEFAULT 0,
            total_value REAL DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        )
        """, commit=True)
        
        # Insert default stats record if it doesn't exist
        execute_query("""
        INSERT OR IGNORE INTO collection_stats (user_id) VALUES (1)
        """, commit=True)
        
        LOGGER.info("Collection tracking tables set up successfully")
    except Exception as e:
        LOGGER.error(f"Error setting up collection tables: {e}")
        raise
