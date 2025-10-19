#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.base.custom_exceptions import DatabaseError
from backend.base.definitions import Constants
from backend.base.helpers import ensure_dir_exists, get_data_dir
from backend.base.logging import LOGGER

# These imports will be done inside setup_db to avoid circular imports

# Global variables
DB_PATH: Optional[Path] = None
DB_CONN: Optional[sqlite3.Connection] = None


def set_db_location(db_folder: Optional[str] = None) -> None:
    """Set the location of the database.

    Args:
        db_folder (Optional[str], optional): The folder to store the database in.
            Defaults to None.

    Raises:
        ValueError: If the database location is not a folder.
    """
    global DB_PATH
    
    if db_folder:
        folder_path = Path(db_folder)
        if not folder_path.exists() or not folder_path.is_dir():
            raise ValueError("Database location is not a folder")
    else:
        folder_path = get_data_dir()
    
    DB_PATH = folder_path / Constants.DEFAULT_DB_NAME
    LOGGER.info(f"Database path set to: {DB_PATH}")


def get_db_connection(timeout: int = 30) -> sqlite3.Connection:
    """Get a connection to the database with improved timeout handling.

    Args:
        timeout (int, optional): Connection timeout in seconds. Defaults to 30.

    Returns:
        sqlite3.Connection: A connection to the database.

    Raises:
        DatabaseError: If the database connection could not be established.
    """
    global DB_CONN
    
    if DB_CONN is not None:
        return DB_CONN
    
    if DB_PATH is None:
        set_db_location()
    
    try:
        # Set a longer timeout to help with locked database issues
        DB_CONN = sqlite3.connect(DB_PATH, timeout=timeout, check_same_thread=False, 
                                   isolation_level=None)  # Autocommit mode
        
        # Use DELETE journal mode instead of WAL for Docker compatibility
        # WAL mode doesn't work well with network filesystems and Docker volumes
        result = DB_CONN.execute('PRAGMA journal_mode = DELETE')
        journal_mode = result.fetchone()[0]
        LOGGER.info(f"Database journal mode set to: {journal_mode}")
        
        # Set busy timeout to wait instead of immediately failing
        DB_CONN.execute(f'PRAGMA busy_timeout = {timeout * 1000}')
        
        # Set synchronous mode to NORMAL for better performance while maintaining safety
        DB_CONN.execute('PRAGMA synchronous = NORMAL')
        
        # Enable foreign keys
        DB_CONN.execute('PRAGMA foreign_keys = ON')
        
        DB_CONN.row_factory = sqlite3.Row
        LOGGER.info("Database connection established successfully")
        return DB_CONN
    except Exception as e:
        LOGGER.error(f"Could not connect to database: {e}")
        raise DatabaseError(f"Could not connect to database: {e}")


def close_db_connection() -> None:
    """Close the database connection."""
    global DB_CONN
    
    if DB_CONN is not None:
        DB_CONN.close()
        DB_CONN = None


def execute_query(query: str, params: Tuple = (), commit: bool = False, max_retries: int = 5, retry_delay: float = 0.5) -> List[Dict[str, Any]]:
    """Execute a SQL query with retry logic for handling database locks.

    Args:
        query (str): The SQL query to execute.
        params (Tuple, optional): The parameters for the query. Defaults to ().
        commit (bool, optional): Whether to commit the transaction. Defaults to False.
        max_retries (int, optional): Maximum number of retries if database is locked. Defaults to 5.
        retry_delay (float, optional): Delay between retries in seconds. Defaults to 0.5.

    Returns:
        List[Dict[str, Any]]: The results of the query.

    Raises:
        DatabaseError: If the query could not be executed after all retries.
    """
    conn = get_db_connection()
    retries = 0
    
    while retries <= max_retries:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Note: commit parameter is ignored since we're using autocommit mode (isolation_level=None)
            # This is intentional for Docker compatibility
            
            if query.strip().upper().startswith("SELECT"):
                return [dict(row) for row in cursor.fetchall()]
            return []
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and retries < max_retries:
                retries += 1
                LOGGER.warning(f"Database locked, retrying ({retries}/{max_retries}) in {retry_delay}s: {e}")
                time.sleep(retry_delay)
                # Increase delay with each retry
                retry_delay *= 1.5
            else:
                LOGGER.error(f"Database query error after {retries} retries: {e}")
                raise DatabaseError(f"Database query error: {e}")
        except Exception as e:
            LOGGER.error(f"Database query error: {e}")
            raise DatabaseError(f"Database query error: {e}")


def setup_db() -> None:
    """Set up the database schema."""
    LOGGER.info("Setting up database schema")
    
    # Create series table
    execute_query("""
    CREATE TABLE IF NOT EXISTS series (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        author TEXT,
        publisher TEXT,
        cover_url TEXT,
        status TEXT,
        content_type TEXT DEFAULT 'MANGA',
        metadata_source TEXT,
        metadata_id TEXT,
        custom_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """, commit=True)
    
    # Add content_type column to series table if it doesn't exist
    try:
        # Check existing columns
        column_check = execute_query("PRAGMA table_info(series)")
        column_names = [col['name'] for col in column_check]

        # Add content_type if missing
        if 'content_type' not in column_names:
            try:
                execute_query("ALTER TABLE series ADD COLUMN content_type TEXT DEFAULT 'MANGA'", commit=True)
                LOGGER.info("Added content_type column to series table")
            except Exception as add_err:
                # If another process already added it or SQLite reports duplicate, ignore
                if 'duplicate column name' in str(add_err).lower():
                    LOGGER.info("content_type column already exists; skipping add")
                else:
                    raise

        # Add custom_path if missing
        if 'custom_path' not in column_names:
            try:
                execute_query("ALTER TABLE series ADD COLUMN custom_path TEXT", commit=True)
                LOGGER.info("Added custom_path column to series table")
            except Exception as add_err:
                if 'duplicate column name' in str(add_err).lower():
                    LOGGER.info("custom_path column already exists; skipping add")
                else:
                    raise
    except Exception as e:
        LOGGER.error(f"Error checking/adding columns to series table: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
    
    # Create volumes table
    execute_query("""
    CREATE TABLE IF NOT EXISTS volumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER NOT NULL,
        volume_number TEXT NOT NULL,
        title TEXT,
        description TEXT,
        cover_url TEXT,
        release_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE
    )
    """, commit=True)
    
    # Create chapters table
    execute_query("""
    CREATE TABLE IF NOT EXISTS chapters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER NOT NULL,
        volume_id INTEGER,
        chapter_number TEXT NOT NULL,
        title TEXT,
        description TEXT,
        release_date TEXT,
        status TEXT,
        read_status TEXT DEFAULT 'UNREAD',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE,
        FOREIGN KEY (volume_id) REFERENCES volumes (id) ON DELETE SET NULL
    )
    """, commit=True)
    
    # Enable foreign key support
    execute_query("PRAGMA foreign_keys = ON;")

    # Create calendar_events table
    execute_query("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER REFERENCES series(id) ON DELETE CASCADE,
        volume_id INTEGER REFERENCES volumes(id) ON DELETE CASCADE,
        chapter_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        event_date TEXT NOT NULL,
        event_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE,
        FOREIGN KEY (volume_id) REFERENCES volumes (id) ON DELETE CASCADE,
        FOREIGN KEY (chapter_id) REFERENCES chapters (id) ON DELETE CASCADE
    )
    """, commit=True)
    
    # Create settings table
    execute_query("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """, commit=True)
    
    # Create metadata_cache table
    execute_query("""
    CREATE TABLE IF NOT EXISTS metadata_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        source_id TEXT NOT NULL,
        data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(source, source_id)
    )
    """, commit=True)
    
    # Create ebook_files table
    execute_query("""
    CREATE TABLE IF NOT EXISTS ebook_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER NOT NULL,
        volume_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_size INTEGER,
        file_type TEXT,
        original_name TEXT,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE,
        FOREIGN KEY (volume_id) REFERENCES volumes (id) ON DELETE CASCADE
    )
    """, commit=True)
    
    # Create authors table
    execute_query("""
    CREATE TABLE IF NOT EXISTS authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        biography TEXT,
        birth_date TEXT,
        death_date TEXT,
        provider TEXT,
        provider_id TEXT,
        folder_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """, commit=True)
    
    # Create author_books table
    execute_query("""
    CREATE TABLE IF NOT EXISTS author_books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_id INTEGER NOT NULL,
        series_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (author_id) REFERENCES authors (id) ON DELETE CASCADE,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE
    )
    """, commit=True)
    
    # Import here to avoid circular imports
    from backend.features.collection import setup_collection_tables
    from backend.features.notifications import setup_notifications_tables
    
    # Set up collection tracking tables
    setup_collection_tables()
    
    # Set up notifications tables
    setup_notifications_tables()
    
    LOGGER.info("Database schema setup complete")
