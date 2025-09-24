#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix script to completely reset and rebuild collections.
This script will:
1. Delete all collections except the ones you specify to keep
2. Create a single default collection if needed
3. Ensure all root folders are properly associated with collections
"""

import sqlite3
from pathlib import Path
import json

def main():
    """Fix collections in the database."""
    # Connect to the database
    db_path = Path("data/db/readloom.db")
    if not db_path.exists():
        print(f"Database file not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all collections
    cursor.execute("SELECT * FROM collections")
    all_collections = cursor.fetchall()
    
    print(f"Found {len(all_collections)} collections in total")
    for collection in all_collections:
        print(f"  ID: {collection['id']}, Name: {collection['name']}, Default: {collection['is_default']}")
    
    # Automatically determine which collections to keep
    # Keep collections named 'Manga' or 'Books' and the first Default Collection
    keep_ids = []
    default_collection_id = None
    
    for collection in all_collections:
        if collection['name'] in ['Manga', 'Books']:
            keep_ids.append(collection['id'])
        elif collection['name'] == 'Default Collection' and default_collection_id is None:
            default_collection_id = collection['id']
            keep_ids.append(collection['id'])
    
    print(f"\nAutomatically keeping collections with IDs: {keep_ids}")
    
    # Get root folders
    cursor.execute("SELECT * FROM root_folders")
    root_folders = cursor.fetchall()
    print(f"\nFound {len(root_folders)} root folders:")
    for folder in root_folders:
        print(f"  ID: {folder['id']}, Name: {folder['name']}, Path: {folder['path']}")
    
    # Delete all collections except the ones to keep
    for collection in all_collections:
        if collection['id'] not in keep_ids:
            # First remove any relationships
            cursor.execute("DELETE FROM collection_root_folders WHERE collection_id = ?", (collection['id'],))
            cursor.execute("DELETE FROM series_collections WHERE collection_id = ?", (collection['id'],))
            
            # Then delete the collection
            cursor.execute("DELETE FROM collections WHERE id = ?", (collection['id'],))
            print(f"Deleted collection with ID {collection['id']} ({collection['name']})")
    
    conn.commit()
    
    # Check if we need to create a default collection
    cursor.execute("SELECT * FROM collections WHERE is_default = 1")
    default_collections = cursor.fetchall()
    
    if not default_collections:
        # Create a default collection
        cursor.execute(
            "INSERT INTO collections (name, description, is_default) VALUES (?, ?, ?)",
            ("Default Collection", "Default collection created by the system", 1)
        )
        default_id = cursor.lastrowid
        print(f"Created new default collection with ID {default_id}")
        conn.commit()
    elif len(default_collections) > 1:
        # Keep only the first default collection
        first_default = default_collections[0]
        print(f"Keeping collection '{first_default['name']}' (ID: {first_default['id']}) as default")
        
        # Remove default flag from all others
        cursor.execute(
            "UPDATE collections SET is_default = 0 WHERE is_default = 1 AND id != ?",
            (first_default['id'],)
        )
        conn.commit()
    
    # Get the current collections after cleanup
    cursor.execute("SELECT * FROM collections")
    current_collections = cursor.fetchall()
    
    print("\nRemaining collections after cleanup:")
    for collection in current_collections:
        print(f"  ID: {collection['id']}, Name: {collection['name']}, Default: {collection['is_default']}")
    
    # Ensure all root folders are associated with at least one collection
    cursor.execute("SELECT * FROM collections WHERE is_default = 1")
    default_collection = cursor.fetchone()
    
    if default_collection:
        default_id = default_collection['id']
        
        for folder in root_folders:
            # Check if this root folder is associated with any collection
            cursor.execute(
                "SELECT COUNT(*) as count FROM collection_root_folders WHERE root_folder_id = ?",
                (folder['id'],)
            )
            count = cursor.fetchone()['count']
            
            if count == 0:
                # Add to default collection
                cursor.execute(
                    "INSERT INTO collection_root_folders (collection_id, root_folder_id) VALUES (?, ?)",
                    (default_id, folder['id'])
                )
                print(f"Added root folder {folder['id']} ({folder['name']}) to default collection")
        
        conn.commit()
    
    # Update the root_folders setting in settings table
    cursor.execute("SELECT * FROM root_folders")
    current_root_folders = cursor.fetchall()
    
    root_folders_setting = []
    for folder in current_root_folders:
        root_folders_setting.append({
            "id": folder['id'],
            "path": folder['path'],
            "name": folder['name'],
            "content_type": folder['content_type']
        })
    
    cursor.execute(
        "UPDATE settings SET value = ? WHERE key = 'root_folders'",
        (json.dumps(root_folders_setting),)
    )
    conn.commit()
    
    print("\nFixed root_folders setting in settings table")
    
    # Final verification
    cursor.execute("SELECT * FROM collections")
    final_collections = cursor.fetchall()
    
    print("\nFinal collections:")
    for collection in final_collections:
        cursor.execute(
            "SELECT COUNT(*) as count FROM collection_root_folders WHERE collection_id = ?",
            (collection['id'],)
        )
        folder_count = cursor.fetchone()['count']
        
        print(f"  ID: {collection['id']}, Name: {collection['name']}, Default: {collection['is_default']}, Root Folders: {folder_count}")
    
    conn.close()
    print("\nCollection cleanup complete!")

if __name__ == "__main__":
    main()
