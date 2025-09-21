#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Set up the environment
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Set database location
from backend.internals.db import set_db_location, setup_db
set_db_location("data/db")

# Set up logging
from backend.base.logging import setup_logging, LOGGER
setup_logging("data/logs", "mangarr.log")
LOGGER.info("Starting test script")

# Import necessary functions
from backend.base.helpers import create_series_folder_structure, get_safe_folder_name
from backend.features.ebook_files import scan_for_ebooks
from backend.internals.db import execute_query

# Create a test series in the database
series_title = "Test Manga 2"
content_type = "MANGA"

# Check if the series already exists
existing_series = execute_query("SELECT id FROM series WHERE title = ?", (series_title,))

if existing_series:
    series_id = existing_series[0]['id']
    LOGGER.info(f"Using existing series with ID: {series_id}")
else:
    # Insert the series into the database
    series_id = execute_query("""
    INSERT INTO series (title, content_type)
    VALUES (?, ?)
    """, (series_title, content_type), commit=True)
    LOGGER.info(f"Created new series with ID: {series_id}")

# Create a volume in the database
volume_number = "1"

# Check if the volume already exists
existing_volume = execute_query("""
    SELECT id FROM volumes 
    WHERE series_id = ? AND volume_number = ?
""", (series_id, volume_number))

if existing_volume:
    volume_id = existing_volume[0]['id']
    LOGGER.info(f"Using existing volume with ID: {volume_id}")
else:
    # Insert the volume into the database
    volume_id = execute_query("""
    INSERT INTO volumes (series_id, volume_number, title)
    VALUES (?, ?, ?)
    """, (series_id, volume_number, f"Volume {volume_number}"), commit=True)
    LOGGER.info(f"Created new volume with ID: {volume_id}")

# Create the folder structure
try:
    LOGGER.info(f"Creating folder structure for {series_title}")
    series_path = create_series_folder_structure(series_id, series_title, content_type)
    LOGGER.info(f"Folder structure created at: {series_path}")
    
    # Create a test volume file
    volume_file = series_path / f"Volume_{volume_number}.pdf"
    with open(volume_file, 'w') as f:
        f.write("Test content")
    LOGGER.info(f"Created test volume file: {volume_file}")
    
    # Scan for e-books
    LOGGER.info("Scanning for e-books")
    stats = scan_for_ebooks(specific_series_id=series_id)
    LOGGER.info(f"Scan stats: {stats}")
    
except Exception as e:
    LOGGER.error(f"Error: {e}")
    import traceback
    LOGGER.error(traceback.format_exc())

LOGGER.info("Test script completed")
