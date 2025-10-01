#!/usr/bin/env python3
"""
Test MangaDex API to understand the response structure.
"""

import requests
import json

def test_mangadex(manga_title):
    """Test MangaDex API for a specific manga."""
    print(f"\n{'='*80}")
    print(f"Testing MangaDex API for: {manga_title}")
    print(f"{'='*80}\n")
    
    # Step 1: Search for manga
    search_url = f"https://api.mangadex.org/manga?title={manga_title.replace(' ', '+')}&limit=1"
    print(f"Step 1: Searching...")
    print(f"URL: {search_url}\n")
    
    try:
        response = requests.get(search_url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"ERROR: Failed to search")
            return
        
        data = response.json()
        
        if not data.get('data') or len(data['data']) == 0:
            print(f"ERROR: No results found")
            return
        
        manga = data['data'][0]
        manga_id = manga['id']
        manga_title_found = manga['attributes']['title'].get('en', 'Unknown')
        
        print(f"Found: {manga_title_found}")
        print(f"ID: {manga_id}")
        
        # Check if lastVolume and lastChapter are in attributes
        last_volume = manga['attributes'].get('lastVolume')
        last_chapter = manga['attributes'].get('lastChapter')
        print(f"Last Volume (from attributes): {last_volume}")
        print(f"Last Chapter (from attributes): {last_chapter}")
        
        # Step 2: Get aggregate data
        print(f"\nStep 2: Getting aggregate data...")
        agg_url = f"https://api.mangadex.org/manga/{manga_id}/aggregate?translatedLanguage[]=en"
        print(f"URL: {agg_url}\n")
        
        agg_response = requests.get(agg_url, timeout=10)
        print(f"Status: {agg_response.status_code}")
        
        if agg_response.status_code != 200:
            print(f"ERROR: Failed to get aggregate")
            return
        
        agg_data = agg_response.json()
        
        # Show structure
        print(f"\nAggregate data structure:")
        print(f"  Keys: {list(agg_data.keys())}")
        
        volumes_data = agg_data.get('volumes', {})
        print(f"  Volumes type: {type(volumes_data)}")
        print(f"  Number of volumes: {len(volumes_data)}")
        
        # Show first few volumes
        if isinstance(volumes_data, dict):
            print(f"\n  Sample volumes (first 3):")
            for i, (vol_id, vol_data) in enumerate(list(volumes_data.items())[:3]):
                chapters = vol_data.get('chapters', {})
                print(f"    Volume {vol_id}: {len(chapters)} chapters")
                # Show first chapter
                if chapters:
                    first_chapter = list(chapters.values())[0]
                    print(f"      Sample chapter: {first_chapter.get('chapter', 'N/A')}")
        
        # Count total
        volume_count = len(volumes_data)
        chapter_count = 0
        
        if isinstance(volumes_data, dict):
            for vol_id, vol_data in volumes_data.items():
                chapter_count += len(vol_data.get('chapters', {}))
        
        print(f"\n{'='*80}")
        print(f"RESULTS:")
        print(f"  Total Volumes: {volume_count}")
        print(f"  Total Chapters: {chapter_count}")
        print(f"  Last Volume (API): {last_volume}")
        print(f"  Last Chapter (API): {last_chapter}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test the problematic manga
    test_mangadex("Dandadan")
    test_mangadex("One Punch Man")
    test_mangadex("Attack on Titan")
