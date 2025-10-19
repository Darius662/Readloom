#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Helper functions for content services.
These functions extend the existing helpers.py with content type-specific functionality.
"""

from pathlib import Path
from typing import Optional, Union

from backend.base.logging import LOGGER


def create_content_folder_structure(content_id: Union[int, str], title: str, content_type: str, 
                                   collection_id: Optional[int] = None, 
                                   root_folder_id: Optional[int] = None,
                                   author: Optional[str] = None) -> str:
    """Create the appropriate folder structure based on content type.
    
    Args:
        content_id: The content ID.
        title: The content title.
        content_type: The content type.
        collection_id: The collection ID (optional).
        root_folder_id: The root folder ID (optional).
        author: The author name (optional, used for books).
        
    Returns:
        The path to the created folder.
    """
    try:
        from backend.features.content_service_factory import get_content_service
        
        # Get the appropriate service for this content type
        service = get_content_service(content_type)
        
        # Use the service to create the folder structure
        folder_path = service.create_folder_structure(
            content_id, 
            title, 
            content_type, 
            collection_id, 
            root_folder_id,
            author
        )
        
        return folder_path
    except Exception as e:
        LOGGER.error(f"Error creating content folder structure: {e}")
        
        # Fall back to the original function if there's an error
        from backend.base.helpers import create_series_folder_structure
        return create_series_folder_structure(content_id, title, content_type, collection_id, root_folder_id)


def get_root_folder_path(content_type: str, collection_id: Optional[int] = None, 
                         root_folder_id: Optional[int] = None) -> Optional[str]:
    """Get the appropriate root folder path for the given content type.
    
    Args:
        content_type: The content type.
        collection_id: The collection ID (optional).
        root_folder_id: The root folder ID (optional).
        
    Returns:
        The root folder path, or None if not found.
    """
    from backend.internals.db import execute_query
    
    try:
        # If an explicit root_folder_id is provided, use it directly
        if root_folder_id is not None:
            LOGGER.info(f"Using explicit root_folder_id={root_folder_id}")
            query = "SELECT path FROM root_folders WHERE id = ?"
            root_folders = execute_query(query, (root_folder_id,))
            if root_folders:
                return root_folders[0]["path"]
        
        # If collection_id is provided, get root folders for that collection
        if collection_id is not None:
            LOGGER.info(f"Getting root folders for collection ID: {collection_id}")
            query = """
            SELECT rf.path FROM root_folders rf
            JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
            WHERE crf.collection_id = ?
            ORDER BY rf.name ASC
            """
            root_folders = execute_query(query, (collection_id,))
            if root_folders:
                return root_folders[0]["path"]
        
        # Try to get the default collection for this content_type
        default_collections = execute_query(
            "SELECT id FROM collections WHERE is_default = 1 AND UPPER(content_type) = UPPER(?)", 
            (content_type,)
        )
        if default_collections:
            default_collection_id = default_collections[0]["id"]
            query = """
            SELECT rf.path FROM root_folders rf
            JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
            WHERE crf.collection_id = ?
            ORDER BY rf.name ASC
            """
            root_folders = execute_query(query, (default_collection_id,))
            if root_folders:
                return root_folders[0]["path"]
        
        # If still no root folders, use the first root folder from the database
        root_folders = execute_query("SELECT path FROM root_folders ORDER BY name ASC LIMIT 1")
        if root_folders:
            return root_folders[0]["path"]
        
        # If still no root folders, use default ebook storage
        from backend.base.helpers import get_ebook_storage_dir
        return str(get_ebook_storage_dir())
    
    except Exception as e:
        LOGGER.error(f"Error getting root folder path: {e}")
        
        # Fall back to the default ebook storage
        from backend.base.helpers import get_ebook_storage_dir
        return str(get_ebook_storage_dir())
