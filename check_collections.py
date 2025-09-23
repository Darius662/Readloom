#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path

def main():
    """Check collections in the database."""
    # Connect to the database
    db_path = Path("data/db/mangarr.db")
    if not db_path.exists():
        print(f"Database file not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check collections table
    cursor.execute("SELECT * FROM collections")
    collections = cursor.fetchall()
    
    print("Collections:")
    for collection in collections:
        print(f"  ID: {collection['id']}, Name: {collection['name']}, Default: {collection['is_default']}")
    
    # Check collection_root_folders table
    cursor.execute("SELECT * FROM collection_root_folders")
    relationships = cursor.fetchall()
    
    print("\nCollection-Root Folder Relationships:")
    for rel in relationships:
        print(f"  Collection ID: {rel['collection_id']}, Root Folder ID: {rel['root_folder_id']}")
    
    conn.close()

if __name__ == "__main__":
    main()
