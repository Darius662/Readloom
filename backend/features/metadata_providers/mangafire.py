#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaFire metadata provider.
"""

import json
import re
import time
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

from .base import MetadataProvider


class MangaFireProvider(MetadataProvider):
    """MangaFire metadata provider."""

    def __init__(self, enabled: bool = True):
        """Initialize the MangaFire provider.
        
        Args:
            enabled: Whether the provider is enabled.
        """
        super().__init__("MangaFire", enabled)
        self.base_url = "https://mangafire.to"
        self.search_url = f"{self.base_url}/filter"
        self.manga_url = f"{self.base_url}/manga"
        self.latest_url = f"{self.base_url}/latest"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": self.base_url,
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        self.session = requests.Session()

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a request to the MangaFire API.
        
        Args:
            url: The URL to request.
            params: The query parameters.
            
        Returns:
            The response.
        """
        try:
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f"Error making request to {url}: {e}")
            raise

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
            response = self._make_request(self.search_url, params)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            manga_items = soup.select('.manga-detail')
            
            for item in manga_items:
                try:
                    title_elem = item.select_one('.manga-name a')
                    title = title_elem.text.strip() if title_elem else "Unknown"
                    
                    manga_url = title_elem['href'] if title_elem and 'href' in title_elem.attrs else ""
                    manga_id = manga_url.split('/')[-1] if manga_url else ""
                    
                    cover_elem = item.select_one('.manga-poster img')
                    cover_url = cover_elem['src'] if cover_elem and 'src' in cover_elem.attrs else ""
                    
                    author_elem = item.select_one('.manga-author')
                    author = author_elem.text.strip() if author_elem else "Unknown"
                    
                    status_elem = item.select_one('.manga-status')
                    status = status_elem.text.strip() if status_elem else "Unknown"
                    
                    latest_chapter_elem = item.select_one('.chapter-name')
                    latest_chapter = latest_chapter_elem.text.strip() if latest_chapter_elem else "Unknown"
                    
                    results.append({
                        "id": manga_id,
                        "title": title,
                        "cover_url": cover_url,
                        "author": author,
                        "status": status,
                        "latest_chapter": latest_chapter,
                        "url": f"{self.base_url}{manga_url}",
                        "source": self.name
                    })
                except Exception as e:
                    self.logger.error(f"Error parsing manga item: {e}")
            
            return results
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
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title_elem = soup.select_one('.manga-name h1')
            title = title_elem.text.strip() if title_elem else "Unknown"
            
            cover_elem = soup.select_one('.manga-poster img')
            cover_url = cover_elem['src'] if cover_elem and 'src' in cover_elem.attrs else ""
            
            author_elem = soup.select_one('.manga-author a')
            author = author_elem.text.strip() if author_elem else "Unknown"
            
            status_elem = soup.select_one('.manga-status')
            status = status_elem.text.strip() if status_elem else "Unknown"
            
            description_elem = soup.select_one('.manga-description')
            description = description_elem.text.strip() if description_elem else ""
            
            genres = []
            genre_elems = soup.select('.manga-genres a')
            for genre_elem in genre_elems:
                genres.append(genre_elem.text.strip())
            
            # Get alternative titles
            alt_titles = []
            alt_titles_elem = soup.select_one('.manga-alt-name')
            if alt_titles_elem:
                alt_titles_text = alt_titles_elem.text.strip()
                if alt_titles_text:
                    alt_titles = [title.strip() for title in alt_titles_text.split(';')]
            
            # Get rating
            rating = "0.0"
            rating_elem = soup.select_one('.manga-rating .rating-num')
            if rating_elem:
                rating = rating_elem.text.strip()
            
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
                "url": url,
                "source": self.name
            }
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
            soup = BeautifulSoup(response.text, 'html.parser')
            
            chapters = []
            chapter_items = soup.select('.chapter-item')
            
            for item in chapter_items:
                try:
                    chapter_elem = item.select_one('.chapter-name')
                    chapter_title = chapter_elem.text.strip() if chapter_elem else "Unknown"
                    
                    chapter_url = chapter_elem['href'] if chapter_elem and 'href' in chapter_elem.attrs else ""
                    chapter_id = chapter_url.split('/')[-1] if chapter_url else ""
                    
                    chapter_number_match = re.search(r'Chapter (\d+(\.\d+)?)', chapter_title)
                    chapter_number = chapter_number_match.group(1) if chapter_number_match else "0"
                    
                    date_elem = item.select_one('.chapter-time')
                    date = date_elem.text.strip() if date_elem else "Unknown"
                    
                    chapters.append({
                        "id": chapter_id,
                        "title": chapter_title,
                        "number": chapter_number,
                        "date": date,
                        "url": f"{self.base_url}{chapter_url}",
                        "manga_id": manga_id
                    })
                except Exception as e:
                    self.logger.error(f"Error parsing chapter item: {e}")
            
            return chapters
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
            soup = BeautifulSoup(response.text, 'html.parser')
            
            images = []
            image_items = soup.select('.chapter-images img')
            
            for item in image_items:
                if 'src' in item.attrs:
                    images.append(item['src'])
            
            return images
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
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            manga_items = soup.select('.manga-item')
            
            for item in manga_items:
                try:
                    title_elem = item.select_one('.manga-name a')
                    title = title_elem.text.strip() if title_elem else "Unknown"
                    
                    manga_url = title_elem['href'] if title_elem and 'href' in title_elem.attrs else ""
                    manga_id = manga_url.split('/')[-1] if manga_url else ""
                    
                    cover_elem = item.select_one('.manga-poster img')
                    cover_url = cover_elem['src'] if cover_elem and 'src' in cover_elem.attrs else ""
                    
                    chapter_elem = item.select_one('.chapter-name')
                    chapter = chapter_elem.text.strip() if chapter_elem else "Unknown"
                    
                    chapter_url = chapter_elem['href'] if chapter_elem and 'href' in chapter_elem.attrs else ""
                    chapter_id = chapter_url.split('/')[-1] if chapter_url else ""
                    
                    date_elem = item.select_one('.chapter-time')
                    date = date_elem.text.strip() if date_elem else "Unknown"
                    
                    results.append({
                        "manga_id": manga_id,
                        "manga_title": title,
                        "cover_url": cover_url,
                        "chapter": chapter,
                        "chapter_id": chapter_id,
                        "date": date,
                        "url": f"{self.base_url}{chapter_url}",
                        "source": self.name
                    })
                except Exception as e:
                    self.logger.error(f"Error parsing latest release item: {e}")
            
            return results
        except Exception as e:
            self.logger.error(f"Error getting latest releases on MangaFire: {e}")
            return []
