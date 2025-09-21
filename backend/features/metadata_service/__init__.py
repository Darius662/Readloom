#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Package initializer for metadata_service.

Re-exports all public functions from facade.
"""

from .cache import save_to_cache, get_from_cache, clear_cache
from .facade import (
    init_metadata_service,
    search_manga,
    get_manga_details,
    get_chapter_list,
    get_chapter_images,
    get_latest_releases,
    get_providers,
    update_provider,
    import_manga_to_collection,
)

__all__ = [
    # Cache functions
    "save_to_cache",
    "get_from_cache",
    "clear_cache",
    
    # Facade functions
    "init_metadata_service",
    "search_manga",
    "get_manga_details",
    "get_chapter_list",
    "get_chapter_images",
    "get_latest_releases",
    "get_providers",
    "update_provider",
    "import_manga_to_collection",
]
