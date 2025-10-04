#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Direct database fix script for Readloom.
This script will fix the collections table constraint issue.
"""

import os
import sqlite3
from pathlib import Path

# Define the path to the database
DB_PATH = Path("/config/data/readloom.db")

def fix_database():
    """Fix the collections table constraint issue."""
    print(f"Attempting to fix database at {DB_PATH}")
    
    if not DB_PATH.exists():
        print(f"Database file not found at {DB_PATH}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if collections table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='collections'")
        if not cursor.fetchone():
            print("Collections table does not exist, nothing to fix")
            conn.close()
            return True
        
        # Check if the constraint exists
        cursor.execute("PRAGMA table_info(collections)")
        has_constraint = False
        for row in cursor.fetchall():
            if "unique_default" in str(row):
                has_constraint = True
                break
        
        if not has_constraint:
            print("No problematic constraint found, nothing to fix")
            conn.close()
            return True
        
        print("Found problematic constraint, fixing...")
        
        # Create a backup of the collections table
        cursor.execute("CREATE TABLE IF NOT EXISTS collections_backup AS SELECT * FROM collections")
        
        # Drop the old table
        cursor.execute("DROP TABLE IF EXISTS collections")
        
        # Create the new table with correct constraints
        cursor.execute("""
        CREATE TABLE collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            is_default INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CHECK (is_default IN (0, 1))
        )
        """)
        
        # Create a unique index to ensure only one default collection
        cursor.execute("""
        CREATE UNIQUE INDEX idx_unique_default 
        ON collections(is_default) WHERE is_default = 1
        """)
        
        # Copy data from backup, ensuring only one default collection
        cursor.execute("""
        INSERT INTO collections (id, name, description, is_default, created_at, updated_at)
        SELECT 
            id, 
            name, 
            description, 
            CASE WHEN is_default = 1 AND rowid = (SELECT MIN(rowid) FROM collections_backup WHERE is_default = 1) THEN 1 ELSE 0 END as is_default,
            created_at, 
            updated_at
        FROM collections_backup
        """)
        
        # Fix the auto-increment sequence
        cursor.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(id) FROM collections) WHERE name = 'collections'")
        
        # Commit the changes
        conn.commit()
        
        print("Collections table fixed successfully")
        conn.close()
        return True
    except Exception as e:
        print(f"Error fixing database: {e}")
        return False

if __name__ == "__main__":
    fix_database()
