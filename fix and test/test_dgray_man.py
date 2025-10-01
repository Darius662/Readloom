#!/usr/bin/env python3
"""
Test D.Gray-man scraping.
"""

import sys
sys.path.insert(0, '.')

from backend.features.scrapers.mangainfo.mangafire import get_mangafire_data
from backend.base.logging import setup_logging
import requests

setup_logging("data/logs", "test_dgray.log")

print("\n" + "="*80)
print("TESTING D.GRAY-MAN SCRAPING")
print("="*80 + "\n")

# Test with different title variations
titles = [
    "D.Gray-man",
    "DGray-man",
    "D Gray-man",
    "D Gray man"
]

for title in titles:
    print(f"Testing: {title}")
    session = requests.Session()
    chapters, volumes = get_mangafire_data(session, title)
    print(f"  Result: {chapters} chapters, {volumes} volumes")
    print()

print("="*80)
print("Expected: 30 volumes")
print("="*80 + "\n")
