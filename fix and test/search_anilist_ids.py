#!/usr/bin/env python3
"""
Search for correct AniList IDs for test manga.
"""

import sys
sys.path.insert(0, '.')

from backend.base.logging import setup_logging
from backend.features.metadata_providers.base import metadata_provider_manager
from backend.features.metadata_providers.setup import initialize_providers
from backend.internals.db import set_db_location

def search_manga(title):
    """Search for manga by title."""
    # Set up
    setup_logging("data/logs", "search_ids.log")
    set_db_location("data/db")
    initialize_providers()
    
    # Get the AniList provider
    anilist = metadata_provider_manager.get_provider("AniList")
    if not anilist:
        print("ERROR: Could not get AniList provider")
        return
    
    print(f"\nSearching for: {title}")
    print("-" * 60)
    
    results = anilist.search(title)
    
    if not results:
        print("No results found")
        return
    
    for i, result in enumerate(results[:5], 1):
        print(f"\n{i}. {result.get('title')}")
        print(f"   ID: {result.get('id')}")
        print(f"   Volumes: {result.get('volumes', 0)}")
        print(f"   Chapters: {result.get('chapters', 0)}")
        print(f"   Status: {result.get('status', 'Unknown')}")

if __name__ == "__main__":
    search_manga("One Punch Man")
    search_manga("Berserk")
    search_manga("Vinland Saga")
