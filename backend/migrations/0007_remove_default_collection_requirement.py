#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration script to remove the requirement for a default collection.
This script will:
1. Update the collections table schema to allow any collection to be marked as default
2. Keep existing collections but remove the special status of "Default Collection"
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Migrate the database to remove default collection requirement."""
    LOGGER.info("Starting migration to remove default collection requirement")
    
    # Update the constraint on the collections table
    try:
        # SQLite doesn't support modifying constraints directly
        # We need to recreate the table with the updated constraint
        
        # First, check if we need to modify the constraint
        constraints = execute_query("PRAGMA table_info(collections)")
        constraint_text = ""
        for constraint in constraints:
            if "unique_default" in str(constraint):
                constraint_text = str(constraint)
                break
        
        if "Default Collection" in constraint_text:
            LOGGER.info("Updating collections table constraint")
            
            # Create a new table with the updated constraint
            execute_query("""
            CREATE TABLE collections_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                is_default INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_default CHECK (is_default = 0 OR is_default = 1)
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
            
            LOGGER.info("Updated collections table constraint")
        else:
            LOGGER.info("Collections table constraint already updated")
    
    except Exception as e:
        LOGGER.error(f"Error updating collections table constraint: {e}")
    
    # Log the current collections
    collections = execute_query("SELECT * FROM collections")
    LOGGER.info(f"Current collections ({len(collections)}):")
    for collection in collections:
        LOGGER.info(f"  ID: {collection['id']}, Name: {collection['name']}, Default: {collection['is_default']}")
    
    LOGGER.info("Migration completed successfully")


if __name__ == "__main__":
    migrate()
