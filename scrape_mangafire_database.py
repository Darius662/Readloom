#!/usr/bin/env python3
"""
Scrape MangaFire to build a comprehensive manga database.
This will create a JSON file with manga titles, chapters, and volumes.
"""

import requests
import json
import time
from bs4 import BeautifulSoup
from typing import Dict, List
import re

# User agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def scrape_manga_list(max_pages=10):
    """
    Scrape MangaFire's manga list.
    
    Args:
        max_pages: Maximum number of pages to scrape (each page has ~24 manga)
    
    Returns:
        List of manga dictionaries
    """
    manga_database = {}
    base_url = "https://mangafire.to/filter"
    
    print(f"\n{'='*80}")
    print("SCRAPING MANGAFIRE DATABASE")
    print(f"{'='*80}\n")
    
    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}/{max_pages}...")
        
        try:
            # Request the page
            params = {
                'page': page,
                'sort': 'recently_updated'  # or 'name', 'trending', etc.
            }
            
            response = requests.get(base_url, params=params, headers=HEADERS, timeout=15)
            
            if response.status_code != 200:
                print(f"  ⚠️  Failed to load page {page}: Status {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find manga cards (adjust selectors based on actual HTML structure)
            manga_cards = soup.select('.unit, .manga-card, [class*="manga"]')
            
            if not manga_cards:
                print(f"  ⚠️  No manga found on page {page} (selector might be wrong)")
                # Try alternative selectors
                manga_cards = soup.select('a[href*="/manga/"]')
            
            print(f"  Found {len(manga_cards)} manga cards")
            
            for card in manga_cards:
                try:
                    # Extract manga URL
                    manga_link = card.get('href') or card.find('a', href=True)
                    if not manga_link:
                        continue
                    
                    if isinstance(manga_link, str):
                        manga_url = manga_link
                    else:
                        manga_url = manga_link.get('href')
                    
                    if not manga_url or '/manga/' not in manga_url:
                        continue
                    
                    # Make URL absolute
                    if not manga_url.startswith('http'):
                        manga_url = f"https://mangafire.to{manga_url}"
                    
                    # Extract manga ID from URL
                    manga_id = manga_url.split('/manga/')[-1].split('?')[0].split('.')[0]
                    
                    # Skip if already scraped
                    if manga_id in manga_database:
                        continue
                    
                    # Get manga details page
                    print(f"    Scraping: {manga_id}...")
                    manga_data = scrape_manga_details(manga_url)
                    
                    if manga_data:
                        manga_database[manga_id] = manga_data
                        print(f"      ✓ {manga_data['title']}: {manga_data['chapters']} ch, {manga_data['volumes']} vol")
                    
                    # Be nice to the server
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"    ✗ Error processing card: {e}")
                    continue
            
            # Be nice between pages
            time.sleep(2)
            
        except Exception as e:
            print(f"  ✗ Error scraping page {page}: {e}")
            continue
    
    return manga_database

def scrape_manga_details(manga_url):
    """
    Scrape details for a specific manga.
    
    Args:
        manga_url: URL to the manga page
    
    Returns:
        Dictionary with manga data or None
    """
    try:
        response = requests.get(manga_url, headers=HEADERS, timeout=15)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title_elem = soup.select_one('h1, .title, [class*="title"]')
        title = title_elem.text.strip() if title_elem else "Unknown"
        
        # Extract chapters and volumes from info section
        chapters = 0
        volumes = 0
        
        # Look for info elements (adjust based on actual HTML)
        info_items = soup.select('.info-item, .meta-item, [class*="info"]')
        
        for item in info_items:
            text = item.text.lower()
            
            # Extract chapters
            if 'chapter' in text:
                match = re.search(r'(\d+)\s*chapter', text)
                if match:
                    chapters = int(match.group(1))
            
            # Extract volumes
            if 'volume' in text:
                match = re.search(r'(\d+)\s*volume', text)
                if match:
                    volumes = int(match.group(1))
        
        # Alternative: Look in the chapter list
        if chapters == 0:
            chapter_list = soup.select('[class*="chapter"], .chapter-item, li[data-number]')
            if chapter_list:
                # Try to find the highest chapter number
                for ch in chapter_list:
                    ch_text = ch.text
                    match = re.search(r'chapter\s*(\d+)', ch_text, re.IGNORECASE)
                    if match:
                        ch_num = int(match.group(1))
                        chapters = max(chapters, ch_num)
        
        # If we still don't have data, return None
        if chapters == 0 and volumes == 0:
            return None
        
        # Normalize title for database key
        normalized_title = title.lower().strip()
        normalized_title = re.sub(r'[^a-z0-9\s]', '', normalized_title)
        normalized_title = ' '.join(normalized_title.split())
        
        return {
            'title': title,
            'normalized_title': normalized_title,
            'chapters': chapters,
            'volumes': volumes,
            'url': manga_url
        }
        
    except Exception as e:
        print(f"      ✗ Error scraping details: {e}")
        return None

def save_database(manga_database, filename='mangafire_database.json'):
    """Save the database to a JSON file."""
    print(f"\n{'='*80}")
    print(f"SAVING DATABASE")
    print(f"{'='*80}\n")
    
    # Convert to a more usable format
    formatted_db = {}
    for manga_id, data in manga_database.items():
        key = data['normalized_title']
        formatted_db[key] = {
            'chapters': data['chapters'],
            'volumes': data['volumes'],
            'title': data['title']
        }
    
    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(formatted_db, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {len(formatted_db)} manga to {filename}")
    
    # Show statistics
    with_volumes = sum(1 for d in formatted_db.values() if d['volumes'] > 0)
    with_chapters = sum(1 for d in formatted_db.values() if d['chapters'] > 0)
    
    print(f"\nStatistics:")
    print(f"  Total manga: {len(formatted_db)}")
    print(f"  With volume data: {with_volumes}")
    print(f"  With chapter data: {with_chapters}")
    
    # Show sample
    print(f"\nSample entries:")
    for i, (key, data) in enumerate(list(formatted_db.items())[:5]):
        print(f"  {data['title']}: {data['chapters']} chapters, {data['volumes']} volumes")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape MangaFire to build manga database")
    parser.add_argument('--pages', type=int, default=10, help='Number of pages to scrape (default: 10)')
    parser.add_argument('--output', type=str, default='mangafire_database.json', help='Output filename')
    
    args = parser.parse_args()
    
    print(f"\nThis will scrape {args.pages} pages from MangaFire")
    print(f"Estimated time: {args.pages * 2} minutes")
    print(f"Output file: {args.output}\n")
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled")
        exit()
    
    # Scrape the database
    manga_db = scrape_manga_list(max_pages=args.pages)
    
    # Save to file
    if manga_db:
        save_database(manga_db, args.output)
        print(f"\n✓ Database created successfully!")
        print(f"\nNext steps:")
        print(f"1. Review the file: {args.output}")
        print(f"2. Use it to update constants.py or load it dynamically")
    else:
        print("\n✗ No data scraped. Check the selectors or try again.")
