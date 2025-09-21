#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaDex metadata provider implementation.
"""

from typing import Dict, List, Any, Optional
import requests

from ..base import MetadataProvider
from ..mangadex_client import (
    search_manga,
    get_manga_by_id,
    get_manga_chapters,
    get_chapter_images as get_chapter_images_api,
    get_latest_releases,
)
from ..mangadex_constants import DEFAULT_HEADERS, BASE_URL
from ..mangadex_mapper import (
    map_search_results,
    map_manga_details,
    map_chapter_list,
    map_chapter_images,
)


class MangaDexProvider(MetadataProvider):
    """MangaDex metadata provider."""

    def __init__(self, enabled: bool = True):
        """Initialize the MangaDex provider.
        
        Args:
            enabled: Whether the provider is enabled.
        """
        super().__init__("MangaDex", enabled)
        self.base_url = BASE_URL
        self.headers = DEFAULT_HEADERS.copy()
        self.session = requests.Session()

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for manga on MangaDex.
        
        Args:
            query: The search query.
            page: The page number.
            
        Returns:
            A list of manga search results.
        """
        try:
            self.logger.info(f"Searching for '{query}' on page {page}")
            data = search_manga(self.session, self.base_url, self.headers, query, page, self.logger)
            return map_search_results(data, self.name, self.logger)
        except Exception as e:
            self.logger.error(f"Error searching manga on MangaDex: {e}")
            return []

    def get_manga_details(self, manga_id: str) -> Dict[str, Any]:
        """Get details for a manga on MangaDex.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            The manga details.
        """
        try:
            data = get_manga_by_id(self.session, self.base_url, self.headers, manga_id, self.logger)
            return map_manga_details(data, self.name, self.logger)
        except Exception as e:
            self.logger.error(f"Error getting manga details on MangaDex: {e}")
            return {}

    def get_chapter_list(self, manga_id: str) -> List[Dict[str, Any]]:
        """Get the chapter list for a manga on MangaDex.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            A list of chapters.
        """
        try:
            data = get_manga_chapters(self.session, self.base_url, self.headers, manga_id, self.logger)
            chapters = map_chapter_list(data, manga_id, self.name, self.logger)
            return {"chapters": chapters}
        except Exception as e:
            self.logger.error(f"Error getting chapter list on MangaDex: {e}")
            return {"chapters": []}

    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter on MangaDex.
        
        Args:
            manga_id: The manga ID.
            chapter_id: The chapter ID.
            
        Returns:
            A list of image URLs.
        """
        try:
            data = get_chapter_images_api(self.session, self.base_url, self.headers, chapter_id, self.logger)
            return map_chapter_images(data, self.logger)
        except Exception as e:
            self.logger.error(f"Error getting chapter images on MangaDex: {e}")
            return []

    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest manga releases on MangaDex.
        
        Args:
            page: The page number.
            
        Returns:
            A list of latest releases.
        """
        try:
            data = get_latest_releases(self.session, self.base_url, self.headers, page, self.logger)
            return map_search_results(data, self.name, self.logger)
        except Exception as e:
            self.logger.error(f"Error getting latest releases on MangaDex: {e}")
            return []
