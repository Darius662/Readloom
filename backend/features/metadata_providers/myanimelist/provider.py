#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MyAnimeList metadata provider implementation.
"""

from typing import Dict, List, Any, Optional
import requests

from ..base import MetadataProvider
from ..myanimelist_client import (
    search_manga,
    get_manga_details,
    get_manga_ranking,
)
from ..myanimelist_constants import BASE_URL
from ..myanimelist_mapper import (
    map_search_results,
    map_manga_details,
    generate_chapter_list,
)


class MyAnimeListProvider(MetadataProvider):
    """MyAnimeList metadata provider."""

    def __init__(self, enabled: bool = True, client_id: str = ""):
        """Initialize the MyAnimeList provider.
        
        Args:
            enabled: Whether the provider is enabled.
            client_id: The MyAnimeList API client ID.
        """
        super().__init__("MyAnimeList", enabled)
        self.base_url = BASE_URL
        self.client_id = client_id
        self.headers = {
            "X-MAL-CLIENT-ID": client_id
        }
        self.session = requests.Session()

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for manga on MyAnimeList.
        
        Args:
            query: The search query.
            page: The page number.
            
        Returns:
            A list of manga search results.
        """
        try:
            if not self.client_id:
                self.logger.error("MyAnimeList API client ID not set")
                return []
            
            self.logger.info(f"Searching for '{query}' on page {page}")
            limit = 10
            offset = (page - 1) * limit
            data = search_manga(self.session, self.base_url, self.headers, query, limit, self.logger)
            return map_search_results(data, self.name, self.logger)
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
            if not self.client_id:
                self.logger.error("MyAnimeList API client ID not set")
                return {}
            
            data = get_manga_details(self.session, self.base_url, self.headers, manga_id, self.logger)
            return map_manga_details(data, self.name, self.logger)
        except Exception as e:
            self.logger.error(f"Error getting manga details on MyAnimeList: {e}")
            return {}

    def get_chapter_list(self, manga_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get the chapter list for a manga on MyAnimeList.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            A dictionary containing a list of chapters.
        """
        try:
            if not self.client_id:
                self.logger.error("MyAnimeList API client ID not set")
                return {"chapters": []}
            
            # MyAnimeList API doesn't provide chapter information
            # We need to generate synthetic chapter data based on manga details
            manga_details = self.get_manga_details(manga_id)
            if not manga_details:
                return {"chapters": []}
            
            return generate_chapter_list(manga_details, self.name, self.logger)
        except Exception as e:
            self.logger.error(f"Error getting chapter list on MyAnimeList: {e}")
            return {"chapters": []}

    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter on MyAnimeList.
        
        Args:
            manga_id: The manga ID.
            chapter_id: The chapter ID.
            
        Returns:
            A list of image URLs.
        """
        # MyAnimeList API doesn't provide chapter images
        self.logger.warning("MyAnimeList API doesn't provide chapter images")
        return []

    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest manga releases on MyAnimeList.
        
        Args:
            page: The page number.
            
        Returns:
            A list of latest releases.
        """
        try:
            if not self.client_id:
                self.logger.error("MyAnimeList API client ID not set")
                return []
            
            limit = 10
            data = get_manga_ranking(self.session, self.base_url, self.headers, "bypopularity", limit, self.logger)
            return map_search_results(data, self.name, self.logger)
        except Exception as e:
            self.logger.error(f"Error getting latest releases on MyAnimeList: {e}")
            return []
