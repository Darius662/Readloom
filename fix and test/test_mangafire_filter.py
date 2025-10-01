#!/usr/bin/env python3
"""
Test MangaFire filter page to see if we can search there.
"""

import requests
from bs4 import BeautifulSoup

manga_title = "Blue Exorcist"

# Try filter page with keyword
filter_url = f"https://mangafire.to/filter?keyword={manga_title.replace(' ', '+')}"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"\nTrying filter page: {filter_url}\n")

response = requests.get(filter_url, headers=headers, timeout=10)
print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for manga cards (we know from earlier they use .unit class)
    units = soup.select('.unit')
    print(f"Found {len(units)} manga cards\n")
    
    if units:
        for i, unit in enumerate(units[:3], 1):
            # Find the link
            link = unit.select_one('a[href*="/manga/"]')
            if link:
                print(f"{i}. {link.get('title', 'No title')}")
                print(f"   URL: {link['href']}")
                print()
    
    # Save for inspection
    with open('mangafire_filter.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("Saved HTML to: mangafire_filter.html")
else:
    print(f"Filter page failed with status: {response.status_code}")
