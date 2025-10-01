#!/usr/bin/env python3
"""
Test Blue Exorcist scraping to see why it's failing.
"""

import sys
sys.path.insert(0, '.')

from backend.features.scrapers.mangainfo.mangadex import get_mangadex_data
from backend.features.scrapers.mangainfo.mangafire import get_mangafire_data
from backend.base.logging import setup_logging
import requests

setup_logging("data/logs", "test_blue_exorcist.log")

print("\n" + "="*80)
print("TESTING BLUE EXORCIST SCRAPING")
print("="*80 + "\n")

# Test with different title variations
titles = [
    "Ao no Exorcist",
    "Blue Exorcist",
    "ao no exorcist"
]

for title in titles:
    print(f"\nTesting: {title}")
    print("-" * 60)
    
    # Test MangaDex
    print("  MangaDex:")
    chapters, volumes = get_mangadex_data(title)
    print(f"    Chapters: {chapters}, Volumes: {volumes}")
    
    # Test MangaFire
    print("  MangaFire:")
    session = requests.Session()
    chapters, volumes = get_mangafire_data(session, title)
    print(f"    Chapters: {chapters}, Volumes: {volumes}")

print("\n" + "="*80)
print("Expected: 32 volumes")
print("="*80 + "\n")
