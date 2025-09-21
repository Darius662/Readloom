#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Jikan API metadata provider for MyAnimeList.
Documentation: https://docs.api.jikan.moe/
"""

import requests
from typing import Dict, List, Any

from ..base import MetadataProvider
from .constants import BASE_URL, MAL_URL, DEFAULT_HEADERS, RATE_LIMIT_DELAY
from .client import make_request
from .mapper import map_search_results, map_manga_details, map_latest_releases
from .chapters import generate_chapter_list


class JikanProvider(MetadataProvider):
    """Jikan API metadata provider for MyAnimeList."""

    def __init__(self, enabled: bool = True):
        """Initialize the Jikan provider.
        
        Args:
            enabled: Whether the provider is enabled.
        """
        super().__init__("MyAnimeList", enabled)
        self.base_url = BASE_URL
        self.mal_url = MAL_URL
        self.headers = DEFAULT_HEADERS
        self.session = requests.Session()
        self.rate_limit_delay = RATE_LIMIT_DELAY

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the Jikan API.
        
        Args:
            endpoint: The API endpoint.
            params: The query parameters.
            
        Returns:
            The JSON response.
        """
        try:
            return make_request(
                self.session, 
                self.base_url, 
                endpoint, 
                self.headers, 
                params, 
                self.rate_limit_delay
            )
        except Exception as e:
            self.logger.error(f"Error making request to {endpoint}: {e}")
            raise

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for manga on MyAnimeList.
        
        Args:
            query: The search query.
            page: The page number.
            
        Returns:
            A list of manga search results.
        """
        params = {
            "q": query,
            "page": page,
            "limit": 20,
            "type": "manga"
        }
        
        try:
            self.logger.info(f"Searching for '{query}' on page {page}")
            data = self._make_request("manga", params)
            
            results = map_search_results(data, self.name)
            
            self.logger.info(f"Returning {len(results)} search results")
            return results
        except Exception as e:
            self.logger.error(f"Error searching manga on MyAnimeList: {e}")
            return []

    def get_manga_details(self, manga_id: str) -> Dict[str, Any]:
        """Get details for a manga on MyAnimeList.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            The manga details.
        """
        try:
            data = self._make_request(f"manga/{manga_id}/full")
            
            if "data" not in data:
                return {}
            
            item = data["data"]
            return map_manga_details(item, manga_id, self.name)
            
        except Exception as e:
            self.logger.error(f"Error getting manga details on MyAnimeList: {e}")
            return {}

    def get_chapter_list(self, manga_id: str) -> Dict[str, Any]:
        """Get the chapter list for a manga on MyAnimeList.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            A dictionary containing chapters and other information.
        """
        try:
            # Unfortunately, Jikan/MAL doesn't provide detailed chapter lists
            # We'll create a better approximation based on manga details
            data = self._make_request(f"manga/{manga_id}/full")
            return generate_chapter_list(manga_id, data)
            
        except Exception as e:
            self.logger.error(f"Error getting chapter list on MyAnimeList: {e}")
            return {"chapters": [], "error": str(e)}

    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter on MyAnimeList.
        
        Args:
            manga_id: The manga ID.
            chapter_id: The chapter ID.
            
        Returns:
            A list of image URLs.
        """
        # MyAnimeList doesn't provide chapter images
        return []

    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest manga releases on MyAnimeList.
        
        Args:
            page: The page number.
            
        Returns:
            A list of latest releases.
        """
        # Use currently publishing manga sorted by updated date for latest releases
        params = {
            "page": page,
            "limit": 20,
            "order_by": "start_date",  # Sort by publication start date
            "sort": "desc",           # Newest first
            "type": "manga",
            "status": "publishing"    # Currently publishing manga
        }
        
        try:
            data = self._make_request("manga", params)
            return map_latest_releases(data, self.name)
            
        except Exception as e:
            self.logger.error(f"Error getting latest releases on MyAnimeList: {e}")
            return []
