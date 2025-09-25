#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cleanup script to remove duplicate collections and fix default collection issues.
"""

import sqlite3
from pathlib import Path

def main():
    """Clean up collections in the database."""
    # Connect to the database
    db_path = Path("data/db/readloom.db")
    if not db_path.exists():
        print(f"Database file not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Find all default collections
    cursor.execute("SELECT * FROM collections WHERE is_default = 1")
    default_collections = cursor.fetchall()
    
    print(f"Found {len(default_collections)} default collections")
    
    # Keep only one default collection (the first one)
    if len(default_collections) > 1:
        first_default = default_collections[0]
        print(f"Keeping collection '{first_default['name']}' (ID: {first_default['id']}) as default")
        
        # Remove default flag from all others
        cursor.execute(
            "UPDATE collections SET is_default = 0 WHERE is_default = 1 AND id != ?",
            (first_default['id'],)
        )
        conn.commit()
        print(f"Removed default flag from {len(default_collections) - 1} collections")
    
    # Find all collections named "Default Collection"
    cursor.execute("SELECT * FROM collections WHERE name = 'Default Collection'")
    named_default_collections = cursor.fetchall()
    
    print(f"Found {len(named_default_collections)} collections named 'Default Collection'")
    
    # Keep only one "Default Collection" (the one that's marked as default, or the first one)
    if len(named_default_collections) > 1:
        # Find if any is marked as default
        default_among_named = next((c for c in named_default_collections if c['is_default'] == 1), None)
        
        if default_among_named:
            keep_id = default_among_named['id']
            print(f"Keeping default collection with ID {keep_id}")
        else:
            keep_id = named_default_collections[0]['id']
            # Set this one as default
            cursor.execute("UPDATE collections SET is_default = 1 WHERE id = ?", (keep_id,))
            print(f"Setting collection with ID {keep_id} as default")
        
        # Delete all other "Default Collection" entries
        for collection in named_default_collections:
            if collection['id'] != keep_id:
                # First remove any relationships
                cursor.execute("DELETE FROM collection_root_folders WHERE collection_id = ?", (collection['id'],))
                cursor.execute("DELETE FROM series_collections WHERE collection_id = ?", (collection['id'],))
                
                # Then delete the collection
                cursor.execute("DELETE FROM collections WHERE id = ?", (collection['id'],))
                print(f"Deleted collection with ID {collection['id']}")
        
        conn.commit()
    
    # Verify the cleanup
    cursor.execute("SELECT * FROM collections WHERE is_default = 1")
    default_collections = cursor.fetchall()
    print(f"After cleanup: {len(default_collections)} default collections")
    
    cursor.execute("SELECT * FROM collections WHERE name = 'Default Collection'")
    named_default_collections = cursor.fetchall()
    print(f"After cleanup: {len(named_default_collections)} collections named 'Default Collection'")
    
    # List all remaining collections
    cursor.execute("SELECT * FROM collections")
    all_collections = cursor.fetchall()
    print("\nRemaining collections:")
    for collection in all_collections:
        print(f"  ID: {collection['id']}, Name: {collection['name']}, Default: {collection['is_default']}")
    
    conn.close()

if __name__ == "__main__":
    main()
