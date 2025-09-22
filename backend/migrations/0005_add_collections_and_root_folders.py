#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration script to add collections and root folders tables and migrate existing settings.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from backend.internals.settings import Settings
from backend.features.collection.collections_schema import setup_collections_tables
from backend.features.collection import create_collection, create_root_folder, add_root_folder_to_collection


def migrate():
    """Migrate the database to add collections and root folders."""
    LOGGER.info("Starting migration to add collections and root folders")
    
    # Set up the new tables
    setup_collections_tables()
    LOGGER.info("Collections tables created")
    
    # Check if default collection exists
    default_collections = execute_query("SELECT id FROM collections WHERE is_default = 1")
    if not default_collections:
        # Create default collection
        collection_id = create_collection("Default Collection", "Default collection created by the system", True)
        LOGGER.info(f"Created default collection with ID {collection_id}")
    else:
        collection_id = default_collections[0]["id"]
        LOGGER.info(f"Default collection already exists with ID {collection_id}")
    
    # Migrate existing root folders from settings
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    if root_folders:
        LOGGER.info(f"Found {len(root_folders)} root folders in settings")
        
        for folder in root_folders:
            # Check if root folder already exists in the database
            existing = execute_query("SELECT id FROM root_folders WHERE path = ?", (folder["path"],))
            
            if existing:
                root_folder_id = existing[0]["id"]
                LOGGER.info(f"Root folder already exists with ID {root_folder_id}: {folder['name']} ({folder['path']})")
            else:
                # Create root folder
                root_folder_id = create_root_folder(folder["path"], folder["name"], folder.get("content_type", "MANGA"))
                LOGGER.info(f"Created root folder with ID {root_folder_id}: {folder['name']} ({folder['path']})")
            
            # Add root folder to default collection if not already added
            relationship = execute_query(
                "SELECT id FROM collection_root_folders WHERE collection_id = ? AND root_folder_id = ?",
                (collection_id, root_folder_id)
            )
            
            if not relationship:
                add_root_folder_to_collection(collection_id, root_folder_id)
                LOGGER.info(f"Added root folder {root_folder_id} to default collection {collection_id}")
            else:
                LOGGER.info(f"Root folder {root_folder_id} already in default collection {collection_id}")
    else:
        LOGGER.info("No root folders found in settings")
        
        # Create default root folder using ebook_storage setting
        ebook_storage = settings.ebook_storage
        
        # Check if root folder already exists in the database
        existing = execute_query("SELECT id FROM root_folders WHERE path = ?", (ebook_storage,))
        
        if existing:
            root_folder_id = existing[0]["id"]
            LOGGER.info(f"Default root folder already exists with ID {root_folder_id}: Default ({ebook_storage})")
        else:
            # Create root folder
            root_folder_id = create_root_folder(ebook_storage, "Default", "MANGA")
            LOGGER.info(f"Created default root folder with ID {root_folder_id}: Default ({ebook_storage})")
        
        # Add root folder to default collection if not already added
        relationship = execute_query(
            "SELECT id FROM collection_root_folders WHERE collection_id = ? AND root_folder_id = ?",
            (collection_id, root_folder_id)
        )
        
        if not relationship:
            add_root_folder_to_collection(collection_id, root_folder_id)
            LOGGER.info(f"Added default root folder {root_folder_id} to default collection {collection_id}")
        else:
            LOGGER.info(f"Default root folder {root_folder_id} already in default collection {collection_id}")
    
    # Add existing series to the default collection
    series = execute_query("SELECT id FROM series")
    
    for series_row in series:
        series_id = series_row["id"]
        
        # Check if series is already in a collection
        relationship = execute_query(
            "SELECT id FROM series_collections WHERE series_id = ?",
            (series_id,)
        )
        
        if not relationship:
            # Add series to default collection
            execute_query(
                "INSERT INTO series_collections (series_id, collection_id) VALUES (?, ?)",
                (series_id, collection_id),
                commit=True
            )
            LOGGER.info(f"Added series {series_id} to default collection {collection_id}")
        else:
            LOGGER.info(f"Series {series_id} already in a collection")
    
    LOGGER.info("Migration completed successfully")


if __name__ == "__main__":
    migrate()
