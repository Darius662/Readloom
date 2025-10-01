#!/usr/bin/env python3
"""
Try to find the correct MangaFire URL for Blue Exorcist.
"""

import requests

# Try different URL variations
urls = [
    "https://mangafire.to/manga/ao-no-exorcist",
    "https://mangafire.to/manga/blue-exorcist",
    "https://mangafire.to/manga/ao-no-exorcist.1pqx2",  # Common pattern
    "https://mangafire.to/manga/blue-exorcist.1pqx2",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("\nTrying different MangaFire URLs:\n")

for url in urls:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"{url}")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ FOUND!")
            # Try to extract volume count from the page
            if 'volume' in response.text.lower():
                print(f"  Contains volume information")
        print()
    except Exception as e:
        print(f"{url}")
        print(f"  Error: {e}\n")
