#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaFire metadata provider with debug logging.
"""

import json
import re
import time
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

from .base import MetadataProvider


class MangaFireDebugProvider(MetadataProvider):
    """MangaFire metadata provider with debug logging."""

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
            self.logger.info(f"Making request to {url} with params {params}")
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            self.logger.info(f"Request successful, status code: {response.status_code}")
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
            self.logger.info(f"Searching for '{query}' on page {page}")
            response = self._make_request(self.search_url, params)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Debug: Log the HTML structure
            self.logger.info(f"HTML response length: {len(response.text)}")
            self.logger.info(f"First 500 chars of HTML: {response.text[:500]}")
            
            results = []
            manga_items = soup.select('.manga-detail')
            self.logger.info(f"Found {len(manga_items)} manga items with selector '.manga-detail'")
            
            # If no manga items found, try alternative selectors
            if not manga_items:
                self.logger.info("Trying alternative selectors...")
                manga_items = soup.select('.manga-item')
                self.logger.info(f"Found {len(manga_items)} manga items with selector '.manga-item'")
                
                if not manga_items:
                    manga_items = soup.select('.manga')
                    self.logger.info(f"Found {len(manga_items)} manga items with selector '.manga'")
            
            for item in manga_items:
                try:
                    # Debug: Log the item HTML
                    self.logger.info(f"Processing manga item: {item}")
                    
                    title_elem = item.select_one('.manga-name a')
                    if not title_elem:
                        title_elem = item.select_one('.title a')
                    if not title_elem:
                        title_elem = item.select_one('a')
                    
                    title = title_elem.text.strip() if title_elem else "Unknown"
                    self.logger.info(f"Found manga title: {title}")
                    
                    manga_url = title_elem['href'] if title_elem and 'href' in title_elem.attrs else ""
                    manga_id = manga_url.split('/')[-1] if manga_url else ""
                    
                    cover_elem = item.select_one('.manga-poster img')
                    if not cover_elem:
                        cover_elem = item.select_one('.cover img')
                    if not cover_elem:
                        cover_elem = item.select_one('img')
                        
                    cover_url = cover_elem['src'] if cover_elem and 'src' in cover_elem.attrs else ""
                    
                    author_elem = item.select_one('.manga-author')
                    if not author_elem:
                        author_elem = item.select_one('.author')
                    author = author_elem.text.strip() if author_elem else "Unknown"
                    
                    status_elem = item.select_one('.manga-status')
                    if not status_elem:
                        status_elem = item.select_one('.status')
                    status = status_elem.text.strip() if status_elem else "Unknown"
                    
                    latest_chapter_elem = item.select_one('.chapter-name')
                    if not latest_chapter_elem:
                        latest_chapter_elem = item.select_one('.latest-chapter')
                    latest_chapter = latest_chapter_elem.text.strip() if latest_chapter_elem else "Unknown"
                    
                    manga_data = {
                        "id": manga_id,
                        "title": title,
                        "cover_url": cover_url,
                        "author": author,
                        "status": status,
                        "latest_chapter": latest_chapter,
                        "url": f"{self.base_url}{manga_url}",
                        "source": self.name
                    }
                    
                    self.logger.info(f"Adding manga to results: {manga_data}")
                    results.append(manga_data)
                except Exception as e:
                    self.logger.error(f"Error parsing manga item: {e}")
            
            self.logger.info(f"Returning {len(results)} search results")
            return results
        except Exception as e:
            self.logger.error(f"Error searching manga on MangaFire: {e}")
            return []
