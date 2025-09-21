#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collection module for MangaArr - compatibility shim.

This module re-exports all public functions from the collection package.
The implementation has been moved to backend.features.collection.
"""

from backend.features.collection import (
    # Schema
    setup_collection_tables,
    
    # Stats
    get_collection_stats,
    update_collection_stats,
    
    # Queries
    get_collection_items,
    export_collection,
    
    # Mutations
    add_to_collection,
    remove_from_collection,
    update_collection_item,
    import_collection,
)

# Re-export all public functions
__all__ = [
    "setup_collection_tables",
    "get_collection_stats",
    "update_collection_stats",
    "get_collection_items",
    "export_collection",
    "add_to_collection",
    "remove_from_collection",
    "update_collection_item",
    "import_collection",
]
