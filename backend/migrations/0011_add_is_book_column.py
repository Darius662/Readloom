#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration to add is_book column to series table.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Add is_book column to series table."""
    try:
        # Check if column already exists
        try:
            execute_query("SELECT is_book FROM series LIMIT 1")
            LOGGER.info("is_book column already exists in series table")
            return True
        except Exception:
            # Column doesn't exist, add it
            LOGGER.info("Adding is_book column to series table")
            
            # Add the column
            execute_query(
                "ALTER TABLE series ADD COLUMN is_book INTEGER DEFAULT 0",
                commit=True
            )
            
            # Update existing records based on content_type
            execute_query(
                """
                UPDATE series 
                SET is_book = CASE 
                    WHEN UPPER(content_type) IN ('BOOK', 'NOVEL') THEN 1 
                    ELSE 0 
                END
                """,
                commit=True
            )
            
            LOGGER.info("is_book column added to series table")
            return True
    except Exception as e:
        LOGGER.error(f"Error adding is_book column: {e}")
        return False
