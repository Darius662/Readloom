#!/usr/bin/env python3
"""
Test what volume data AniList actually provides.
"""

import sys
sys.path.insert(0, '.')

from backend.base.logging import setup_logging
from backend.features.metadata_providers.base import metadata_provider_manager
from backend.features.metadata_providers.setup import initialize_providers
from backend.internals.db import set_db_location

def test_anilist_data():
    """Test what AniList provides."""
    setup_logging("data/logs", "test_anilist.log")
    set_db_location("data/db")
    initialize_providers()
    
    anilist = metadata_provider_manager.get_provider("AniList")
    
    test_manga = [
        ("Dandadan", "132029"),
        ("One Punch Man", "85364"),
        ("Attack on Titan", "53390"),
        ("Shangri-La Frontier", "122063"),
    ]
    
    print("\n" + "="*80)
    print("TESTING ANILIST API VOLUME DATA")
    print("="*80 + "\n")
    
    for title, manga_id in test_manga:
        print(f"{title} (ID: {manga_id})")
        print("-" * 60)
        
        # Make direct GraphQL query to see raw data
        import requests
        
        query = """
        query ($id: Int) {
            Media(id: $id, type: MANGA) {
                id
                title {
                    romaji
                    english
                }
                volumes
                chapters
                status
            }
        }
        """
        
        response = requests.post(
            "https://graphql.anilist.co",
            json={"query": query, "variables": {"id": int(manga_id)}},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            media = data.get("data", {}).get("Media", {})
            
            print(f"  Title (Romaji): {media.get('title', {}).get('romaji')}")
            print(f"  Title (English): {media.get('title', {}).get('english')}")
            print(f"  Volumes from API: {media.get('volumes')}")
            print(f"  Chapters from API: {media.get('chapters')}")
            print(f"  Status: {media.get('status')}")
        else:
            print(f"  ERROR: {response.status_code}")
        
        print()
    
    print("="*80 + "\n")

if __name__ == "__main__":
    test_anilist_data()
