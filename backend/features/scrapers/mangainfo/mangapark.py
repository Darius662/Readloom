#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaPark scraper for MangaInfo provider.
"""

import re
import time
from typing import Tuple
import requests
from bs4 import BeautifulSoup

from backend.base.logging import LOGGER
from .constants import MANGAPARK_URL
from .utils import get_random_headers


def get_mangapark_data(session: requests.Session, manga_title: str) -> Tuple[int, int]:
    """
    Get chapter and volume counts from MangaPark.
    
    Args:
        session: The requests session to use.
        manga_title: The manga title.
        
    Returns:
        Tuple[int, int]: (chapter_count, volume_count)
    """
    try:
        # Update headers for this request
        session.headers.update(get_random_headers())
        
        # Search for the manga
        search_url = f"{MANGAPARK_URL}/search?q={manga_title.replace(' ', '+')}"
        LOGGER.info(f"Searching MangaPark: {search_url}")
        
        response = session.get(search_url, timeout=10)
        if response.status_code != 200:
            LOGGER.warning(f"MangaPark search failed: {response.status_code}")
            return (0, 0)
            
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.select('.manga-list .item')
        
        if not search_results:
            return (0, 0)
            
        # Get the first result's URL
        first_result = search_results[0]
        manga_link = first_result.select_one('a.fw-bold')
        if not manga_link or not manga_link.has_attr('href'):
            return (0, 0)
            
        # Get the manga details page
        manga_url = MANGAPARK_URL + manga_link['href']
        
        # Small delay
        time.sleep(1)
        
        # Get the manga details
        manga_response = session.get(manga_url, timeout=10)
        if manga_response.status_code != 200:
            return (0, 0)
            
        manga_soup = BeautifulSoup(manga_response.text, 'html.parser')
        
        # Look for chapter count
        chapter_count = 0
        chapter_text = manga_soup.select_one('.detail-set span:-soup-contains("Chapter")')
        if chapter_text:
            # Extract numbers from text
            numbers = re.findall(r'\d+', chapter_text.text)
            if numbers:
                chapter_count = int(numbers[0])
        
        # If no chapter count found, try counting chapter links
        if chapter_count == 0:
            chapter_links = manga_soup.select('.chapter-list a')
            chapter_count = len(chapter_links)
        
        # Look for volume count if available - enhanced search
        volume_count = 0
        
        # Try various selectors that might contain volume information
        volume_selectors = [
            '.detail-set span:-soup-contains("Volume")',
            '.info-item:-soup-contains("Volume")',
            '.manga-info-text li:-soup-contains("Volume")',
            '.series-information:-soup-contains("Volume")',
            '.manga-stats:-soup-contains("Volume")'
        ]
        
        for selector in volume_selectors:
            volume_text = manga_soup.select_one(selector)
            if volume_text:
                numbers = re.findall(r'\d+', volume_text.text)
                if numbers:
                    volume_count = int(numbers[0])
                    break
        
        # If volume count is still 0, try advanced detection methods
        if volume_count == 0:
            # Look for volume dropdown menu or selector
            volume_dropdown = manga_soup.select('.volume-selector option, .volume-list li, .volumes-container .volume')
            if volume_dropdown:
                volume_count = len(volume_dropdown)
            
            # Check for volume listings
            volume_listings = manga_soup.select('[class*="volume"], [id*="volume"]')
            if volume_listings and volume_count == 0:
                # Count unique volume references
                volume_numbers = set()
                for item in volume_listings:
                    vol_matches = re.findall(r'(?:^|[^0-9])(?:Vol(?:ume)?[\s.]*)(\d+)', item.text, re.IGNORECASE)
                    volume_numbers.update(vol_matches)
                
                if volume_numbers:
                    volume_count = len(volume_numbers)
        
        # If we still don't have a volume count, estimate based on chapters
        if volume_count == 0:
            volume_count = max(1, chapter_count // 10)
        
        if chapter_count > 0:
            LOGGER.info(f"MangaPark data for {manga_title}: {chapter_count} chapters, {volume_count} volumes")
            
        return (chapter_count, volume_count)
        
    except Exception as e:
        LOGGER.error(f"Error getting MangaPark data: {e}")
        return (0, 0)
