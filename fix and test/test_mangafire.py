#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for the MangaFire provider.
"""

import logging
import sys
from backend.features.metadata_providers.mangafire import MangaFireProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def test_search():
    """Test the search functionality of the MangaFire provider."""
    provider = MangaFireProvider(enabled=True)
    query = "Naruto"
    
    print(f"Searching for '{query}'...")
    results = provider.search(query)
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results):
        print(f"{i+1}. {result.get('title', 'Unknown')} by {result.get('author', 'Unknown')}")
        print(f"   ID: {result.get('id', 'Unknown')}")
        print(f"   Cover URL: {result.get('cover_url', 'Unknown')}")
        print(f"   Status: {result.get('status', 'Unknown')}")
        print(f"   Latest Chapter: {result.get('latest_chapter', 'Unknown')}")
        print(f"   URL: {result.get('url', 'Unknown')}")
        print()

if __name__ == "__main__":
    test_search()
