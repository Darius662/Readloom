#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup check module to verify if initial setup has been completed.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from backend.internals.settings import Settings


def is_setup_complete() -> bool:
    """Check if the initial setup has been completed.
    
    Returns:
        bool: True if setup is complete, False otherwise.
    """
    try:
        # Check if collections table exists and has at least one collection
        try:
            collections = execute_query("SELECT COUNT(*) as count FROM collections")
            if not collections or collections[0]['count'] == 0:
                LOGGER.warning("No collections found, setup is not complete")
                return False
        except Exception as e:
            LOGGER.error(f"Error checking collections: {e}")
            return False
        
        # Check if root folders are configured
        settings = Settings().get_settings()
        root_folders = settings.root_folders
        if not root_folders:
            LOGGER.warning("No root folders configured, setup is not complete")
            return False
        
        # Check if at least one root folder exists on disk
        import os
        valid_root_folder_found = False
        for folder in root_folders:
            if os.path.exists(folder['path']) and os.path.isdir(folder['path']):
                valid_root_folder_found = True
                break
        
        if not valid_root_folder_found:
            LOGGER.warning("No valid root folders found on disk, setup is not complete")
            return False
        
        # If we get here, setup is complete
        LOGGER.info("Setup check passed, application is ready to use")
        return True
    except Exception as e:
        LOGGER.error(f"Error checking setup status: {e}")
        return False


def check_setup_on_startup() -> None:
    """Check setup status on application startup."""
    LOGGER.info("Checking setup status...")
    is_complete = is_setup_complete()
    
    if is_complete:
        LOGGER.info("Setup is complete, application is ready to use")
    else:
        LOGGER.warning("Setup is not complete, user will be directed to setup wizard")
