#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
import os
from pathlib import Path

def main():
    """Check the settings in the database."""
    # Connect to the database
    db_path = Path("data/db/readloom.db")
    if not db_path.exists():
        print(f"Database file not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if settings table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
    if not cursor.fetchone():
        print("Settings table does not exist")
        return
    
    # Get all settings
    cursor.execute("SELECT key, value FROM settings")
    settings = {row['key']: json.loads(row['value']) for row in cursor.fetchall()}
    
    print("Settings:")
    for key, value in settings.items():
        print(f"  {key}: {value}")
    
    # Check if root_folders setting exists
    if 'root_folders' in settings:
        print("\nRoot folders:")
        for folder in settings['root_folders']:
            print(f"  {folder}")
    else:
        print("\nNo root_folders setting found")
    
    # Check root_folders table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='root_folders'")
    if not cursor.fetchone():
        print("\nroot_folders table does not exist")
        return
    
    # Get all root folders from the table
    cursor.execute("SELECT * FROM root_folders")
    folders = cursor.fetchall()
    
    print("\nRoot folders from table:")
    for folder in folders:
        print(f"  ID: {folder['id']}, Path: {folder['path']}, Name: {folder['name']}, Content Type: {folder['content_type']}")
    
    # Check collections table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='collections'")
    if not cursor.fetchone():
        print("\ncollections table does not exist")
        return
    
    # Get all collections
    cursor.execute("SELECT * FROM collections")
    collections = cursor.fetchall()
    
    print("\nCollections:")
    for collection in collections:
        print(f"  ID: {collection['id']}, Name: {collection['name']}, Default: {collection['is_default']}")
    
    # Check collection_root_folders table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='collection_root_folders'")
    if not cursor.fetchone():
        print("\ncollection_root_folders table does not exist")
        return
    
    # Get all collection-root folder relationships
    cursor.execute("SELECT * FROM collection_root_folders")
    relationships = cursor.fetchall()
    
    print("\nCollection-Root Folder Relationships:")
    for rel in relationships:
        print(f"  Collection ID: {rel['collection_id']}, Root Folder ID: {rel['root_folder_id']}")
    
    conn.close()

if __name__ == "__main__":
    main()
