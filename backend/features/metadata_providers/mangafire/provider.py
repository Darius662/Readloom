#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaFire metadata provider implementation.
"""

from typing import Dict, List, Any, Optional
import requests

from ..base import MetadataProvider
from ..mangafire_client import make_request
from ..mangafire_constants import DEFAULT_HEADERS, BASE_URL, SEARCH_URL, MANGA_URL, LATEST_URL
from ..mangafire_parser import (
    parse_search_results,
    parse_manga_details,
    parse_chapter_list,
    parse_chapter_images,
    parse_latest_releases,
)


class MangaFireProvider(MetadataProvider):
    """MangaFire metadata provider."""

    def __init__(self, enabled: bool = True):
        """Initialize the MangaFire provider.
        
        Args:
            enabled: Whether the provider is enabled.
        """
        super().__init__("MangaFire", enabled)
        self.base_url = BASE_URL
        self.search_url = SEARCH_URL
        self.manga_url = MANGA_URL
        self.latest_url = LATEST_URL
        self.headers = DEFAULT_HEADERS.copy()
        self.headers["Referer"] = self.base_url
        self.session = requests.Session()

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a request to the MangaFire API.
        
        Args:
            url: The URL to request.
            params: The query parameters.
            
        Returns:
            The response.
        """
        return make_request(self.session, url, self.headers, params, self.logger)

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for manga on MangaFire.
        
        Args:
            query: The search query.
            page: The page number.
            
        Returns:
            A list of manga search results.
        """
        params = {
            "keyword": query,
            "page": page
        }
        
        try:
            self.logger.info(f"Searching for '{query}' on page {page}")
            response = self._make_request(self.search_url, params)
            return parse_search_results(response.text, self.name, self.logger)
        except Exception as e:
            self.logger.error(f"Error searching manga on MangaFire: {e}")
            return []

    def get_manga_details(self, manga_id: str) -> Dict[str, Any]:
        """Get details for a manga on MangaFire.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            The manga details.
        """
        url = f"{self.manga_url}/{manga_id}"
        
        try:
            response = self._make_request(url)
            return parse_manga_details(response.text, manga_id, self.name, self.logger)
        except Exception as e:
            self.logger.error(f"Error getting manga details on MangaFire: {e}")
            return {}

    def get_chapter_list(self, manga_id: str) -> List[Dict[str, Any]]:
        """Get the chapter list for a manga on MangaFire.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            A list of chapters.
        """
        url = f"{self.manga_url}/{manga_id}"
        
        try:
            response = self._make_request(url)
            return parse_chapter_list(response.text, manga_id, self.name, self.logger)
        except Exception as e:
            self.logger.error(f"Error getting chapter list on MangaFire: {e}")
            return []

    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter on MangaFire.
        
        Args:
            manga_id: The manga ID.
            chapter_id: The chapter ID.
            
        Returns:
            A list of image URLs.
        """
        url = f"{self.manga_url}/{manga_id}/{chapter_id}"
        
        try:
            response = self._make_request(url)
            return parse_chapter_images(response.text, self.logger)
        except Exception as e:
            self.logger.error(f"Error getting chapter images on MangaFire: {e}")
            return []

    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest manga releases on MangaFire.
        
        Args:
            page: The page number.
            
        Returns:
            A list of latest releases.
        """
        params = {
            "page": page
        }
        
        try:
            response = self._make_request(self.latest_url, params)
            return parse_latest_releases(response.text, self.name, self.logger)
        except Exception as e:
            self.logger.error(f"Error getting latest releases on MangaFire: {e}")
            return []
