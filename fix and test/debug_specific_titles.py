#!/usr/bin/env python3
"""
Debug script to investigate why specific titles still show incorrect volumes.
"""

import sys
sys.path.insert(0, '.')

from backend.base.logging import setup_logging, LOGGER
from backend.features.metadata_providers.base import metadata_provider_manager
from backend.features.metadata_providers.setup import initialize_providers
from backend.internals.db import set_db_location

def debug_title(title):
    """Debug volume detection for a specific title."""
    # Set up
    setup_logging("data/logs", "debug_titles.log")
    set_db_location("data/db")
    initialize_providers()
    
    # Get the AniList provider
    anilist = metadata_provider_manager.get_provider("AniList")
    if not anilist:
        print("ERROR: Could not get AniList provider")
        return
    
    print(f"\n{'='*80}")
    print(f"DEBUGGING: {title}")
    print(f"{'='*80}\n")
    
    # Search for the title
    print(f"Step 1: Searching AniList for '{title}'...")
    results = anilist.search(title)
    
    if not results:
        print("  ❌ No results found")
        return
    
    # Show top result
    top_result = results[0]
    print(f"  ✅ Found: {top_result.get('title')}")
    print(f"     ID: {top_result.get('id')}")
    print(f"     AniList API Volumes: {top_result.get('volumes', 'None')}")
    print(f"     AniList API Chapters: {top_result.get('chapters', 'None')}")
    
    manga_id = top_result.get('id')
    
    # Get detailed info
    print(f"\nStep 2: Getting manga details from AniList...")
    details = anilist.get_manga_details(manga_id)
    
    if not details:
        print("  ❌ Could not get details")
        return
    
    manga_title = details.get("title", "Unknown")
    volume_count = details.get("volume_count", 0)
    volumes_list = details.get("volumes", [])
    
    print(f"  Title: {manga_title}")
    print(f"  Volume Count (from scraper): {volume_count}")
    print(f"  Volumes List Length: {len(volumes_list)}")
    
    # Test the scraper directly
    print(f"\nStep 3: Testing scraper directly with title '{manga_title}'...")
    if anilist.info_provider:
        try:
            chapters, volumes = anilist.info_provider.get_chapter_count(manga_title)
            print(f"  Scraper returned: {chapters} chapters, {volumes} volumes")
            
            # Check if it's in the static database
            from backend.features.scrapers.mangainfo.constants import POPULAR_MANGA_DATA
            title_lower = manga_title.lower()
            
            found_in_static = False
            for known_title, data in POPULAR_MANGA_DATA.items():
                if known_title in title_lower or title_lower in known_title:
                    print(f"  ✅ Found in static database as '{known_title}':")
                    print(f"     Chapters: {data['chapters']}, Volumes: {data['volumes']}")
                    found_in_static = True
                    break
            
            if not found_in_static:
                print(f"  ⚠️  NOT in static database, will try web scraping")
                print(f"     Testing with normalized title: '{title_lower}'")
        except Exception as e:
            print(f"  ❌ Scraper error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("  ❌ Info provider not available")
    
    # Show sample volumes
    if volumes_list:
        print(f"\nStep 4: Sample volumes created:")
        for i, vol in enumerate(volumes_list[:5]):
            print(f"  - Volume {vol.get('number')}: {vol.get('title')} (Release: {vol.get('release_date')})")
        if len(volumes_list) > 5:
            print(f"  ... and {len(volumes_list) - 5} more volumes")
    else:
        print(f"\nStep 4: ❌ No volumes were created!")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    # Test the problematic titles
    debug_title("Shangri-La Frontier")
    debug_title("Attack on Titan")
    debug_title("Shingeki no Kyojin")
