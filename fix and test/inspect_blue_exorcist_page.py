#!/usr/bin/env python3
"""
Inspect the Blue Exorcist MangaFire page to find where volume count is.
"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://mangafire.to/manga/ao-no-exorcistt.kl6"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"\nInspecting: {url}\n")

response = requests.get(url, headers=headers, timeout=10)
print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for volume information in various places
    print("Looking for volume information:\n")
    
    # 1. Check for volume dropdown/selector
    volume_selectors = soup.select('[data-name="vol"] li, .volume-list li, option[value*="volume"]')
    print(f"1. Volume list items: {len(volume_selectors)}")
    if volume_selectors:
        print(f"   Sample: {volume_selectors[0].text.strip()[:50]}")
    
    # 2. Check for volume tabs
    volume_tabs = soup.select('[data-name="vol"]')
    print(f"\n2. Volume tabs: {len(volume_tabs)}")
    if volume_tabs:
        # Count items inside
        items = volume_tabs[0].select('li, a')
        print(f"   Items inside: {len(items)}")
    
    # 3. Look for text containing "volume"
    text = soup.get_text()
    volume_matches = re.findall(r'(\d+)\s*volumes?', text, re.IGNORECASE)
    if volume_matches:
        print(f"\n3. Found in text: {set(volume_matches)}")
    
    # 4. Look for volume pattern in URLs
    volume_urls = soup.select('a[href*="volume"]')
    print(f"\n4. Links with 'volume': {len(volume_urls)}")
    if volume_urls:
        # Extract volume numbers
        vol_numbers = set()
        for link in volume_urls:
            match = re.search(r'volume[/-](\d+)', link['href'])
            if match:
                vol_numbers.add(match.group(1))
        print(f"   Unique volumes: {sorted(vol_numbers, key=int) if vol_numbers else 'none'}")
    
    # 5. Save HTML for manual inspection
    with open('blue_exorcist_page.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print(f"\n5. Saved HTML to: blue_exorcist_page.html")
    
    # 6. Look for specific info sections
    info_items = soup.select('.info-item, .meta-item, [class*="info"]')
    print(f"\n6. Info items found: {len(info_items)}")
    for item in info_items[:5]:
        text = item.text.strip()
        if 'volume' in text.lower() or 'chapter' in text.lower():
            print(f"   {text[:100]}")
else:
    print(f"Failed with status: {response.status_code}")
