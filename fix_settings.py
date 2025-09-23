#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
import os
from pathlib import Path

def main():
    """Fix the root_folders setting in the database."""
    # Connect to the database
    db_path = Path("data/db/mangarr.db")
    if not db_path.exists():
        print(f"Database file not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all root folders from the table
    cursor.execute("SELECT * FROM root_folders")
    folders = cursor.fetchall()
    
    # Convert to list of dictionaries
    root_folders = []
    for folder in folders:
        root_folders.append({
            "id": folder['id'],
            "path": folder['path'],
            "name": folder['name'],
            "content_type": folder['content_type']
        })
    
    # Update the root_folders setting
    cursor.execute(
        "UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
        (json.dumps(root_folders), "root_folders")
    )
    conn.commit()
    
    print(f"Updated root_folders setting with {len(root_folders)} folders:")
    for folder in root_folders:
        print(f"  ID: {folder['id']}, Path: {folder['path']}, Name: {folder['name']}")
    
    conn.close()

if __name__ == "__main__":
    main()
