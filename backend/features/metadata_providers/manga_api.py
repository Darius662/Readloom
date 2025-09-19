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
        endpoint = "/api/search/"
        params = {
            "query": query
        }
        
        try:
            data = self._make_request(endpoint, params)
            
            results = []
            # The API returns a list of manga directly
            if isinstance(data, list):
                for manga in data:
                    try:
                        manga_endpoint = manga.get("manga_endpoint", "")
                        # Remove trailing slash if present
                        if manga_endpoint.endswith("/"):
                            manga_endpoint = manga_endpoint[:-1]
                            
                        results.append({
                            "id": manga_endpoint,
                            "title": manga.get("title", "Unknown"),
                            "cover_url": manga.get("image", ""),
                            "type": manga.get("type", "Unknown"),
                            "latest_chapter": manga.get("chapter", ""),
                            "rating": manga.get("rating", "0"),
                            "source": self.name
                        })
                    except Exception as e:
                        self.logger.error(f"Error parsing manga search result: {e}")
            
            # If no results found, try to get latest updates as a fallback
            if not results:
                self.logger.info(f"No search results found for '{query}', using latest updates as fallback")
                latest_results = self.get_latest_releases(page)
                
                # Filter latest results to find anything that might match the query
                query_lower = query.lower()
                for manga in latest_results:
                    if query_lower in manga.get("manga_title", "").lower():
                        results.append({
                            "id": manga.get("manga_id", ""),
                            "title": manga.get("manga_title", "Unknown"),
                            "cover_url": manga.get("cover_url", ""),
                            "type": manga.get("type", "Unknown"),
                            "latest_chapter": manga.get("chapter", ""),
                            "rating": "0",
                            "source": self.name
                        })
            
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
        # The manga_id is actually the manga_endpoint from search results
        endpoint = f"/api/manga/{manga_id}"
        
        try:
            data = self._make_request(endpoint)
            
            if not data:
                return {}
            
            # Extract chapters
            chapters = []
            if "chapter_list" in data:
                for chapter in data["chapter_list"]:
                    chapter_endpoint = chapter.get("chapter_endpoint", "")
                    # Remove trailing slash if present
                    if chapter_endpoint.endswith("/"):
                        chapter_endpoint = chapter_endpoint[:-1]
                        
                    chapters.append({
                        "id": chapter_endpoint,
                        "title": chapter.get("chapter_name", ""),
                        "number": chapter.get("chapter_name", "").replace("Ch.", "").strip(),
                        "date": chapter.get("updated_on", ""),
                        "url": f"{self.api_url}/api/chapter/{chapter_endpoint}"
                    })
            
            # Extract genres
            genres = []
            if "genre_list" in data:
                genres = data["genre_list"]
            
            return {
                "id": manga_id,
                "title": data.get("title", "Unknown"),
                "alternative_titles": data.get("alter_title", []),
                "cover_url": data.get("image", ""),
                "author": data.get("author", "Unknown"),
                "status": data.get("status", "Unknown"),
                "description": data.get("synopsis", ""),
                "genres": genres,
                "rating": data.get("rating", "0"),
                "chapters": chapters,
                "type": data.get("type", "Unknown"),
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
        # The chapter_id is actually the chapter_endpoint from manga details
        endpoint = f"/api/chapter/{chapter_id}"
        
        try:
            data = self._make_request(endpoint)
            
            images = []
            if "chapter_image" in data:
                images = data["chapter_image"]
            
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
        endpoint = f"/api/latest_update/{page}"
        
        try:
            data = self._make_request(endpoint)
            
            results = []
            if "latestUpdateList" in data:
                for manga in data["latestUpdateList"]:
                    try:
                        manga_endpoint = manga.get("manga_endpoint", "")
                        # Remove trailing slash if present
                        if manga_endpoint.endswith("/"):
                            manga_endpoint = manga_endpoint[:-1]
                            
                        # Get the latest chapter info
                        latest_chapter = ""
                        if "listNewChapter" in manga and len(manga["listNewChapter"]) > 0:
                            latest_chapter = manga["listNewChapter"][0].get("chapterName", "")
                            
                        results.append({
                            "manga_id": manga_endpoint,
                            "manga_title": manga.get("title", "Unknown"),
                            "cover_url": manga.get("image", ""),
                            "chapter": latest_chapter,
                            "type": manga.get("type", "Unknown"),
                            "hot_tag": manga.get("hotTag", ""),
                            "source": self.name
                        })
                    except Exception as e:
                        self.logger.error(f"Error parsing latest release: {e}")
            
            return results
        except Exception as e:
            self.logger.error(f"Error getting latest releases with Manga-API: {e}")
            return []
