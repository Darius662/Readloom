#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Metadata service for Readloom - compatibility shim.

This module re-exports all public functions from the metadata_service package.
The implementation has been moved to backend.features.metadata_service.
"""

from backend.features.metadata_service import (
    init_metadata_service,
    search_manga,
    get_manga_details,
    get_chapter_list,
    get_chapter_images,
    get_latest_releases,
    get_providers,
    update_provider,
    import_manga_to_collection,
    save_to_cache,
    get_from_cache,
    clear_cache,
)

# Re-export all public functions
__all__ = [
    "init_metadata_service",
    "search_manga",
    "get_manga_details",
    "get_chapter_list",
    "get_chapter_images",
    "get_latest_releases",
    "get_providers",
    "update_provider",
    "import_manga_to_collection",
    "save_to_cache",
    "get_from_cache",
    "clear_cache",
]
