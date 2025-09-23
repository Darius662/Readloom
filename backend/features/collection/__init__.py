#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Collection package for MangaArr.

Provides functions for managing manga collection tracking.
"""

from .schema import setup_collection_tables
from .stats import get_collection_stats, update_collection_stats
from .queries import get_collection_items, export_collection
from .mutations import (
    add_to_collection,
    remove_from_collection,
    update_collection_item,
    import_collection,
)
from .collections import (
    create_collection,
    get_collections,
    get_collection_by_id,
    update_collection,
    delete_collection,
    add_root_folder_to_collection,
    remove_root_folder_from_collection,
    get_collection_root_folders,
    create_root_folder,
    get_root_folders,
    get_root_folder_by_id,
    update_root_folder,
    delete_root_folder,
    add_series_to_collection,
    remove_series_from_collection,
    get_collection_series,
    get_default_collection,
)

__all__ = [
    # Schema
    "setup_collection_tables",
    
    # Stats
    "get_collection_stats",
    "update_collection_stats",
    
    # Queries
    "get_collection_items",
    "export_collection",
    
    # Mutations
    "add_to_collection",
    "remove_from_collection",
    "update_collection_item",
    "import_collection",
    
    # Collections Management
    "create_collection",
    "get_collections",
    "get_collection_by_id",
    "update_collection",
    "delete_collection",
    
    # Root Folder Management
    "add_root_folder_to_collection",
    "remove_root_folder_from_collection",
    "get_collection_root_folders",
    "create_root_folder",
    "get_root_folders",
    "get_root_folder_by_id",
    "update_root_folder",
    "delete_root_folder",
    
    # Series-Collection Management
    "add_series_to_collection",
    "remove_series_from_collection",
    "get_collection_series",
    
    # Default Collection
    "get_default_collection",
]
