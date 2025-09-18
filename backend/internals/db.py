#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.base.custom_exceptions import DatabaseError
from backend.base.definitions import Constants
from backend.base.helpers import ensure_dir_exists, get_data_dir
from backend.base.logging import LOGGER

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


def get_db_connection() -> sqlite3.Connection:
    """Get a connection to the database.

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
        DB_CONN = sqlite3.connect(DB_PATH, check_same_thread=False)
        DB_CONN.row_factory = sqlite3.Row
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


def execute_query(query: str, params: Tuple = (), commit: bool = False) -> List[Dict[str, Any]]:
    """Execute a SQL query.

    Args:
        query (str): The SQL query to execute.
        params (Tuple, optional): The parameters for the query. Defaults to ().
        commit (bool, optional): Whether to commit the transaction. Defaults to False.

    Returns:
        List[Dict[str, Any]]: The results of the query.

    Raises:
        DatabaseError: If the query could not be executed.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if commit:
            conn.commit()
        
        if query.strip().upper().startswith("SELECT"):
            return [dict(row) for row in cursor.fetchall()]
        return []
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
        metadata_source TEXT,
        metadata_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """, commit=True)
    
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
    
    # Create calendar_events table
    execute_query("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER,
        volume_id INTEGER,
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
    
    LOGGER.info("Database schema setup complete")
