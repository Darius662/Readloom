#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Jikan API metadata provider for MyAnimeList.
Documentation: https://docs.api.jikan.moe/
"""

import time
from typing import Dict, List, Any, Optional
import requests
from urllib.parse import quote

from .base import MetadataProvider


class JikanProvider(MetadataProvider):
    """Jikan API metadata provider for MyAnimeList."""

    def __init__(self, enabled: bool = True):
        """Initialize the Jikan provider.
        
        Args:
            enabled: Whether the provider is enabled.
        """
        super().__init__("MyAnimeList", enabled)
        self.base_url = "https://api.jikan.moe/v4"
        self.mal_url = "https://myanimelist.net/manga"
        self.headers = {
            "User-Agent": "MangaArr/1.0.0",
            "Accept": "application/json"
        }
        self.session = requests.Session()
        # Jikan API has a rate limit of 3 requests per second
        self.rate_limit_delay = 0.4  # seconds

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the Jikan API.
        
        Args:
            url: The URL to request.
            params: The query parameters.
            
        Returns:
            The JSON response.
        """
        try:
            self.logger.info(f"Making request to {url} with params {params}")
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            self.logger.info(f"Request successful, status code: {response.status_code}")
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error making request to {url}: {e}")
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
            data = self._make_request(f"{self.base_url}/manga", params)
            
            results = []
            if "data" in data:
                for item in data["data"]:
                    try:
                        manga_id = item["mal_id"]
                        title = item["title"]
                        
                        # Get cover art
                        cover_url = item.get("images", {}).get("jpg", {}).get("large_image_url", "")
                        
                        # Get author
                        authors = []
                        for author in item.get("authors", []):
                            authors.append(author.get("name", ""))
                        author = ", ".join(authors) if authors else "Unknown"
                        
                        # Get status
                        status = item.get("status", "Unknown").upper()
                        
                        # Get description
                        description = item.get("synopsis", "")
                        
                        # Get genres
                        genres = []
                        for genre in item.get("genres", []):
                            genres.append(genre.get("name", ""))
                        
                        # Get rating
                        rating = str(item.get("score", 0))
                        
                        manga_data = {
                            "id": str(manga_id),
                            "title": title,
                            "cover_url": cover_url,
                            "author": author,
                            "status": status,
                            "description": description,
                            "genres": genres,
                            "rating": rating,
                            "url": f"{self.mal_url}/{manga_id}",
                            "source": self.name
                        }
                        
                        results.append(manga_data)
                    except Exception as e:
                        self.logger.error(f"Error parsing manga item: {e}")
            
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
            data = self._make_request(f"{self.base_url}/manga/{manga_id}/full")
            
            if "data" not in data:
                return {}
            
            item = data["data"]
            
            # Get title
            title = item["title"]
            
            # Get alternative titles
            alt_titles = []
            if "titles" in item:
                for title_obj in item["titles"]:
                    if title_obj.get("type") != "Default":
                        alt_titles.append(title_obj.get("title", ""))
            
            # Get cover art
            cover_url = item.get("images", {}).get("jpg", {}).get("large_image_url", "")
            
            # Get author
            authors = []
            for author in item.get("authors", []):
                authors.append(author.get("name", ""))
            author = ", ".join(authors) if authors else "Unknown"
            
            # Get status
            status = item.get("status", "Unknown").upper()
            
            # Get description
            description = item.get("synopsis", "")
            
            # Get genres
            genres = []
            for genre in item.get("genres", []):
                genres.append(genre.get("name", ""))
            
            # Get rating
            rating = str(item.get("score", 0))
            
            # Get volumes
            volumes = []
            volume_count = item.get("volumes", 0)
            if volume_count:
                for i in range(1, volume_count + 1):
                    volumes.append({
                        "number": str(i),
                        "title": f"Volume {i}"
                    })
            
            return {
                "id": str(manga_id),
                "title": title,
                "alternative_titles": alt_titles,
                "cover_url": cover_url,
                "author": author,
                "status": status,
                "description": description,
                "genres": genres,
                "rating": rating,
                "volumes": volumes,
                "url": f"{self.mal_url}/{manga_id}",
                "source": self.name
            }
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
            # Unfortunately, Jikan/MAL doesn't provide chapter lists
            # We'll create a placeholder based on the manga details
            data = self._make_request(f"{self.base_url}/manga/{manga_id}")
            
            chapters = []
            release_date = None
            
            if "data" in data:
                item = data["data"]
                chapter_count = item.get("chapters", 0)
                
                # Try to get the release date from the published info
                if "published" in item and "from" in item["published"] and item["published"]["from"]:
                    release_date = item["published"]["from"].split("T")[0]
                
                if chapter_count:
                    for i in range(1, chapter_count + 1):
                        # For the latest chapter, use the release date if available
                        chapter_date = release_date if i == chapter_count else ""
                        
                        chapters.append({
                            "id": f"{manga_id}_{i}",
                            "title": f"Chapter {i}",
                            "number": str(i),
                            "date": chapter_date,
                            "url": f"{self.mal_url}/{manga_id}",
                            "manga_id": manga_id
                        })
                else:
                    # If no chapter count, create at least one chapter with the release date
                    chapters.append({
                        "id": f"{manga_id}_1",
                        "title": "Chapter 1",
                        "number": "1",
                        "date": release_date or "",
                        "url": f"{self.mal_url}/{manga_id}",
                        "manga_id": manga_id
                    })
            
            return {"chapters": chapters}
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
        params = {
            "page": page,
            "limit": 20,
            "order_by": "start_date",
            "sort": "desc",
            "type": "manga",
            "status": "publishing"
        }
        
        try:
            data = self._make_request(f"{self.base_url}/manga", params)
            
            results = []
            if "data" in data:
                for item in data["data"]:
                    try:
                        manga_id = item["mal_id"]
                        manga_title = item["title"]
                        
                        # Get cover art
                        cover_url = item.get("images", {}).get("jpg", {}).get("large_image_url", "")
                        
                        # Get date
                        date = item.get("published", {}).get("from", "").split("T")[0] if item.get("published", {}).get("from") else ""
                        
                        results.append({
                            "manga_id": str(manga_id),
                            "manga_title": manga_title,
                            "cover_url": cover_url,
                            "chapter": "Latest",
                            "chapter_id": f"{manga_id}_latest",
                            "date": date,
                            "url": f"{self.mal_url}/{manga_id}",
                            "source": self.name
                        })
                    except Exception as e:
                        self.logger.error(f"Error parsing latest release item: {e}")
            
            return results
        except Exception as e:
            self.logger.error(f"Error getting latest releases on MyAnimeList: {e}")
            return []
