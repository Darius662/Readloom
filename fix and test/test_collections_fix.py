#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify the fix for duplicate Default Collections.
This script will:
1. Check the current state of collections
2. Try to create a duplicate default collection (which should fail)
3. Verify that only one default collection exists
"""

import sqlite3
from pathlib import Path

def main():
    """Test the fix for duplicate Default Collections."""
    # Connect to the database
    db_path = Path("data/db/readloom.db")
    if not db_path.exists():
        print(f"Database file not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check current state of collections
    cursor.execute("SELECT * FROM collections")
    collections = cursor.fetchall()
    
    print("Current collections:")
    for collection in collections:
        print(f"  ID: {collection['id']}, Name: {collection['name']}, Default: {collection['is_default']}")
    
    # Count default collections
    cursor.execute("SELECT COUNT(*) as count FROM collections WHERE is_default = 1")
    default_count = cursor.fetchone()['count']
    print(f"\nNumber of default collections: {default_count}")
    
    # Try to create a duplicate default collection (should fail due to constraint)
    print("\nTrying to create a duplicate default collection...")
    try:
        cursor.execute("""
        INSERT INTO collections (name, description, is_default) 
        VALUES ('Another Default', 'This should fail', 1)
        """)
        conn.commit()
        print("ERROR: Created duplicate default collection! Fix is not working.")
    except sqlite3.IntegrityError as e:
        print(f"Success! Constraint prevented duplicate default collection: {e}")
    
    # Try to create a non-default collection (should succeed)
    print("\nTrying to create a non-default collection...")
    try:
        cursor.execute("""
        INSERT INTO collections (name, description, is_default) 
        VALUES ('Regular Collection', 'This should work', 0)
        """)
        conn.commit()
        print("Success! Created non-default collection.")
    except sqlite3.IntegrityError as e:
        print(f"ERROR: Could not create non-default collection: {e}")
    
    # Try to update an existing collection to be default (should fail)
    print("\nTrying to update a collection to be default...")
    try:
        cursor.execute("""
        UPDATE collections SET is_default = 1 
        WHERE name = 'Regular Collection'
        """)
        conn.commit()
        print("ERROR: Updated collection to be default! Fix is not working.")
    except sqlite3.IntegrityError as e:
        print(f"Success! Constraint prevented updating collection to default: {e}")
    
    # Check final state of collections
    cursor.execute("SELECT * FROM collections")
    collections = cursor.fetchall()
    
    print("\nFinal collections state:")
    for collection in collections:
        print(f"  ID: {collection['id']}, Name: {collection['name']}, Default: {collection['is_default']}")
    
    # Count default collections again
    cursor.execute("SELECT COUNT(*) as count FROM collections WHERE is_default = 1")
    default_count = cursor.fetchone()['count']
    print(f"\nFinal number of default collections: {default_count}")
    
    # Clean up test collection
    cursor.execute("DELETE FROM collections WHERE name = 'Regular Collection'")
    conn.commit()
    print("\nTest complete. Cleaned up test collection.")
    
    conn.close()

if __name__ == "__main__":
    main()
