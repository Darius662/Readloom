#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MyAnimeList metadata provider.
"""

import json
import re
import time
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

from .base import MetadataProvider


class MyAnimeListProvider(MetadataProvider):
    """MyAnimeList metadata provider."""

    def __init__(self, enabled: bool = True, client_id: Optional[str] = None):
        """Initialize the MyAnimeList provider.
        
        Args:
            enabled: Whether the provider is enabled.
            client_id: The MyAnimeList API client ID.
        """
        super().__init__("MyAnimeList", enabled)
        self.base_url = "https://api.myanimelist.net/v2"
        self.client_id = client_id
        self.headers = {
            "X-MAL-CLIENT-ID": client_id if client_id else "",
            "User-Agent": "MangaArr/1.0.0",
            "Accept": "application/json"
        }
        self.session = requests.Session()

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the MyAnimeList API.
        
        Args:
            url: The URL to request.
            params: The query parameters.
            
        Returns:
            The JSON response.
        """
        if not self.client_id:
            self.logger.error("MyAnimeList client ID not set")
            return {}

        try:
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error making request to {url}: {e}")
            return {}

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for manga on MyAnimeList.
        
        Args:
            query: The search query.
            page: The page number.
            
        Returns:
            A list of manga search results.
        """
        if not self.client_id:
            self.logger.error("MyAnimeList client ID not set")
            return []

        limit = 10
        offset = (page - 1) * limit
        
        url = f"{self.base_url}/manga"
        params = {
            "q": query,
            "limit": limit,
            "offset": offset,
            "fields": "id,title,main_picture,alternative_titles,synopsis,mean,rank,popularity,num_list_users,num_volumes,num_chapters,authors{first_name,last_name},genres,status,media_type,start_date,end_date"
        }
        
        try:
            data = self._make_request(url, params)
            
            results = []
            if "data" in data:
                for item in data["data"]:
                    try:
                        node = item["node"]
                        
                        # Extract author names
                        authors = []
                        if "authors" in node:
                            for author in node["authors"]:
                                author_name = f"{author['node']['first_name']} {author['node']['last_name']}".strip()
                                authors.append(author_name)
                        
                        # Extract genres
                        genres = []
                        if "genres" in node:
                            for genre in node["genres"]:
                                genres.append(genre["name"])
                        
                        # Get cover URL
                        cover_url = ""
                        if "main_picture" in node and "large" in node["main_picture"]:
                            cover_url = node["main_picture"]["large"]
                        elif "main_picture" in node and "medium" in node["main_picture"]:
                            cover_url = node["main_picture"]["medium"]
                        
                        # Get alternative titles
                        alt_titles = []
                        if "alternative_titles" in node:
                            if "en" in node["alternative_titles"] and node["alternative_titles"]["en"]:
                                alt_titles.append(node["alternative_titles"]["en"])
                            if "ja" in node["alternative_titles"] and node["alternative_titles"]["ja"]:
                                alt_titles.append(node["alternative_titles"]["ja"])
                            if "synonyms" in node["alternative_titles"]:
                                alt_titles.extend(node["alternative_titles"]["synonyms"])
                        
                        results.append({
                            "id": str(node["id"]),
                            "title": node["title"],
                            "alternative_titles": alt_titles,
                            "cover_url": cover_url,
                            "author": ", ".join(authors),
                            "status": node.get("status", "Unknown"),
                            "description": node.get("synopsis", ""),
                            "genres": genres,
                            "rating": str(node.get("mean", 0)),
                            "volumes": node.get("num_volumes", 0),
                            "chapters": node.get("num_chapters", 0),
                            "url": f"https://myanimelist.net/manga/{node['id']}",
                            "source": self.name
                        })
                    except Exception as e:
                        self.logger.error(f"Error parsing manga item: {e}")
            
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
        if not self.client_id:
            self.logger.error("MyAnimeList client ID not set")
            return {}

        url = f"{self.base_url}/manga/{manga_id}"
        params = {
            "fields": "id,title,main_picture,alternative_titles,synopsis,mean,rank,popularity,num_list_users,num_volumes,num_chapters,authors{first_name,last_name},genres,status,media_type,start_date,end_date,related_manga,recommendations"
        }
        
        try:
            data = self._make_request(url, params)
            
            if not data:
                return {}
            
            # Extract author names
            authors = []
            if "authors" in data:
                for author in data["authors"]:
                    author_name = f"{author['node']['first_name']} {author['node']['last_name']}".strip()
                    authors.append(author_name)
            
            # Extract genres
            genres = []
            if "genres" in data:
                for genre in data["genres"]:
                    genres.append(genre["name"])
            
            # Get cover URL
            cover_url = ""
            if "main_picture" in data and "large" in data["main_picture"]:
                cover_url = data["main_picture"]["large"]
            elif "main_picture" in data and "medium" in data["main_picture"]:
                cover_url = data["main_picture"]["medium"]
            
            # Get alternative titles
            alt_titles = []
            if "alternative_titles" in data:
                if "en" in data["alternative_titles"] and data["alternative_titles"]["en"]:
                    alt_titles.append(data["alternative_titles"]["en"])
                if "ja" in data["alternative_titles"] and data["alternative_titles"]["ja"]:
                    alt_titles.append(data["alternative_titles"]["ja"])
                if "synonyms" in data["alternative_titles"]:
                    alt_titles.extend(data["alternative_titles"]["synonyms"])
            
            # Get related manga
            related_manga = []
            if "related_manga" in data:
                for manga in data["related_manga"]:
                    related_manga.append({
                        "id": str(manga["node"]["id"]),
                        "title": manga["node"]["title"],
                        "relation_type": manga["relation_type"],
                        "url": f"https://myanimelist.net/manga/{manga['node']['id']}"
                    })
            
            # Get recommendations
            recommendations = []
            if "recommendations" in data:
                for rec in data["recommendations"]:
                    recommendations.append({
                        "id": str(rec["node"]["id"]),
                        "title": rec["node"]["title"],
                        "url": f"https://myanimelist.net/manga/{rec['node']['id']}"
                    })
            
            return {
                "id": str(data["id"]),
                "title": data["title"],
                "alternative_titles": alt_titles,
                "cover_url": cover_url,
                "author": ", ".join(authors),
                "status": data.get("status", "Unknown"),
                "description": data.get("synopsis", ""),
                "genres": genres,
                "rating": str(data.get("mean", 0)),
                "rank": data.get("rank", 0),
                "popularity": data.get("popularity", 0),
                "volumes": data.get("num_volumes", 0),
                "chapters": data.get("num_chapters", 0),
                "start_date": data.get("start_date", ""),
                "end_date": data.get("end_date", ""),
                "media_type": data.get("media_type", ""),
                "related_manga": related_manga,
                "recommendations": recommendations,
                "url": f"https://myanimelist.net/manga/{data['id']}",
                "source": self.name
            }
        except Exception as e:
            self.logger.error(f"Error getting manga details on MyAnimeList: {e}")
            return {}

    def get_chapter_list(self, manga_id: str) -> List[Dict[str, Any]]:
        """Get the chapter list for a manga on MyAnimeList.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            A list of chapters.
        """
        # MyAnimeList API doesn't provide chapter lists
        # This is a limitation of the API
        self.logger.warning("MyAnimeList API doesn't provide chapter lists")
        return []

    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter on MyAnimeList.
        
        Args:
            manga_id: The manga ID.
            chapter_id: The chapter ID.
            
        Returns:
            A list of image URLs.
        """
        # MyAnimeList API doesn't provide chapter images
        # This is a limitation of the API
        self.logger.warning("MyAnimeList API doesn't provide chapter images")
        return []

    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest manga releases on MyAnimeList.
        
        Args:
            page: The page number.
            
        Returns:
            A list of latest releases.
        """
        # MyAnimeList API doesn't provide a direct way to get latest releases
        # We can use the seasonal manga endpoint as an approximation
        if not self.client_id:
            self.logger.error("MyAnimeList client ID not set")
            return []

        limit = 10
        offset = (page - 1) * limit
        
        url = f"{self.base_url}/manga/ranking"
        params = {
            "ranking_type": "bypopularity",
            "limit": limit,
            "offset": offset,
            "fields": "id,title,main_picture,alternative_titles,synopsis,mean,rank,popularity,num_volumes,num_chapters,authors{first_name,last_name},genres,status,media_type,start_date,end_date"
        }
        
        try:
            data = self._make_request(url, params)
            
            results = []
            if "data" in data:
                for item in data["data"]:
                    try:
                        node = item["node"]
                        
                        # Extract author names
                        authors = []
                        if "authors" in node:
                            for author in node["authors"]:
                                author_name = f"{author['node']['first_name']} {author['node']['last_name']}".strip()
                                authors.append(author_name)
                        
                        # Get cover URL
                        cover_url = ""
                        if "main_picture" in node and "large" in node["main_picture"]:
                            cover_url = node["main_picture"]["large"]
                        elif "main_picture" in node and "medium" in node["main_picture"]:
                            cover_url = node["main_picture"]["medium"]
                        
                        results.append({
                            "manga_id": str(node["id"]),
                            "manga_title": node["title"],
                            "cover_url": cover_url,
                            "author": ", ".join(authors),
                            "volumes": node.get("num_volumes", 0),
                            "chapters": node.get("num_chapters", 0),
                            "rating": str(node.get("mean", 0)),
                            "url": f"https://myanimelist.net/manga/{node['id']}",
                            "source": self.name
                        })
                    except Exception as e:
                        self.logger.error(f"Error parsing latest release item: {e}")
            
            return results
        except Exception as e:
            self.logger.error(f"Error getting latest releases on MyAnimeList: {e}")
            return []
