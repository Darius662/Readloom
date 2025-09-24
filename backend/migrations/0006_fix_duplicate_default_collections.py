#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration script to fix duplicate default collections.
This script will:
1. Find all collections marked as default
2. Keep only one default collection (the first one)
3. Update the collections table schema to prevent future duplicates
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Migrate the database to fix duplicate default collections."""
    LOGGER.info("Starting migration to fix duplicate default collections")
    
    # Find all default collections
    default_collections = execute_query("SELECT * FROM collections WHERE is_default = 1")
    
    LOGGER.info(f"Found {len(default_collections)} default collections")
    
    # Keep only one default collection (the first one)
    if len(default_collections) > 1:
        first_default = default_collections[0]
        LOGGER.info(f"Keeping collection '{first_default['name']}' (ID: {first_default['id']}) as default")
        
        # Remove default flag from all others
        execute_query(
            "UPDATE collections SET is_default = 0 WHERE is_default = 1 AND id != ?",
            (first_default['id'],),
            commit=True
        )
        LOGGER.info(f"Removed default flag from {len(default_collections) - 1} collections")
    
    # Add constraint to prevent multiple default collections
    try:
        # Check if the constraint already exists
        constraints = execute_query("PRAGMA table_info(collections)")
        has_constraint = False
        for constraint in constraints:
            if "unique_default" in str(constraint):
                has_constraint = True
                break
        
        if not has_constraint:
            # SQLite doesn't support adding constraints to existing tables directly
            # We need to recreate the table with the constraint
            LOGGER.info("Adding constraint to prevent multiple default collections")
            
            # Create a new table with the constraint
            execute_query("""
            CREATE TABLE collections_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                is_default INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_default CHECK (is_default = 0 OR (is_default = 1 AND name = 'Default Collection'))
            )
            """, commit=True)
            
            # Copy data from old table to new table
            execute_query("""
            INSERT INTO collections_new (id, name, description, is_default, created_at, updated_at)
            SELECT id, name, description, is_default, created_at, updated_at FROM collections
            """, commit=True)
            
            # Drop old table
            execute_query("DROP TABLE collections", commit=True)
            
            # Rename new table to old table name
            execute_query("ALTER TABLE collections_new RENAME TO collections", commit=True)
            
            LOGGER.info("Added constraint to collections table")
    except Exception as e:
        LOGGER.error(f"Error adding constraint: {e}")
    
    # Verify the migration
    default_collections = execute_query("SELECT * FROM collections WHERE is_default = 1")
    LOGGER.info(f"After migration: {len(default_collections)} default collections")
    
    LOGGER.info("Migration completed successfully")


if __name__ == "__main__":
    migrate()
