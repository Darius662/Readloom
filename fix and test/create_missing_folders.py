#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Set up the environment
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Set database location
from backend.internals.db import set_db_location, execute_query
set_db_location("data/db")

# Set up logging
from backend.base.logging import setup_logging, LOGGER
setup_logging("data/logs", "readloom.log")
LOGGER.info("Starting folder creation script")

# Import necessary functions
from backend.base.helpers import create_series_folder_structure, get_safe_folder_name

# Get all series from the database
try:
    series_list = execute_query("SELECT id, title, content_type FROM series")
    LOGGER.info(f"Found {len(series_list)} series in the database")
    
    # Create folders for each series
    for series in series_list:
        series_id = series['id']
        series_title = series['title']
        content_type = series.get('content_type', 'MANGA')
        
        LOGGER.info(f"Creating folder for series: {series_title} (ID: {series_id}, Type: {content_type})")
        
        # Create the folder structure
        series_path = create_series_folder_structure(series_id, series_title, content_type)
        LOGGER.info(f"Folder structure created at: {series_path}")
    
    LOGGER.info("All folders created successfully")
    
except Exception as e:
    LOGGER.error(f"Error: {e}")
    import traceback
    LOGGER.error(traceback.format_exc())

LOGGER.info("Folder creation script completed")
