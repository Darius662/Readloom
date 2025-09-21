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
]
