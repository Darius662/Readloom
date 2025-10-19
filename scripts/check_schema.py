#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Check the database schema.
"""

import os
import sys
import sqlite3

# Add parent directory to path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.base.logging import setup_logging, LOGGER
from backend.internals.db import set_db_location, execute_query

def check_schema():
    """Check the database schema."""
    # Set up logging
    setup_logging("data/logs", "check_schema.log")
    LOGGER.info("Checking database schema")
    
    # Set database location
    set_db_location("data/db")
    
    # Connect to the database
    conn = sqlite3.connect("data/db/readloom.db")
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("PRAGMA table_info(series)")
    columns = cursor.fetchall()
    
    print("Series table columns:")
    for column in columns:
        print(f"  {column[1]} ({column[2]})")
    
    # Check if is_book column exists
    is_book_exists = any(column[1] == "is_book" for column in columns)
    print(f"is_book column exists: {is_book_exists}")
    
    # Close connection
    conn.close()

if __name__ == "__main__":
    check_schema()
