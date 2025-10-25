#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration 0015: Add ebook-related columns to collection_items table.

This migration adds columns to support ebook file management in the collection items.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Add ebook-related columns to collection_items table."""
    LOGGER.info("Adding ebook-related columns to collection_items table")
    
    try:
        # Check if columns already exist
        columns = execute_query("PRAGMA table_info(collection_items)")
        column_names = [col["name"] for col in columns]
        
        # Add has_file column if it doesn't exist
        if "has_file" not in column_names:
            execute_query("""
                ALTER TABLE collection_items ADD COLUMN has_file INTEGER DEFAULT 0
            """, commit=True)
            LOGGER.info("Added has_file column to collection_items")
        else:
            LOGGER.info("has_file column already exists")
        
        # Add ebook_file_id column if it doesn't exist
        if "ebook_file_id" not in column_names:
            execute_query("""
                ALTER TABLE collection_items ADD COLUMN ebook_file_id INTEGER
            """, commit=True)
            LOGGER.info("Added ebook_file_id column to collection_items")
        else:
            LOGGER.info("ebook_file_id column already exists")
        
        # Add digital_format column if it doesn't exist
        if "digital_format" not in column_names:
            execute_query("""
                ALTER TABLE collection_items ADD COLUMN digital_format TEXT
            """, commit=True)
            LOGGER.info("Added digital_format column to collection_items")
        else:
            LOGGER.info("digital_format column already exists")
        
        LOGGER.info("Migration completed successfully")
        return True
    
    except Exception as e:
        LOGGER.error(f"Error during migration: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


def rollback():
    """Rollback the migration (optional)."""
    LOGGER.info("Rolling back ebook-related columns from collection_items")
    try:
        # Note: SQLite doesn't support dropping columns easily, so we'll just log it
        LOGGER.warning("SQLite doesn't support dropping columns. Manual cleanup may be needed.")
        return True
    except Exception as e:
        LOGGER.error(f"Error during rollback: {e}")
        return False
