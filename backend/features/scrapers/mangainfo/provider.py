#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaInfo provider implementation.
"""

import requests
import re
import json
from pathlib import Path
from typing import Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from .constants import POPULAR_MANGA_DATA
from .utils import get_random_headers, get_estimated_data
from .mangapark import get_mangapark_data
from .mangadex import get_mangadex_data
from .mangafire import get_mangafire_data


class MangaInfoProvider:
    """Manga chapter and volume count provider using smart database caching."""

    def __init__(self):
        """Initialize the manga info provider."""
        # Use a session for better performance and cookie handling
        self.session = requests.Session()
        self.session.headers.update(get_random_headers())
        
        # Memory cache to avoid repeated database queries in the same session
        self.memory_cache = {}
        
        # Dynamic static database (loaded from JSON, auto-populated)
        self.static_db_file = Path(__file__).parent / 'manga_static_db.json'
        self.dynamic_static_db = self._load_static_db()
    
    def _load_static_db(self) -> Dict:
        """Load the dynamic static database from JSON file.
        
        Returns:
            Dictionary of manga data
        """
        # Start with the hardcoded popular manga as base
        db = dict(POPULAR_MANGA_DATA)
        
        # Load additional manga from JSON file if it exists
        if self.static_db_file.exists():
            try:
                with open(self.static_db_file, 'r', encoding='utf-8') as f:
                    json_db = json.load(f)
                    db.update(json_db)
                    LOGGER.info(f"Loaded {len(json_db)} manga from dynamic static database")
            except Exception as e:
                LOGGER.error(f"Error loading static database: {e}")
        
        return db
    
    def _save_to_static_db(self, manga_title: str, chapters: int, volumes: int):
        """Save manga data to the dynamic static database.
        
        Args:
            manga_title: The manga title
            chapters: Number of chapters
            volumes: Number of volumes
        """
        try:
            # Normalize title for key
            normalized_title = self.normalize_title(manga_title)
            
            # Add to in-memory database
            self.dynamic_static_db[normalized_title] = {
                'chapters': chapters,
                'volumes': volumes,
                'title': manga_title
            }
            
            # Load existing JSON file
            existing_db = {}
            if self.static_db_file.exists():
                try:
                    with open(self.static_db_file, 'r', encoding='utf-8') as f:
                        existing_db = json.load(f)
                except Exception as e:
                    LOGGER.warning(f"Error reading existing static DB: {e}")
            
            # Add new entry
            existing_db[normalized_title] = {
                'chapters': chapters,
                'volumes': volumes,
                'title': manga_title
            }
            
            # Save to JSON file
            with open(self.static_db_file, 'w', encoding='utf-8') as f:
                json.dump(existing_db, f, indent=2, ensure_ascii=False)
            
            LOGGER.info(f"Saved {manga_title} to dynamic static database ({volumes} volumes)")
            
        except Exception as e:
            LOGGER.error(f"Error saving to static database: {e}")
    
    @staticmethod
    def normalize_title(title: str) -> str:
        """Normalize a manga title for consistent matching.
        
        Args:
            title: The manga title to normalize
            
        Returns:
            Normalized title (lowercase, alphanumeric only)
        """
        # Convert to lowercase and remove special characters
        normalized = re.sub(r'[^a-z0-9\s]', '', title.lower())
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        return normalized
    
    def get_chapter_count(self, manga_title: str, anilist_id: Optional[str] = None, 
                         status: Optional[str] = None, force_refresh: bool = False) -> Tuple[int, int]:
        """
        Get chapter and volume count for a manga using smart caching.
        
        Args:
            manga_title: The title of the manga
            anilist_id: Optional AniList ID for better cache matching
            status: Optional manga status (ONGOING, COMPLETED, etc.)
            force_refresh: If True, bypass cache and scrape fresh data
            
        Returns:
            Tuple of (chapter_count, volume_count)
        """
        # Check memory cache first (for same session)
        cache_key = f"{manga_title}_{anilist_id}" if anilist_id else manga_title
        if not force_refresh and cache_key in self.memory_cache:
            LOGGER.info(f"Using memory cache for {manga_title}: {self.memory_cache[cache_key]}")
            return self.memory_cache[cache_key]
        
        # Normalize title for database lookup
        normalized_title = self.normalize_title(manga_title)
        
        # Check database cache
        if not force_refresh:
            cached_data = self._get_from_cache(normalized_title, anilist_id)
            if cached_data:
                result = (cached_data['chapter_count'], cached_data['volume_count'])
                self.memory_cache[cache_key] = result
                return result
        
        # No cache or force refresh - scrape fresh data
        LOGGER.info(f"Scraping fresh data for {manga_title}")
        chapters, volumes, source = self._scrape_data(manga_title)
        
        # Store in database cache
        self._save_to_cache(
            manga_title=manga_title,
            normalized_title=normalized_title,
            anilist_id=anilist_id,
            chapter_count=chapters,
            volume_count=volumes,
            source=source,
            status=status
        )
        
        # Store in memory cache
        result = (chapters, volumes)
        self.memory_cache[cache_key] = result
        
        return result
    
    def _get_from_cache(self, normalized_title: str, anilist_id: Optional[str] = None) -> Optional[Dict]:
        """Get cached data from database.
        
        Args:
            normalized_title: Normalized manga title
            anilist_id: Optional AniList ID
            
        Returns:
            Cached data dict or None if not found/stale
        """
        try:
            # Try to find by AniList ID first (most accurate)
            if anilist_id:
                result = execute_query(
                    "SELECT * FROM manga_volume_cache WHERE anilist_id = ? ORDER BY refreshed_at DESC LIMIT 1",
                    (anilist_id,)
                )
                if result:
                    cache_entry = result[0]
                    if self._is_cache_fresh(cache_entry):
                        LOGGER.info(f"Using database cache (by AniList ID): {cache_entry['manga_title']}")
                        return cache_entry
                    else:
                        LOGGER.info(f"Cache stale for {cache_entry['manga_title']}, will refresh")
                        return None
            
            # Try to find by normalized title
            result = execute_query(
                "SELECT * FROM manga_volume_cache WHERE manga_title_normalized = ? ORDER BY refreshed_at DESC LIMIT 1",
                (normalized_title,)
            )
            if result:
                cache_entry = result[0]
                if self._is_cache_fresh(cache_entry):
                    LOGGER.info(f"Using database cache (by title): {cache_entry['manga_title']}")
                    return cache_entry
                else:
                    LOGGER.info(f"Cache stale for {cache_entry['manga_title']}, will refresh")
                    return None
            
            return None
        except Exception as e:
            LOGGER.error(f"Error reading from cache: {e}")
            return None
    
    def _is_cache_fresh(self, cache_entry: Dict) -> bool:
        """Check if a cache entry is still fresh.
        
        Args:
            cache_entry: The cache entry dict
            
        Returns:
            True if cache is fresh, False if stale
        """
        try:
            refreshed_at = datetime.fromisoformat(cache_entry['refreshed_at'])
            age_days = (datetime.now() - refreshed_at).days
            
            # Determine freshness based on status
            status = cache_entry.get('status', '').upper()
            if status == 'COMPLETED' or status == 'FINISHED':
                # Completed manga: cache for 90 days
                return age_days < 90
            else:
                # Ongoing manga: cache for 30 days
                return age_days < 30
        except Exception as e:
            LOGGER.error(f"Error checking cache freshness: {e}")
            return False
    
    def _scrape_data(self, manga_title: str) -> Tuple[int, int, str]:
        """Scrape data from multiple sources.
        
        Args:
            manga_title: The manga title
            
        Returns:
            Tuple of (chapters, volumes, source)
        """
        # First, check dynamic static database (includes both hardcoded and auto-populated)
        manga_title_lower = manga_title.lower()
        normalized_title = self.normalize_title(manga_title)
        
        # Check by normalized title first (exact match)
        if normalized_title in self.dynamic_static_db:
            data = self.dynamic_static_db[normalized_title]
            LOGGER.info(f"Found in static database: {manga_title} (exact match)")
            return (data['chapters'], data['volumes'], 'static_database')
        
        # Check by partial match
        for known_title, data in self.dynamic_static_db.items():
            # Check main title
            if known_title in manga_title_lower or manga_title_lower in known_title:
                LOGGER.info(f"Found in static database: {manga_title} (matched: {known_title})")
                return (data['chapters'], data['volumes'], 'static_database')
            
            # Check aliases if they exist
            if 'aliases' in data:
                for alias in data['aliases']:
                    alias_lower = alias.lower()
                    if alias_lower in manga_title_lower or manga_title_lower in alias_lower:
                        LOGGER.info(f"Found in static database: {manga_title} (matched alias: {alias})")
                        return (data['chapters'], data['volumes'], 'static_database')
        
        # Not in static database, scrape from web sources
        LOGGER.info(f"Not in static database, scraping web sources for: {manga_title}")
        results = []
        sources = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Try MangaPark, MangaDex API, MangaFire and estimation in parallel
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
                sources.append('mangapark')
                
            if mangadex_result[0] > 0:
                results.append(mangadex_result)
                sources.append('mangadex')
                
            if mangafire_result[0] > 0:
                results.append(mangafire_result)
                sources.append('mangafire')
                
            results.append(estimate_result)
            sources.append('estimation')
        
        # Sort results by chapter count (descending) to get the most complete data
        sorted_results = sorted(zip(results, sources), key=lambda x: x[0][0], reverse=True)
        
        # Use the result with the highest chapter count
        if sorted_results:
            best_result, best_source = sorted_results[0]
            chapters, volumes = best_result
            LOGGER.info(f"Best data for {manga_title}: {chapters} chapters, {volumes} volumes (source: {best_source})")
            
            # Save to dynamic static database if we got good data (not estimation)
            if best_source != 'estimation' and volumes > 0:
                self._save_to_static_db(manga_title, chapters, volumes)
            
            return (chapters, volumes, best_source)
        
        # Fallback to a very conservative estimate
        LOGGER.warning(f"No data found for {manga_title}, using fallback")
        return (20, 2, 'fallback')
    
    def _save_to_cache(self, manga_title: str, normalized_title: str, anilist_id: Optional[str],
                       chapter_count: int, volume_count: int, source: str, status: Optional[str]) -> None:
        """Save scraped data to database cache.
        
        Args:
            manga_title: Original manga title
            normalized_title: Normalized title
            anilist_id: Optional AniList ID
            chapter_count: Number of chapters
            volume_count: Number of volumes
            source: Data source
            status: Manga status
        """
        try:
            # Check if entry exists
            existing = execute_query(
                "SELECT id, refresh_count FROM manga_volume_cache WHERE manga_title_normalized = ?",
                (normalized_title,)
            )
            
            if existing:
                # Update existing entry
                refresh_count = existing[0]['refresh_count'] + 1
                execute_query(
                    """
                    UPDATE manga_volume_cache 
                    SET chapter_count = ?, volume_count = ?, source = ?, status = ?,
                        refreshed_at = CURRENT_TIMESTAMP, refresh_count = ?, anilist_id = ?
                    WHERE manga_title_normalized = ?
                    """,
                    (chapter_count, volume_count, source, status, refresh_count, anilist_id, normalized_title),
                    commit=True
                )
                LOGGER.info(f"Updated cache for {manga_title} (refresh #{refresh_count})")
            else:
                # Insert new entry
                execute_query(
                    """
                    INSERT INTO manga_volume_cache 
                    (manga_title, manga_title_normalized, anilist_id, chapter_count, volume_count, source, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (manga_title, normalized_title, anilist_id, chapter_count, volume_count, source, status),
                    commit=True
                )
                LOGGER.info(f"Cached data for {manga_title}: {chapter_count} chapters, {volume_count} volumes")
        except Exception as e:
            LOGGER.error(f"Error saving to cache: {e}")
