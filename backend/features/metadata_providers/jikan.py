#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Jikan API metadata provider for MyAnimeList.
Documentation: https://docs.api.jikan.moe/
"""

import time
from datetime import datetime, timedelta
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
            # Unfortunately, Jikan/MAL doesn't provide detailed chapter lists
            # We'll create a better approximation based on manga details
            data = self._make_request(f"{self.base_url}/manga/{manga_id}/full")
            
            chapters = []
            start_date = None
            end_date = None
            publishing_status = "finished"
            
            if "data" in data:
                item = data["data"]
                chapter_count = item.get("chapters", 0)
                
                # Get publication dates and status
                if "published" in item:
                    if "from" in item["published"] and item["published"]["from"]:
                        start_date = item["published"]["from"].split("T")[0]
                    if "to" in item["published"] and item["published"]["to"]:
                        end_date = item["published"]["to"].split("T")[0]
                
                # Get the publishing status
                publishing_status = item.get("status", "finished").lower()
                
                if chapter_count:
                    # If we have both start and end dates and a chapter count, we can estimate release dates
                    if start_date and end_date and publishing_status == "finished" and chapter_count > 1:
                        try:
                            # Calculate an estimated interval between releases
                            start = datetime.strptime(start_date, "%Y-%m-%d")
                            end = datetime.strptime(end_date, "%Y-%m-%d")
                            days_between = (end - start).days
                            interval = max(1, days_between // (chapter_count - 1))  # At least 1 day between chapters
                            
                            for i in range(1, chapter_count + 1):
                                # For first chapter, use start_date
                                # For last chapter, use end_date
                                # For others, interpolate dates between
                                if i == 1:
                                    chapter_date = start_date
                                elif i == chapter_count:
                                    chapter_date = end_date
                                else:
                                    # Calculate an estimated date for this chapter
                                    estimated_date = start + timedelta(days=interval * (i-1))
                                    chapter_date = estimated_date.strftime("%Y-%m-%d")
                                
                                chapters.append({
                                    "id": f"{manga_id}_{i}",
                                    "title": f"Chapter {i}",
                                    "number": str(i),
                                    "date": chapter_date,
                                    "url": f"{self.mal_url}/{manga_id}",
                                    "manga_id": manga_id
                                })
                        except Exception as date_error:
                            self.logger.warning(f"Error calculating chapter dates: {date_error}")
                            # Fall back to simpler method if date calculation fails
                            self._add_simple_chapters(chapters, manga_id, chapter_count, start_date, end_date)
                    else:
                        # Simpler method without date interpolation
                        self._add_simple_chapters(chapters, manga_id, chapter_count, start_date, end_date)
                elif start_date:  # No chapter count but we have a start date
                    # If no chapter count, create at least one chapter with the release date
                    chapters.append({
                        "id": f"{manga_id}_1",
                        "title": "Chapter 1",
                        "number": "1",
                        "date": start_date,
                        "url": f"{self.mal_url}/{manga_id}",
                        "manga_id": manga_id
                    })
                else:  # No chapter count, no dates
                    chapters.append({
                        "id": f"{manga_id}_1",
                        "title": "Chapter 1",
                        "number": "1",
                        "date": datetime.now().strftime("%Y-%m-%d"),  # Use current date
                        "url": f"{self.mal_url}/{manga_id}",
                        "manga_id": manga_id
                    })
            
            return {"chapters": chapters}
        except Exception as e:
            self.logger.error(f"Error getting chapter list on MyAnimeList: {e}")
            return {"chapters": [], "error": str(e)}
    
    def _add_simple_chapters(self, chapters, manga_id, chapter_count, start_date, end_date):
        """Add chapters with simple date assignment logic.
        
        Args:
            chapters: The list to add chapters to
            manga_id: The manga ID
            chapter_count: Number of chapters
            start_date: Publication start date
            end_date: Publication end date
        """
        # If we have publishing dates but can't interpolate, assign logically
        for i in range(1, chapter_count + 1):
            if i == 1 and start_date:
                chapter_date = start_date
            elif i == chapter_count and end_date:
                chapter_date = end_date
            elif start_date:  # For middle chapters, use start_date if available
                chapter_date = start_date
            else:  # No dates available
                chapter_date = datetime.now().strftime("%Y-%m-%d")  # Use current date as fallback
            
            chapters.append({
                "id": f"{manga_id}_{i}",
                "title": f"Chapter {i}",
                "number": str(i),
                "date": chapter_date,
                "url": f"{self.mal_url}/{manga_id}",
                "manga_id": manga_id
            })

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
            data = self._make_request(f"{self.base_url}/manga", params)
            
            results = []
            if "data" in data:
                for item in data["data"]:
                    try:
                        manga_id = item["mal_id"]
                        manga_title = item["title"]
                        
                        # Get cover art
                        cover_url = item.get("images", {}).get("jpg", {}).get("large_image_url", "")
                        
                        # For ongoing manga, try to estimate the most recent chapter release date
                        release_date = ""
                        
                        # First try to get date from publishing info
                        if item.get("published", {}).get("from"):
                            # Use from date as base date
                            start_date_str = item["published"]["from"].split("T")[0]
                            
                            try:
                                # For ongoing manga, estimate the most recent release
                                # Use the start date and assume biweekly releases up to current date
                                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                                today = datetime.now()
                                days_since_start = (today - start_date).days
                                
                                # Assume biweekly releases (14 days)
                                chapter_count = days_since_start // 14
                                if chapter_count > 0:
                                    # Estimate the latest chapter release date
                                    latest_release = start_date + timedelta(days=14 * chapter_count)
                                    # If this would be in the future, use today's date
                                    if latest_release > today:
                                        latest_release = today
                                    release_date = latest_release.strftime("%Y-%m-%d")
                                else:
                                    release_date = start_date_str
                            except Exception as date_err:
                                self.logger.warning(f"Error calculating release date: {date_err}")
                                release_date = start_date_str  # Fall back to start date
                        else:
                            # No publication date, use today's date for ongoing manga
                            release_date = datetime.now().strftime("%Y-%m-%d")
                        
                        results.append({
                            "manga_id": str(manga_id),
                            "manga_title": manga_title,
                            "cover_url": cover_url,
                            "chapter": f"Latest Chapter",
                            "chapter_id": f"{manga_id}_latest",
                            "date": release_date,  # Always include a date
                            "url": f"{self.mal_url}/{manga_id}",
                            "source": self.name
                        })
                    except Exception as e:
                        self.logger.error(f"Error parsing latest release item: {e}")
            
            return results
        except Exception as e:
            self.logger.error(f"Error getting latest releases on MyAnimeList: {e}")
            return []
