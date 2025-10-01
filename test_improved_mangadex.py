#!/usr/bin/env python3
"""
Test the improved MangaDex implementation.
"""

import sys
sys.path.insert(0, '.')

from backend.base.logging import setup_logging
from backend.features.scrapers.mangainfo.mangadex import get_mangadex_data

# Set up logging
setup_logging("data/logs", "test_mangadex.log")

def test_manga(title, expected_volumes):
    """Test a manga title."""
    print(f"\nTesting: {title}")
    print("-" * 60)
    
    chapters, volumes = get_mangadex_data(title)
    
    print(f"  Chapters: {chapters}")
    print(f"  Volumes: {volumes}")
    print(f"  Expected: {expected_volumes}")
    
    if volumes == expected_volumes:
        print(f"  ✅ SUCCESS!")
    elif volumes > 0:
        print(f"  ⚠️  Got {volumes}, expected {expected_volumes}")
    else:
        print(f"  ❌ FAILED - No data")

print("\n" + "="*80)
print("TESTING IMPROVED MANGADEX API")
print("="*80)

test_manga("Dandadan", 24)
test_manga("One Punch Man", 29)
test_manga("Attack on Titan", 34)
test_manga("Shingeki no Kyojin", 34)

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
