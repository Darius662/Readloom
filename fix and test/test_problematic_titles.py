#!/usr/bin/env python3
"""
Test the problematic titles that were showing incorrect volume counts.
"""

import sys
sys.path.insert(0, '.')

from backend.base.logging import setup_logging
from backend.features.metadata_providers.base import metadata_provider_manager
from backend.features.metadata_providers.setup import initialize_providers
from backend.internals.db import set_db_location

def test_titles():
    """Test problematic titles."""
    # Set up
    setup_logging("data/logs", "test_problematic.log")
    set_db_location("data/db")
    initialize_providers()
    
    # Get the AniList provider
    anilist = metadata_provider_manager.get_provider("AniList")
    if not anilist:
        print("ERROR: Could not get AniList provider")
        return
    
    # Test cases: (Search Term, Expected Volumes)
    test_cases = [
        ("Shangri-La Frontier", 17),
        ("Attack on Titan", 34),
        ("Shingeki no Kyojin", 34),
    ]
    
    print("\n" + "="*80)
    print("TESTING PROBLEMATIC TITLES")
    print("="*80 + "\n")
    
    for search_term, expected_volumes in test_cases:
        print(f"Testing: {search_term}")
        print("-" * 60)
        
        try:
            # Search for the title
            results = anilist.search(search_term)
            
            if not results:
                print(f"  [FAILED] No results found")
                continue
            
            # Get first result
            manga_id = results[0].get('id')
            manga_title = results[0].get('title')
            
            print(f"  Found: {manga_title} (ID: {manga_id})")
            
            # Get details
            details = anilist.get_manga_details(manga_id)
            
            if not details:
                print(f"  [FAILED] Could not get details")
                continue
            
            volume_count = details.get("volume_count", 0)
            volumes_list = details.get("volumes", [])
            
            print(f"  Volume Count: {volume_count}")
            print(f"  Volumes List Length: {len(volumes_list)}")
            
            # Check result
            if volume_count == expected_volumes:
                print(f"  [SUCCESS] Correct volume count!")
            elif volume_count > 0:
                print(f"  [WARNING] Got {volume_count} volumes, expected {expected_volumes}")
            else:
                print(f"  [FAILED] No volumes detected")
            
            print()
        
        except Exception as e:
            print(f"  [ERROR] {e}")
            print()
    
    print("="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_titles()
