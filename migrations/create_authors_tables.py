#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration script to create the authors table and related tables.
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.base.logging import LOGGER

def create_authors_tables(db_path):
    """Create the authors table and related tables."""
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create authors table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            provider TEXT NOT NULL,
            provider_id TEXT NOT NULL,
            birth_date TEXT,
            death_date TEXT,
            biography TEXT,
            folder_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(provider, provider_id)
        )
        ''')
        
        # Create collection_authors table for many-to-many relationship
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection_authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
            FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE,
            UNIQUE(collection_id, author_id)
        )
        ''')
        
        # Create author_books table for many-to-many relationship
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS author_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER NOT NULL,
            series_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE,
            FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
            UNIQUE(author_id, series_id)
        )
        ''')
        
        # Commit the changes
        conn.commit()
        
        # Close the connection
        conn.close()
        
        LOGGER.info("Authors tables created successfully")
        return True
        
    except Exception as e:
        LOGGER.error(f"Error creating authors tables: {e}")
        return False

if __name__ == "__main__":
    # Get the database path from the environment or use the default
    db_path = os.environ.get("READLOOM_DB_PATH", "data/readloom.db")
    
    # Make sure the database path is absolute
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_path)
    
    # Create the authors tables
    success = create_authors_tables(db_path)
    
    if success:
        print("Authors tables created successfully")
    else:
        print("Error creating authors tables")
        sys.exit(1)
