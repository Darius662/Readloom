#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration runner for database schema updates.
"""

import importlib
import os
from pathlib import Path
from typing import List, Dict, Any

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def get_migration_files() -> List[str]:
    """Get a list of migration files sorted by version number.
    
    Returns:
        List[str]: List of migration file names.
    """
    migrations_dir = Path(__file__).parent.parent / "migrations"
    migration_files = []
    
    for file in os.listdir(migrations_dir):
        if file.endswith(".py") and file.startswith("0"):
            migration_files.append(file)
    
    # Sort by version number
    migration_files.sort()
    
    return migration_files


def get_applied_migrations() -> List[str]:
    """Get a list of migrations that have already been applied.
    
    Returns:
        List[str]: List of applied migration file names.
    """
    # Create migrations table if it doesn't exist
    execute_query("""
    CREATE TABLE IF NOT EXISTS migrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        migration_file TEXT NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(migration_file)
    )
    """, commit=True)
    
    # Get applied migrations
    result = execute_query("SELECT migration_file FROM migrations")
    return [row["migration_file"] for row in result]


def mark_migration_applied(migration_file: str) -> None:
    """Mark a migration as applied.
    
    Args:
        migration_file (str): The migration file name.
    """
    execute_query(
        "INSERT OR IGNORE INTO migrations (migration_file) VALUES (?)",
        (migration_file,),
        commit=True
    )


def run_migrations() -> None:
    """Run all pending migrations."""
    LOGGER.info("Checking for pending migrations")
    
    migration_files = get_migration_files()
    applied_migrations = get_applied_migrations()
    
    pending_migrations = [f for f in migration_files if f not in applied_migrations]
    
    if not pending_migrations:
        LOGGER.info("No pending migrations found")
        return
    
    LOGGER.info(f"Found {len(pending_migrations)} pending migrations")
    
    for migration_file in pending_migrations:
        LOGGER.info(f"Running migration: {migration_file}")
        
        try:
            # Import the migration module
            module_name = f"backend.migrations.{migration_file[:-3]}"
            migration_module = importlib.import_module(module_name)
            
            # Run the migration
            migration_module.migrate()
            
            # Mark migration as applied
            mark_migration_applied(migration_file)
            
            LOGGER.info(f"Migration {migration_file} completed successfully")
        except Exception as e:
            LOGGER.error(f"Error running migration {migration_file}: {e}")
            raise
