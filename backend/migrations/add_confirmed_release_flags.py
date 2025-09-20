#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration script to add confirmed_release flag to chapters and volumes.
"""

from backend.internals.db import execute_query

def run_migration():
    """Add confirmed_release flag to chapters and volumes tables."""
    try:
        # Add is_confirmed_date column to chapters table if it doesn't exist
        execute_query(
            """
            SELECT 1 FROM pragma_table_info('chapters') 
            WHERE name = 'is_confirmed_date'
            """
        )
        
        # If the column doesn't exist, add it
        if not execute_query("SELECT 1 FROM pragma_table_info('chapters') WHERE name = 'is_confirmed_date'"):
            execute_query(
                """
                ALTER TABLE chapters 
                ADD COLUMN is_confirmed_date INTEGER DEFAULT 0
                """,
                commit=True
            )
            print("Added is_confirmed_date column to chapters table")
        
        # Add is_confirmed_date column to volumes table if it doesn't exist
        if not execute_query("SELECT 1 FROM pragma_table_info('volumes') WHERE name = 'is_confirmed_date'"):
            execute_query(
                """
                ALTER TABLE volumes 
                ADD COLUMN is_confirmed_date INTEGER DEFAULT 0
                """,
                commit=True
            )
            print("Added is_confirmed_date column to volumes table")
            
        return True
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    run_migration()
