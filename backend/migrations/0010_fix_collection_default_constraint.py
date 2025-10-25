#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration: Fix collection default constraint
- Removes the old CHECK constraint that was preventing default collections
- Adds a unique partial index to ensure only one default collection
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Run the migration to fix the collection default constraint."""
    try:
        LOGGER.info("Running migration: Fix collection default constraint")
        
        # Check if collections table exists
        tables = execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='collections'")
        if not tables:
            LOGGER.info("Collections table does not exist yet, skipping migration")
            return
        
        # SQLite doesn't support dropping constraints directly, so we need to recreate the table
        # First, check if we need to do this migration by trying to create the index
        try:
            execute_query("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_default 
            ON collections(is_default) WHERE is_default = 1
            """, commit=True)
            LOGGER.info("Created unique index for default collection")
        except Exception as e:
            LOGGER.info(f"Index might already exist or table needs recreation: {e}")
            
            # Get existing data
            collections = execute_query("SELECT * FROM collections")
            
            # Drop the old table
            execute_query("DROP TABLE IF EXISTS collections_old", commit=True)
            execute_query("ALTER TABLE collections RENAME TO collections_old", commit=True)
            
            # Create new table with correct constraint
            execute_query("""
            CREATE TABLE collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                is_default INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (is_default IN (0, 1))
            )
            """, commit=True)
            
            # Create the unique index
            execute_query("""
            CREATE UNIQUE INDEX idx_unique_default 
            ON collections(is_default) WHERE is_default = 1
            """, commit=True)
            
            # Migrate data - ensure only one default
            default_count = 0
            for collection in collections:
                is_default = collection['is_default']
                
                # Only allow the first default collection
                if is_default == 1:
                    if default_count > 0:
                        is_default = 0
                    default_count += 1
                
                execute_query("""
                INSERT INTO collections (id, name, description, is_default, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    collection['id'],
                    collection['name'],
                    collection['description'],
                    is_default,
                    collection['created_at'],
                    collection['updated_at']
                ), commit=True)
            
            # Drop old table
            execute_query("DROP TABLE collections_old", commit=True)
            
            LOGGER.info("Recreated collections table with correct constraint")
        
        LOGGER.info("Migration completed: Fix collection default constraint")
        
    except Exception as e:
        LOGGER.error(f"Error running migration: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        raise
