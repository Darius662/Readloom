#!/usr/bin/env python3
"""
Test MangaFire search to see what HTML structure it returns.
"""

import requests
from bs4 import BeautifulSoup

manga_title = "Ao no Exorcist"
search_url = f"https://mangafire.to/search?q={manga_title.replace(' ', '+')}"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"\nSearching MangaFire: {search_url}\n")

response = requests.get(search_url, headers=headers, timeout=10)
print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try different selectors
    selectors = [
        '.manga-card',
        '.mangas-card',
        '.unit',
        '[class*="card"]',
        'a[href*="/manga/"]'
    ]
    
    print("Testing different selectors:\n")
    for selector in selectors:
        results = soup.select(selector)
        print(f"  {selector}: {len(results)} results")
        if results and len(results) > 0:
            first = results[0]
            print(f"    First result HTML: {str(first)[:200]}...")
            # Try to find href
            link = first.select_one('a[href]') if first.name != 'a' else first
            if link and link.has_attr('href'):
                print(f"    Link: {link['href']}")
            print()
    
    # Save HTML for inspection
    with open('mangafire_search.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("\nSaved HTML to: mangafire_search.html")
else:
    print(f"Search failed with status: {response.status_code}")
