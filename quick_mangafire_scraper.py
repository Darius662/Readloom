#!/usr/bin/env python3
"""
Quick scraper to test MangaFire's structure and build a small database.
This will help us understand the HTML structure before doing a full scrape.
"""

import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def test_mangafire_structure():
    """Test MangaFire's HTML structure."""
    print("\n" + "="*80)
    print("TESTING MANGAFIRE STRUCTURE")
    print("="*80 + "\n")
    
    # Test with a known manga
    test_urls = [
        "https://mangafire.to/manga/dandadan.1pqx2",
        "https://mangafire.to/manga/one-punch-man.1pqx3",
        "https://mangafire.to/filter?page=1"
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        print("-" * 60)
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            print(f"Status: {response.status_code}")
            
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Save HTML for inspection
            filename = url.split('/')[-1].replace('?', '_') + '.html'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print(f"Saved HTML to: {filename}")
            
            # Try to find key elements
            print("\nLooking for key elements:")
            
            # Title
            title = soup.select_one('h1, .title, [class*="title"]')
            if title:
                print(f"  Title: {title.text.strip()}")
            
            # Info section
            info_section = soup.select('.info, .meta, [class*="info"]')
            print(f"  Info sections found: {len(info_section)}")
            
            # Chapters
            chapters = soup.select('[class*="chapter"], .chapter-item')
            print(f"  Chapter elements found: {len(chapters)}")
            
            # Look for volume/chapter counts in text
            text = soup.get_text()
            if 'volume' in text.lower():
                print(f"  ✓ Contains 'volume' text")
            if 'chapter' in text.lower():
                print(f"  ✓ Contains 'chapter' text")
            
        except Exception as e:
            print(f"Error: {e}")

def scrape_specific_manga(manga_slug):
    """Scrape a specific manga by slug."""
    url = f"https://mangafire.to/manga/{manga_slug}"
    print(f"\nScraping: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code != 200:
            print(f"Failed: Status {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all text and look for patterns
        text = soup.get_text()
        
        # Look for volume/chapter info
        import re
        
        # Try to find "X Volumes" or "X Chapters"
        volume_match = re.search(r'(\d+)\s*Volumes?', text, re.IGNORECASE)
        chapter_match = re.search(r'(\d+)\s*Chapters?', text, re.IGNORECASE)
        
        volumes = int(volume_match.group(1)) if volume_match else 0
        chapters = int(chapter_match.group(1)) if chapter_match else 0
        
        print(f"  Volumes: {volumes}")
        print(f"  Chapters: {chapters}")
        
        return {'volumes': volumes, 'chapters': chapters}
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("\nOption 1: Test HTML structure")
    print("Option 2: Scrape specific manga")
    print("Option 3: Build database from list")
    
    choice = input("\nChoose option (1/2/3): ")
    
    if choice == '1':
        test_mangafire_structure()
    elif choice == '2':
        slug = input("Enter manga slug (e.g., 'dandadan.1pqx2'): ")
        scrape_specific_manga(slug)
    elif choice == '3':
        print("\nUse scrape_mangafire_database.py for full scraping")
    else:
        print("Invalid choice")
