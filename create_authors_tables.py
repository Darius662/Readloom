#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to create the authors tables directly in the database.
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

def create_authors_tables():
    """Create the authors tables directly in the database."""
    try:
        # Get the database path
        data_dir = os.environ.get('READLOOM_DATA_DIR', 'data')
        if not os.path.isabs(data_dir):
            # Make it absolute relative to the project root
            project_root = Path(__file__).parent
            data_dir = os.path.join(project_root, data_dir)
        
        # Ensure the data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Set the database path
        db_path = os.path.join(data_dir, 'readloom.db')
        
        print(f"Using database at: {db_path}")
        
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
        print("Created authors table")
        
        # Create collection_authors table
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
        print("Created collection_authors table")
        
        # Create author_books table
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
        print("Created author_books table")
        
        # Commit the changes
        conn.commit()
        
        # Close the connection
        conn.close()
        
        print("Authors tables created successfully")
        return True
        
    except Exception as e:
        print(f"Error creating authors tables: {e}")
        return False

if __name__ == "__main__":
    success = create_authors_tables()
    if not success:
        sys.exit(1)
