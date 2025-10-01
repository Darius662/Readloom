#!/usr/bin/env python3
"""
Test script for the new smart caching system.
"""

import sys
sys.path.insert(0, '.')

from backend.base.logging import setup_logging, LOGGER
from backend.internals.db import set_db_location, execute_query
from backend.internals.migrations import run_migrations
from backend.features.metadata_providers.base import metadata_provider_manager
from backend.features.metadata_providers.setup import initialize_providers

def test_smart_caching():
    """Test the smart caching system."""
    # Set up
    setup_logging("data/logs", "test_smart_caching.log")
    set_db_location("data/db")
    
    print("\n" + "="*80)
    print("TESTING SMART CACHING SYSTEM")
    print("="*80 + "\n")
    
    # Run migrations to create the cache table
    print("Step 1: Running database migrations...")
    try:
        run_migrations()
        print("  ✓ Migrations complete\n")
    except Exception as e:
        print(f"  ✗ Migration error: {e}\n")
        return
    
    # Initialize providers
    print("Step 2: Initializing providers...")
    initialize_providers()
    print("  ✓ Providers initialized\n")
    
    # Get AniList provider
    anilist = metadata_provider_manager.get_provider("AniList")
    if not anilist:
        print("  ✗ ERROR: Could not get AniList provider")
        return
    
    # Test cases
    test_cases = [
        ("Dandadan", "132029"),
        ("One Punch Man", "85364"),
        ("Attack on Titan", "53390"),
    ]
    
    for manga_name, manga_id in test_cases:
        print(f"Step 3: Testing {manga_name}...")
        print("-" * 60)
        
        # First call - should scrape and cache
        print(f"  First call (should scrape and cache)...")
        details = anilist.get_manga_details(manga_id)
        
        if not details:
            print(f"  ✗ Could not get details")
            continue
        
        volume_count = details.get("volume_count", 0)
        print(f"  Volume count: {volume_count}")
        
        # Check if it was cached
        normalized_title = anilist.info_provider.normalize_title(details.get("title", ""))
        cache_entry = execute_query(
            "SELECT * FROM manga_volume_cache WHERE manga_title_normalized = ?",
            (normalized_title,)
        )
        
        if cache_entry:
            entry = cache_entry[0]
            print(f"  ✓ Cached in database:")
            print(f"    - Title: {entry['manga_title']}")
            print(f"    - Chapters: {entry['chapter_count']}")
            print(f"    - Volumes: {entry['volume_count']}")
            print(f"    - Source: {entry['source']}")
            print(f"    - Cached at: {entry['cached_at']}")
        else:
            print(f"  ✗ Not found in cache")
        
        print()
    
    # Show cache statistics
    print("="*80)
    print("CACHE STATISTICS")
    print("="*80 + "\n")
    
    total_cached = execute_query("SELECT COUNT(*) as count FROM manga_volume_cache")[0]['count']
    print(f"Total cached entries: {total_cached}")
    
    # Show all cached entries
    all_cached = execute_query(
        "SELECT manga_title, volume_count, source, refreshed_at FROM manga_volume_cache ORDER BY refreshed_at DESC"
    )
    
    if all_cached:
        print("\nCached manga:")
        for entry in all_cached:
            print(f"  - {entry['manga_title']}: {entry['volume_count']} volumes (source: {entry['source']}, refreshed: {entry['refreshed_at']})")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
    
    print("Next steps:")
    print("1. Import a manga from AniList - it should use the cache")
    print("2. Wait 30+ days and import again - it should refresh the cache")
    print("3. Use force_refresh=True to bypass cache and scrape fresh data")

if __name__ == "__main__":
    test_smart_caching()
