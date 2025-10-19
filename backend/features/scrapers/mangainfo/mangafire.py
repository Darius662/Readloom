#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaFire scraper for MangaInfo provider.
"""

import re
import time
from typing import Tuple
import requests
from bs4 import BeautifulSoup

from backend.base.logging import LOGGER
from .constants import MANGAFIRE_URL
from .utils import get_random_headers


def get_mangafire_data(session: requests.Session, manga_title: str) -> Tuple[int, int]:
    """
    Get chapter and volume counts from MangaFire.
    This source is especially good for volume information.
    
    Args:
        session: The requests session to use.
        manga_title: The manga title.
        
    Returns:
        Tuple[int, int]: (chapter_count, volume_count)
    """
    try:
        # Update headers for this request
        session.headers.update(get_random_headers())
        
        # Use the filter page (search page is broken, returns 404)
        filter_url = f"{MANGAFIRE_URL}/filter?keyword={manga_title.replace(' ', '+')}"
        LOGGER.info(f"Searching MangaFire: {filter_url}")
        
        try:
            response = session.get(filter_url, timeout=10)
            if response.status_code != 200:
                LOGGER.warning(f"MangaFire filter page failed: {response.status_code}")
                return (0, 0)
        except Exception as e:
            LOGGER.warning(f"MangaFire request failed: {e}")
            return (0, 0)
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # UPDATED: MangaFire now uses different selectors
        search_results = soup.select('.manga-card, .unit, .manga-item')
            
        if not search_results:
            LOGGER.warning("No search results found on MangaFire")
            return (0, 0)
            
        # Get the first result's URL
        first_result = search_results[0]
        manga_link = first_result.select_one('a[href*="/manga/"], a[href*="/series/"]')
        if not manga_link or not manga_link.has_attr('href'):
            LOGGER.warning("No manga link found in search results")
            return (0, 0)
            
        # Get the manga details page
        manga_url = MANGAFIRE_URL + manga_link['href'] if not manga_link['href'].startswith('http') else manga_link['href']
        
        # Small delay
        time.sleep(1)
        
        # Get the manga details
        manga_response = session.get(manga_url, timeout=10)
        if manga_response.status_code != 200:
            LOGGER.warning(f"MangaFire manga page failed: {manga_response.status_code}")
            return (0, 0)
            
        manga_soup = BeautifulSoup(manga_response.text, 'html.parser')
        
        # Extract chapters and volumes information
        chapter_count = 0
        volume_count = 0
        
        # UPDATED: Look for chapter count in various locations with updated selectors
        chapter_indicators = [
            manga_soup.select_one('.manga-info span:-soup-contains("Chapter")'),
            manga_soup.select_one('.manga-info span:-soup-contains("Chapters")'),
            manga_soup.select_one('.info-item:-soup-contains("Chapter")'),
            manga_soup.select_one('div:-soup-contains("Chapters")'),
            manga_soup.select_one('.detail-info:-soup-contains("Chapter")'),
            manga_soup.select_one('.series-info:-soup-contains("Chapter")')
        ]
        
        for indicator in chapter_indicators:
            if indicator:
                numbers = re.findall(r'\d+', indicator.text)
                if numbers:
                    chapter_count = int(numbers[0])
                    break
        
        # Try counting chapters if no count found
        if chapter_count == 0:
            chapter_elements = manga_soup.select('.chapters-list a, .chapter-item, .chapter-row, .chapter-link')
            if chapter_elements:
                chapter_count = len(chapter_elements)
        
        # UPDATED: Look for volume information with updated selectors
        volume_selectors = [
            '.volumes-list .volume-item',
            '.manga-volumes .volume',
            '.volume-selector option',
            '.volume-list li',
            '.manga-volume',
            '#volumes-container .volume',
            '.volume-dropdown option',
            '.volume-select option',
            '.volume-container .volume'
        ]
        
        for selector in volume_selectors:
            volume_items = manga_soup.select(selector)
            if volume_items:
                volume_count = len(volume_items)
                LOGGER.info(f"Found {volume_count} volumes using selector {selector}")
                break
        
        # UPDATED: If no direct volume listing, try to find volume information in manga description or info
        if volume_count == 0:
            # Check language dropdown (e.g., "English (32 Volumes)")
            dropdown_items = manga_soup.select('.dropdown-item, .language-item, .format-item')
            for item in dropdown_items:
                match = re.search(r'\((\d+)\s+Volumes?\)', item.text, re.IGNORECASE)
                if match:
                    volume_count = int(match.group(1))
                    LOGGER.info(f"Found volume count {volume_count} in dropdown: {item.text.strip()}")
                    break
            
            # If still not found, check other text elements
            if volume_count == 0:
                volume_texts = [
                    manga_soup.select_one('.manga-info span:-soup-contains("Volume")'),
                    manga_soup.select_one('.manga-info span:-soup-contains("Volumes")'),
                    manga_soup.select_one('.info-item:-soup-contains("Volume")'),
                    manga_soup.select_one('.detail-info:-soup-contains("Volume")'),
                    manga_soup.select_one('.series-info:-soup-contains("Volume")')
                ]
                
                for text in volume_texts:
                    if text:
                        numbers = re.findall(r'\d+', text.text)
                        if numbers:
                            volume_count = int(numbers[0])
                            LOGGER.info(f"Found volume count {volume_count} in text: {text.text.strip()}")
                            break
        
        # UPDATED: Look for volume patterns in chapter titles with improved regex
        if volume_count == 0 and chapter_count > 0:
            all_text = manga_soup.get_text()
            vol_matches = re.findall(r'(?:^|[^0-9a-zA-Z])(?:Vol(?:ume)?[\s.]*?)(\d+)(?:[^0-9]|$)', all_text, re.IGNORECASE)
            unique_volumes = set(vol_matches)
            
            if unique_volumes:
                volume_count = len(unique_volumes)
                LOGGER.info(f"Inferred {volume_count} volumes from text pattern matching")
        
        # If we still don't have volume count, estimate based on chapters
        if volume_count == 0:
            volume_count = max(1, chapter_count // 9)  # Roughly 9 chapters per volume on average
            LOGGER.info(f"Estimated {volume_count} volumes based on {chapter_count} chapters")
        
        LOGGER.info(f"MangaFire data for {manga_title}: {chapter_count} chapters, {volume_count} volumes")
        return (chapter_count, volume_count)
        
    except Exception as e:
        LOGGER.error(f"Error getting MangaFire data: {e}")
        return (0, 0)
