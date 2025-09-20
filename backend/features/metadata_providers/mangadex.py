#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaDex API metadata provider.
Documentation: https://api.mangadex.org/docs/
"""

import time
from typing import Dict, List, Any, Optional
import requests
from urllib.parse import quote

from .base import MetadataProvider


class MangaDexProvider(MetadataProvider):
    """MangaDex API metadata provider."""

    def __init__(self, enabled: bool = True):
        """Initialize the MangaDex provider.
        
        Args:
            enabled: Whether the provider is enabled.
        """
        super().__init__("MangaDex", enabled)
        self.base_url = "https://api.mangadex.org"
        self.manga_url = "https://mangadex.org/title"
        self.chapter_url = "https://mangadex.org/chapter"
        self.headers = {
            "User-Agent": "MangaArr/1.0.0",
            "Accept": "application/json"
        }
        self.session = requests.Session()

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the MangaDex API.
        
        Args:
            url: The URL to request.
            params: The query parameters.
            
        Returns:
            The JSON response.
        """
        try:
            self.logger.info(f"Making request to {url} with params {params}")
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            self.logger.info(f"Request successful, status code: {response.status_code}")
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error making request to {url}: {e}")
            raise

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for manga on MangaDex.
        
        Args:
            query: The search query.
            page: The page number.
            
        Returns:
            A list of manga search results.
        """
        limit = 20
        offset = (page - 1) * limit
        
        params = {
            "title": query,
            "limit": limit,
            "offset": offset,
            "includes[]": ["cover_art", "author"]
        }
        
        try:
            self.logger.info(f"Searching for '{query}' on page {page}")
            data = self._make_request(f"{self.base_url}/manga", params)
            
            results = []
            if "data" in data:
                for item in data["data"]:
                    try:
                        manga_id = item["id"]
                        attributes = item["attributes"]
                        title = attributes["title"].get("en") or next(iter(attributes["title"].values()))
                        
                        # Get cover art
                        cover_url = ""
                        if "relationships" in item:
                            for rel in item["relationships"]:
                                if rel["type"] == "cover_art" and "attributes" in rel:
                                    filename = rel["attributes"].get("fileName", "")
                                    if filename:
                                        cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{filename}.512.jpg"
                        
                        # Get author
                        author = "Unknown"
                        if "relationships" in item:
                            for rel in item["relationships"]:
                                if rel["type"] == "author" and "attributes" in rel:
                                    author = rel["attributes"].get("name", "Unknown")
                        
                        # Get status
                        status = attributes.get("status", "Unknown").upper()
                        
                        # Get description
                        description = attributes.get("description", {}).get("en", "")
                        
                        manga_data = {
                            "id": manga_id,
                            "title": title,
                            "cover_url": cover_url,
                            "author": author,
                            "status": status,
                            "description": description,
                            "url": f"{self.manga_url}/{manga_id}",
                            "source": self.name
                        }
                        
                        results.append(manga_data)
                    except Exception as e:
                        self.logger.error(f"Error parsing manga item: {e}")
            
            self.logger.info(f"Returning {len(results)} search results")
            return results
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
            params = {
                "includes[]": ["cover_art", "author", "artist", "tag"]
            }
            
            data = self._make_request(f"{self.base_url}/manga/{manga_id}", params)
            
            if "data" not in data:
                return {}
            
            item = data["data"]
            attributes = item["attributes"]
            
            # Get title
            title = attributes["title"].get("en") or next(iter(attributes["title"].values()))
            
            # Get alternative titles
            alt_titles = []
            for alt_title in attributes.get("altTitles", []):
                for lang, title_text in alt_title.items():
                    alt_titles.append(title_text)
            
            # Get cover art
            cover_url = ""
            if "relationships" in item:
                for rel in item["relationships"]:
                    if rel["type"] == "cover_art" and "attributes" in rel:
                        filename = rel["attributes"].get("fileName", "")
                        if filename:
                            cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{filename}.512.jpg"
            
            # Get author
            author = "Unknown"
            if "relationships" in item:
                for rel in item["relationships"]:
                    if rel["type"] == "author" and "attributes" in rel:
                        author = rel["attributes"].get("name", "Unknown")
            
            # Get status
            status = attributes.get("status", "Unknown").upper()
            
            # Get description
            description = attributes.get("description", {}).get("en", "")
            
            # Get genres
            genres = []
            if "tags" in attributes:
                for tag in attributes["tags"]:
                    if tag["attributes"]["group"] == "genre":
                        genres.append(tag["attributes"]["name"]["en"])
            
            # Get rating
            rating = "0.0"
            if "statistics" in data and "rating" in data["statistics"]:
                rating_data = data["statistics"]["rating"]
                if "average" in rating_data:
                    rating = str(round(rating_data["average"], 1))
            
            return {
                "id": manga_id,
                "title": title,
                "alternative_titles": alt_titles,
                "cover_url": cover_url,
                "author": author,
                "status": status,
                "description": description,
                "genres": genres,
                "rating": rating,
                "url": f"{self.manga_url}/{manga_id}",
                "source": self.name
            }
        except Exception as e:
            self.logger.error(f"Error getting manga details on MangaDex: {e}")
            return {}

    def get_chapter_list(self, manga_id: str) -> Dict[str, Any]:
        """Get the chapter list for a manga on MangaDex.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            A dictionary containing chapters and other information.
        """
        try:
            params = {
                "manga": manga_id,
                "translatedLanguage[]": ["en"],
                "limit": 100,
                "order[chapter]": "desc"
            }
            
            data = self._make_request(f"{self.base_url}/chapter", params)
            
            chapters = []
            if "data" in data:
                for item in data["data"]:
                    try:
                        chapter_id = item["id"]
                        attributes = item["attributes"]
                        
                        # Get chapter number
                        chapter_number = attributes.get("chapter", "0")
                        
                        # Get title
                        title = attributes.get("title", f"Chapter {chapter_number}")
                        if not title:
                            title = f"Chapter {chapter_number}"
                        
                        # Get date
                        date = attributes.get("publishAt", "")
                        if date:
                            date = date.split("T")[0]  # Format: YYYY-MM-DD
                        
                        chapters.append({
                            "id": chapter_id,
                            "title": title,
                            "number": chapter_number,
                            "date": date,
                            "url": f"{self.chapter_url}/{chapter_id}",
                            "manga_id": manga_id
                        })
                    except Exception as e:
                        self.logger.error(f"Error parsing chapter item: {e}")
            
            return {"chapters": chapters}
        except Exception as e:
            self.logger.error(f"Error getting chapter list on MangaDex: {e}")
            return {"chapters": [], "error": str(e)}

    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter on MangaDex.
        
        Args:
            manga_id: The manga ID.
            chapter_id: The chapter ID.
            
        Returns:
            A list of image URLs.
        """
        try:
            # Get chapter data
            data = self._make_request(f"{self.base_url}/at-home/server/{chapter_id}")
            
            if "baseUrl" not in data or "chapter" not in data:
                return []
            
            base_url = data["baseUrl"]
            chapter_hash = data["chapter"]["hash"]
            image_files = data["chapter"]["data"]
            
            # Construct image URLs
            image_urls = []
            for filename in image_files:
                image_url = f"{base_url}/data/{chapter_hash}/{filename}"
                image_urls.append(image_url)
            
            return image_urls
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
        limit = 20
        offset = (page - 1) * limit
        
        params = {
            "limit": limit,
            "offset": offset,
            "translatedLanguage[]": ["en"],
            "includes[]": ["manga", "cover_art"],
            "order[publishAt]": "desc"
        }
        
        try:
            data = self._make_request(f"{self.base_url}/chapter", params)
            
            results = []
            if "data" in data:
                for item in data["data"]:
                    try:
                        chapter_id = item["id"]
                        attributes = item["attributes"]
                        
                        # Get chapter number
                        chapter_number = attributes.get("chapter", "0")
                        
                        # Get title
                        chapter_title = attributes.get("title", f"Chapter {chapter_number}")
                        if not chapter_title:
                            chapter_title = f"Chapter {chapter_number}"
                        
                        # Get date
                        date = attributes.get("publishAt", "")
                        if date:
                            date = date.split("T")[0]  # Format: YYYY-MM-DD
                        
                        # Get manga data
                        manga_id = ""
                        manga_title = "Unknown"
                        cover_url = ""
                        
                        if "relationships" in item:
                            for rel in item["relationships"]:
                                if rel["type"] == "manga":
                                    manga_id = rel["id"]
                                    if "attributes" in rel:
                                        titles = rel["attributes"].get("title", {})
                                        manga_title = titles.get("en") or next(iter(titles.values()), "Unknown")
                                elif rel["type"] == "cover_art" and "attributes" in rel:
                                    filename = rel["attributes"].get("fileName", "")
                                    if filename and manga_id:
                                        cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{filename}.512.jpg"
                        
                        results.append({
                            "manga_id": manga_id,
                            "manga_title": manga_title,
                            "cover_url": cover_url,
                            "chapter": chapter_title,
                            "chapter_id": chapter_id,
                            "date": date,
                            "url": f"{self.chapter_url}/{chapter_id}",
                            "source": self.name
                        })
                    except Exception as e:
                        self.logger.error(f"Error parsing latest release item: {e}")
            
            return results
        except Exception as e:
            self.logger.error(f"Error getting latest releases on MangaDex: {e}")
            return []
