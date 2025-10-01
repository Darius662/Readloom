#!/usr/bin/env python3
"""
Debug MangaDex search for Blue Exorcist to see what it's finding.
"""

import requests
import json

manga_title = "Ao no Exorcist"
search_url = f"https://api.mangadex.org/manga?title={manga_title.replace(' ', '+')}&limit=5&includes[]=cover_art"

print(f"\nSearching MangaDex for: {manga_title}")
print(f"URL: {search_url}\n")

response = requests.get(search_url, timeout=10)
data = response.json()

if data.get('data'):
    print(f"Found {len(data['data'])} results:\n")
    
    for i, manga in enumerate(data['data'], 1):
        attributes = manga.get('attributes', {})
        titles = attributes.get('title', {})
        
        print(f"{i}. {titles.get('en', titles.get('ja-ro', 'Unknown'))}")
        print(f"   ID: {manga['id']}")
        print(f"   Last Volume: {attributes.get('lastVolume', 'N/A')}")
        print(f"   Last Chapter: {attributes.get('lastChapter', 'N/A')}")
        print(f"   Status: {attributes.get('status', 'N/A')}")
        print(f"   Publication Demographic: {attributes.get('publicationDemographic', 'N/A')}")
        print(f"   Content Rating: {attributes.get('contentRating', 'N/A')}")
        print()
else:
    print("No results found")
