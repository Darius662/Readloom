#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Manga-API metadata provider.
Based on the API from https://github.com/FireFlyDeveloper/Manga-API
"""

import json
from typing import Dict, List, Any, Optional
import requests
from urllib.parse import quote

from .base import MetadataProvider


class MangaAPIProvider(MetadataProvider):
    """Manga-API metadata provider."""

    def __init__(self, enabled: bool = True, api_url: str = "https://manga-api.fly.dev"):
        """Initialize the Manga-API provider.
        
        Args:
            enabled: Whether the provider is enabled.
            api_url: The base URL for the Manga-API.
        """
        super().__init__("MangaAPI", enabled)
        self.api_url = api_url
        self.headers = {
            "User-Agent": "MangaArr/1.0.0",
            "Accept": "application/json"
        }
        self.session = requests.Session()

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the Manga-API.
        
        Args:
            endpoint: The API endpoint.
            params: The query parameters.
            
        Returns:
            The JSON response.
        """
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error making request to {url}: {e}")
            return {}

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for manga using Manga-API.
        
        Args:
            query: The search query.
            page: The page number.
            
        Returns:
            A list of manga search results.
        """
        endpoint = "/search"
        params = {
            "query": query,
            "page": page
        }
        
        try:
            data = self._make_request(endpoint, params)
            
            results = []
            if "mangas" in data:
                for manga in data["mangas"]:
                    try:
                        results.append({
                            "id": manga.get("id", ""),
                            "title": manga.get("title", "Unknown"),
                            "cover_url": manga.get("image", ""),
                            "author": manga.get("author", "Unknown"),
                            "latest_chapter": manga.get("chapter", ""),
                            "views": manga.get("views", 0),
                            "url": manga.get("url", ""),
                            "source": self.name
                        })
                    except Exception as e:
                        self.logger.error(f"Error parsing manga search result: {e}")
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching manga with Manga-API: {e}")
            return []

    def get_manga_details(self, manga_id: str) -> Dict[str, Any]:
        """Get details for a manga using Manga-API.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            The manga details.
        """
        endpoint = "/chapter-info"
        params = {
            "id": manga_id
        }
        
        try:
            data = self._make_request(endpoint, params)
            
            if not data:
                return {}
            
            # Extract chapters
            chapters = []
            if "chapters" in data:
                for chapter in data["chapters"]:
                    chapters.append({
                        "id": chapter.get("id", ""),
                        "title": chapter.get("title", ""),
                        "number": chapter.get("number", ""),
                        "date": chapter.get("date", ""),
                        "url": chapter.get("url", "")
                    })
            
            # Extract genres
            genres = []
            if "genres" in data:
                genres = data["genres"]
            
            # Extract alternative titles
            alt_titles = []
            if "alternativeTitles" in data:
                alt_titles = data["alternativeTitles"]
            
            return {
                "id": manga_id,
                "title": data.get("title", "Unknown"),
                "alternative_titles": alt_titles,
                "cover_url": data.get("image", ""),
                "author": data.get("author", "Unknown"),
                "status": data.get("status", "Unknown"),
                "description": data.get("description", ""),
                "genres": genres,
                "rating": str(data.get("rating", 0)),
                "chapters": chapters,
                "url": data.get("url", ""),
                "source": self.name
            }
        except Exception as e:
            self.logger.error(f"Error getting manga details with Manga-API: {e}")
            return {}

    def get_chapter_list(self, manga_id: str) -> List[Dict[str, Any]]:
        """Get the chapter list for a manga using Manga-API.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            A list of chapters.
        """
        # The chapter list is included in the manga details
        manga_details = self.get_manga_details(manga_id)
        
        if "chapters" in manga_details:
            return manga_details["chapters"]
        
        return []

    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter using Manga-API.
        
        Args:
            manga_id: The manga ID.
            chapter_id: The chapter ID.
            
        Returns:
            A list of image URLs.
        """
        endpoint = "/fetch-chapter"
        params = {
            "id": manga_id,
            "chapterID": chapter_id
        }
        
        try:
            data = self._make_request(endpoint, params)
            
            images = []
            if "images" in data:
                images = data["images"]
            
            return images
        except Exception as e:
            self.logger.error(f"Error getting chapter images with Manga-API: {e}")
            return []

    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest manga releases using Manga-API.
        
        Args:
            page: The page number.
            
        Returns:
            A list of latest releases.
        """
        endpoint = "/latest-release"
        
        try:
            data = self._make_request(endpoint)
            
            results = []
            if "mangas" in data:
                for manga in data["mangas"]:
                    try:
                        results.append({
                            "manga_id": manga.get("id", ""),
                            "manga_title": manga.get("title", "Unknown"),
                            "cover_url": manga.get("image", ""),
                            "chapter": manga.get("chapter", ""),
                            "url": manga.get("url", ""),
                            "source": self.name
                        })
                    except Exception as e:
                        self.logger.error(f"Error parsing latest release: {e}")
            
            return results
        except Exception as e:
            self.logger.error(f"Error getting latest releases with Manga-API: {e}")
            return []
