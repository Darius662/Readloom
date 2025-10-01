#!/usr/bin/env python3
"""
Test script to verify the volume detection fix.
Tests that the scraper is called during get_manga_details() and returns accurate volume counts.
"""

import sys
sys.path.insert(0, '.')

from backend.base.logging import setup_logging, LOGGER
from backend.features.metadata_providers.base import metadata_provider_manager
from backend.features.metadata_providers.setup import initialize_providers
from backend.internals.db import set_db_location

def test_volume_detection():
    """Test volume detection for various manga."""
    # Set up logging and database
    setup_logging("data/logs", "test_volume_fix.log")
    set_db_location("data/db")
    
    # Initialize providers
    initialize_providers()
    
    # Get the AniList provider
    anilist = metadata_provider_manager.get_provider("AniList")
    if not anilist:
        print("ERROR: Could not get AniList provider")
        return
    
    # Test cases: (AniList ID, Expected Title, Expected Volumes)
    test_cases = [
        ("85364", "One Punch Man", 29),  # Should show 29 volumes
        ("30002", "Berserk", 41),        # Should show 41 volumes
        ("30642", "Vinland Saga", 26),   # Should show 26 volumes (completed, has 29 in AniList)
    ]
    
    print("\n" + "="*80)
    print("TESTING VOLUME DETECTION FIX")
    print("="*80 + "\n")
    
    for manga_id, expected_title, expected_volumes in test_cases:
        print(f"\nTesting: {expected_title} (ID: {manga_id})")
        print("-" * 60)
        
        try:
            # Get manga details
            details = anilist.get_manga_details(manga_id)
            
            if not details:
                print(f"  ❌ ERROR: Could not get details for {expected_title}")
                continue
            
            title = details.get("title", "Unknown")
            volume_count = details.get("volume_count", 0)
            volumes_list = details.get("volumes", [])
            
            print(f"  Title: {title}")
            print(f"  Volume Count (from scraper): {volume_count}")
            print(f"  Volumes List Length: {len(volumes_list)}")
            
            # Check if the volume count matches expected
            if volume_count == expected_volumes:
                print(f"  ✅ SUCCESS: Volume count is correct ({volume_count} volumes)")
            elif volume_count > 0:
                print(f"  ⚠️  WARNING: Volume count is {volume_count}, expected {expected_volumes}")
            else:
                print(f"  ❌ FAILED: No volume count detected (expected {expected_volumes})")
            
            # Check if volumes list matches
            if len(volumes_list) == volume_count:
                print(f"  ✅ Volumes list length matches volume count")
            else:
                print(f"  ⚠️  Volumes list length ({len(volumes_list)}) doesn't match volume count ({volume_count})")
            
            # Show sample volumes
            if volumes_list:
                print(f"  Sample volumes:")
                for i, vol in enumerate(volumes_list[:3]):
                    print(f"    - Volume {vol.get('number')}: {vol.get('title')} (Release: {vol.get('release_date')})")
                if len(volumes_list) > 3:
                    print(f"    ... and {len(volumes_list) - 3} more volumes")
        
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_volume_detection()
