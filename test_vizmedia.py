#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for the VizMedia provider.
"""

import logging
import sys
import os
import json
from datetime import datetime
from backend.features.metadata_providers.vizmedia import VizMediaProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def test_latest_releases():
    """Test the latest releases functionality of the VizMedia provider."""
    provider = VizMediaProvider(enabled=True)
    
    print("Getting latest releases...")
    results = provider.get_latest_releases()
    
    print(f"Found {len(results)} releases:")
    for i, result in enumerate(results[:5]):  # Show first 5 results
        print(f"{i+1}. {result.get('manga_title', 'Unknown')}")
        print(f"   ID: {result.get('manga_id', 'Unknown')}")
        print(f"   Cover URL: {result.get('cover_url', 'Unknown')}")
        print(f"   Release Date: {result.get('release_date', 'Unknown')}")
        print(f"   URL: {result.get('url', 'Unknown')}")
        print()
    
    # Save results to file for inspection
    with open('vizmedia_releases.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved all results to vizmedia_releases.json")

def test_calendar_specific_month():
    """Test getting releases for a specific month."""
    provider = VizMediaProvider(enabled=True)
    
    # Get current month and year
    now = datetime.now()
    year = now.year
    month = now.month
    
    print(f"Getting releases for {year}-{month:02d}...")
    results = provider.get_calendar_releases(year, month)
    
    print(f"Found {len(results)} releases:")
    for i, result in enumerate(results[:5]):  # Show first 5 results
        print(f"{i+1}. {result.get('manga_title', 'Unknown')}")
        print(f"   ID: {result.get('manga_id', 'Unknown')}")
        print(f"   Volume: {result.get('volume', 'Unknown')}")
        print(f"   Format: {result.get('format', 'Unknown')}")
        print(f"   Release Date: {result.get('release_date', 'Unknown')}")
        print()

if __name__ == "__main__":
    print("Testing VizMedia provider...")
    test_latest_releases()
    test_calendar_specific_month()
