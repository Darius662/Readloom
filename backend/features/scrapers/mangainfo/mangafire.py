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
        
        # Try alternative search methods if regular search fails
        # First, try standard search
        search_url = f"{MANGAFIRE_URL}/search?q={manga_title.replace(' ', '+')}"
        LOGGER.info(f"Searching MangaFire (method 1): {search_url}")
        
        try:
            response = session.get(search_url, timeout=10)
            search_success = response.status_code == 200
        except Exception as e:
            LOGGER.warning(f"MangaFire search request failed: {e}")
            search_success = False
        
        # If first search fails, try alternative search method
        if not search_success:
            # Try direct manga URL if it looks like a common title format
            # Convert to URL-friendly format
            url_title = manga_title.lower().replace(' ', '-')
            url_title = re.sub(r'[^a-z0-9-]', '', url_title)
            alt_search_url = f"{MANGAFIRE_URL}/manga/{url_title}"
            
            LOGGER.info(f"Trying alternative MangaFire search (method 2): {alt_search_url}")
            try:
                response = session.get(alt_search_url, timeout=10)
                if response.status_code == 200:
                    search_success = True
                    LOGGER.info("Alternative search method succeeded")
                else:
                    LOGGER.warning(f"Alternative MangaFire search failed: {response.status_code}")
            except Exception as e:
                LOGGER.warning(f"Alternative MangaFire search request failed: {e}")
        
        if not search_success:
            LOGGER.warning("All MangaFire search methods failed")
            return (0, 0)
            
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.select('.manga-card')
        
        if not search_results:
            # Try alternative selector
            search_results = soup.select('.mangas-card')
            
        if not search_results:
            LOGGER.warning("No search results found on MangaFire")
            return (0, 0)
            
        # Get the first result's URL
        first_result = search_results[0]
        manga_link = first_result.select_one('a')
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
        
        # Look for chapter count in various locations
        chapter_indicators = [
            manga_soup.select_one('.manga-info span:-soup-contains("Chapter")'),
            manga_soup.select_one('.manga-info span:-soup-contains("Chapters")'),
            manga_soup.select_one('.info-item:-soup-contains("Chapter")'),
            manga_soup.select_one('div:-soup-contains("Chapters")')
        ]
        
        for indicator in chapter_indicators:
            if indicator:
                numbers = re.findall(r'\d+', indicator.text)
                if numbers:
                    chapter_count = int(numbers[0])
                    break
        
        # Try counting chapters if no count found
        if chapter_count == 0:
            chapter_elements = manga_soup.select('.chapters-list a, .chapter-item')
            if chapter_elements:
                chapter_count = len(chapter_elements)
        
        # Look for volume information
        # MangaFire often has volume information in dropdown menus or tabs
        volume_selectors = [
            '.volumes-list .volume-item',
            '.manga-volumes .volume',
            '.volume-selector option',
            '.volume-list li',
            '.manga-volume',
            '#volumes-container .volume'
        ]
        
        for selector in volume_selectors:
            volume_items = manga_soup.select(selector)
            if volume_items:
                volume_count = len(volume_items)
                LOGGER.info(f"Found {volume_count} volumes using selector {selector}")
                break
        
        # If no direct volume listing, try to find volume information in manga description or info
        if volume_count == 0:
            volume_texts = [
                manga_soup.select_one('.manga-info span:-soup-contains("Volume")'),
                manga_soup.select_one('.manga-info span:-soup-contains("Volumes")'),
                manga_soup.select_one('.info-item:-soup-contains("Volume")')
            ]
            
            for text in volume_texts:
                if text:
                    numbers = re.findall(r'\d+', text.text)
                    if numbers:
                        volume_count = int(numbers[0])
                        LOGGER.info(f"Found volume count {volume_count} in text: {text.text.strip()}")
                        break
        
        # Advanced method: look for volume patterns in chapter titles
        if volume_count == 0 and chapter_count > 0:
            all_text = manga_soup.get_text()
            vol_matches = re.findall(r'(?:^|[^0-9])(?:Vol(?:ume)?[\s.]*)(\d+)', all_text, re.IGNORECASE)
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
