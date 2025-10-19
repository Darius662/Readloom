#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration: Add manga_volume_cache table for dynamic volume caching.

This migration creates a table to cache volume counts from web scraping,
replacing the static hardcoded database with a dynamic caching system.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Create the manga_volume_cache table."""
    LOGGER.info("Creating manga_volume_cache table")
    
    # Create the cache table
    execute_query("""
        CREATE TABLE IF NOT EXISTS manga_volume_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manga_title TEXT NOT NULL,
            manga_title_normalized TEXT NOT NULL,
            anilist_id TEXT,
            mal_id TEXT,
            chapter_count INTEGER NOT NULL DEFAULT 0,
            volume_count INTEGER NOT NULL DEFAULT 0,
            source TEXT NOT NULL,
            status TEXT,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            refresh_count INTEGER DEFAULT 0,
            UNIQUE(manga_title_normalized)
        )
    """, commit=True)
    
    # Create indexes for better performance
    execute_query("""
        CREATE INDEX IF NOT EXISTS idx_manga_cache_anilist 
        ON manga_volume_cache(anilist_id)
    """, commit=True)
    
    execute_query("""
        CREATE INDEX IF NOT EXISTS idx_manga_cache_title 
        ON manga_volume_cache(manga_title_normalized)
    """, commit=True)
    
    execute_query("""
        CREATE INDEX IF NOT EXISTS idx_manga_cache_refreshed 
        ON manga_volume_cache(refreshed_at)
    """, commit=True)
    
    LOGGER.info("manga_volume_cache table created successfully")


def rollback():
    """Rollback the migration (optional)."""
    LOGGER.info("Rolling back manga_volume_cache table")
    execute_query("DROP TABLE IF EXISTS manga_volume_cache", commit=True)
    LOGGER.info("manga_volume_cache table dropped")
