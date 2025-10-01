#!/usr/bin/env python3
"""
Debug Dandadan volume detection to see what's happening.
"""

import sys
sys.path.insert(0, '.')

from backend.base.logging import setup_logging, LOGGER
from backend.features.metadata_providers.base import metadata_provider_manager
from backend.features.metadata_providers.setup import initialize_providers
from backend.internals.db import set_db_location
from backend.features.scrapers.mangainfo.provider import MangaInfoProvider

def debug_dandadan():
    """Debug Dandadan volume detection."""
    # Set up
    setup_logging("data/logs", "debug_dandadan.log")
    set_db_location("data/db")
    initialize_providers()
    
    print("\n" + "="*80)
    print("DEBUGGING DANDADAN")
    print("="*80 + "\n")
    
    # Test the scraper directly
    print("Step 1: Testing scraper directly with 'Dandadan'...")
    provider = MangaInfoProvider()
    chapters, volumes = provider.get_chapter_count("Dandadan")
    print(f"  Scraper returned: {chapters} chapters, {volumes} volumes")
    print()
    
    # Test with AniList
    print("Step 2: Testing through AniList provider...")
    anilist = metadata_provider_manager.get_provider("AniList")
    if not anilist:
        print("  ERROR: Could not get AniList provider")
        return
    
    # Search for Dandadan
    results = anilist.search("Dandadan")
    if not results:
        print("  ERROR: No results found")
        return
    
    manga_id = results[0].get('id')
    manga_title = results[0].get('title')
    print(f"  Found: {manga_title} (ID: {manga_id})")
    
    # Get details
    details = anilist.get_manga_details(manga_id)
    if not details:
        print("  ERROR: Could not get details")
        return
    
    volume_count = details.get("volume_count", 0)
    volumes_list = details.get("volumes", [])
    
    print(f"  Volume Count from AniList: {volume_count}")
    print(f"  Volumes List Length: {len(volumes_list)}")
    print()
    
    # Check what AniList API says
    print("Step 3: Checking AniList API data...")
    print(f"  AniList API Chapters: {results[0].get('chapters', 'None')}")
    print(f"  AniList API Volumes: {results[0].get('volumes', 'None')}")
    print()
    
    print("="*80)
    print("EXPECTED: 211 chapters, 24 volumes")
    print(f"GOT:      {chapters} chapters, {volumes} volumes")
    print("="*80 + "\n")

if __name__ == "__main__":
    debug_dandadan()
