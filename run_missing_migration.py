#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to run the missing manga_volume_cache migration.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.base.logging import LOGGER
# Import the migration module dynamically
import importlib.util
import os

migration_path = os.path.join(os.path.dirname(__file__), 'backend/migrations/0008_add_manga_volume_cache.py')
spec = importlib.util.spec_from_file_location('migration_module', migration_path)
migration_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration_module)

# Get the migrate function
migrate = migration_module.migrate
from backend.internals.db import execute_query


def main():
    """Run the missing migration."""
    LOGGER.info("Checking if manga_volume_cache table exists")
    
    # Check if the table exists
    result = execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='manga_volume_cache'")
    
    if result:
        LOGGER.info("manga_volume_cache table already exists")
    else:
        LOGGER.info("manga_volume_cache table does not exist, creating it now")
        migrate()
        
        # Mark migration as applied in migrations table
        execute_query(
            "INSERT OR IGNORE INTO migrations (migration_file) VALUES (?)",
            ("0008_add_manga_volume_cache.py",),
            commit=True
        )
        
        LOGGER.info("Migration completed successfully")


if __name__ == "__main__":
    main()
