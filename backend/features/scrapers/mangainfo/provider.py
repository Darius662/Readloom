#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaInfo provider implementation.
"""

import requests
from typing import Dict, Tuple
from concurrent.futures import ThreadPoolExecutor

from backend.base.logging import LOGGER
from .constants import POPULAR_MANGA_DATA
from .utils import get_random_headers, get_estimated_data
from .mangapark import get_mangapark_data
from .mangadex import get_mangadex_data
from .mangafire import get_mangafire_data


class MangaInfoProvider:
    """Manga chapter and volume count provider using multiple sources."""

    def __init__(self):
        """Initialize the manga info provider."""
        # Use a session for better performance and cookie handling
        self.session = requests.Session()
        self.session.headers.update(get_random_headers())
        
        # Cache to avoid repeated requests for the same manga
        self.cache = {}
    
    def get_chapter_count(self, manga_title: str) -> Tuple[int, int]:
        """
        Get chapter and volume count for a manga.
        
        Args:
            manga_title: The title of the manga
            
        Returns:
            Tuple of (chapter_count, volume_count)
        """
        # Check cache first
        if manga_title in self.cache:
            LOGGER.info(f"Using cached data for {manga_title}: {self.cache[manga_title]}")
            return self.cache[manga_title]
        
        # Check if this is a popular manga we have static data for
        manga_title_lower = manga_title.lower()
        
        # Look for matching popular manga in our static database
        for known_title, data in POPULAR_MANGA_DATA.items():
            if known_title in manga_title_lower or manga_title_lower in known_title:
                result = (data['chapters'], data['volumes'])
                LOGGER.info(f"Using static data for {manga_title}: {result[0]} chapters, {result[1]} volumes")
                self.cache[manga_title] = result
                return result
        
        # Try different sources to get the most accurate data
        results = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Try MangaPark, MangaDex API, MangaFire and a generic estimation in parallel
            future_mangapark = executor.submit(get_mangapark_data, self.session, manga_title)
            future_mangadex = executor.submit(get_mangadex_data, manga_title)
            future_mangafire = executor.submit(get_mangafire_data, self.session, manga_title)
            future_estimate = executor.submit(get_estimated_data, manga_title)
            
            # Collect results
            mangapark_result = future_mangapark.result()
            mangadex_result = future_mangadex.result()
            mangafire_result = future_mangafire.result()
            estimate_result = future_estimate.result()
            
            # Add valid results to our collection
            if mangapark_result[0] > 0:
                results.append(mangapark_result)
                
            if mangadex_result[0] > 0:
                results.append(mangadex_result)
                
            if mangafire_result[0] > 0:
                results.append(mangafire_result)
                
            results.append(estimate_result)  # Always include our estimate as fallback
        
        # Sort results by chapter count (descending) to get the most complete data
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Use the result with the highest chapter count
        if results:
            best_result = results[0]
            LOGGER.info(f"Best data for {manga_title}: {best_result[0]} chapters, {best_result[1]} volumes")
            self.cache[manga_title] = best_result
            return best_result
        
        # Fallback to a very conservative estimate
        result = (20, 2)  # 20 chapters, 2 volumes as minimum
        self.cache[manga_title] = result
        return result
