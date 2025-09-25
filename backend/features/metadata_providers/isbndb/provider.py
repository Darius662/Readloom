#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ISBNdb metadata provider implementation.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

import requests

from ..base import MetadataProvider


class ISBNdbProvider(MetadataProvider):
    """ISBNdb metadata provider."""

    def __init__(self, enabled: bool = True, api_key: str = ""):
        """Initialize the ISBNdb provider.
        
        Args:
            enabled: Whether the provider is enabled.
            api_key: API key for ISBNdb API (required).
        """
        super().__init__("ISBNdb", enabled)
        self.base_url = "https://api2.isbndb.com"
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Readloom/1.0.0"
        }
        
        # Add API key to headers if provided
        if self.api_key:
            self.headers["Authorization"] = self.api_key
            
        self.session = requests.Session()

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for books on ISBNdb.
        
        Args:
            query: The search query.
            page: The page number (1-indexed).
            
        Returns:
            A list of book search results.
        """
        results: List[Dict[str, Any]] = []
        
        # Check if API key is available
        if not self.api_key:
            self.logger.error("ISBNdb API key is required")
            return results
            
        try:
            # Build the API URL
            url = f"{self.base_url}/books/{query}"
            params = {
                "page": page,
                "pageSize": 10
            }
                
            # Make the request
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if "books" not in data:
                return results
                
            for item in data["books"]:
                # Extract authors
                authors = item.get("authors", [])
                author = ", ".join(authors) if authors else "Unknown"
                
                # Extract cover URL
                cover_url = item.get("image", "")
                
                # Extract status
                status = "Unknown"
                if "date_published" in item:
                    status = "COMPLETED"  # Most books on ISBNdb are completed
                
                # Extract description
                description = item.get("synopsis", "")
                if not description:
                    description = item.get("overview", "")
                
                # Extract genres/subjects
                genres = item.get("subjects", [])
                
                # Extract publisher
                publisher = item.get("publisher", "")
                
                # Extract ISBN
                isbn = item.get("isbn13", item.get("isbn", ""))
                
                # Extract published date
                published_date = item.get("date_published", "")
                
                result = {
                    "id": isbn,  # Use ISBN as ID
                    "title": item.get("title", ""),
                    "alternative_titles": [],
                    "cover_url": cover_url,
                    "author": author,
                    "status": status,
                    "description": description,
                    "genres": genres,
                    "rating": "0",  # ISBNdb doesn't provide ratings
                    "volumes": 1,  # Most books are single volumes
                    "chapters": 0,  # ISBNdb doesn't provide chapter info
                    "url": f"https://isbndb.com/book/{isbn}",
                    "source": self.name,
                    "isbn": isbn,
                    "published_date": published_date,
                    "publisher": publisher
                }
                
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Error searching ISBNdb API: {e}")
        
        return results

    def get_manga_details(self, manga_id: str) -> Dict[str, Any]:
        """Get details for a book on ISBNdb.
        
        Args:
            manga_id: The book ID (ISBN).
            
        Returns:
            The book details.
        """
        # Check if API key is available
        if not self.api_key:
            self.logger.error("ISBNdb API key is required")
            return {}
            
        try:
            # Build the API URL
            url = f"{self.base_url}/book/{manga_id}"
                
            # Make the request
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            item = response.json()["book"]
            
            # Extract authors
            authors = item.get("authors", [])
            author = ", ".join(authors) if authors else "Unknown"
            
            # Extract cover URL
            cover_url = item.get("image", "")
            
            # Extract status
            status = "Unknown"
            if "date_published" in item:
                status = "COMPLETED"  # Most books on ISBNdb are completed
            
            # Extract description
            description = item.get("synopsis", "")
            if not description:
                description = item.get("overview", "")
            
            # Extract genres/subjects
            genres = item.get("subjects", [])
            
            # Extract publisher
            publisher = item.get("publisher", "")
            
            # Extract ISBN
            isbn = item.get("isbn13", item.get("isbn", ""))
            
            # Extract published date
            published_date = item.get("date_published", "")
            
            # Extract dimensions and pages
            dimensions = item.get("dimensions", "")
            pages = 0
            if "pages" in item:
                try:
                    pages = int(item["pages"])
                except (ValueError, TypeError):
                    pass
            
            # Create a single volume entry
            volumes_list = []
            if published_date:
                volumes_list.append({
                    "number": "1",
                    "title": item.get("title", ""),
                    "description": description,
                    "cover_url": cover_url,
                    "release_date": published_date
                })
            
            return {
                "id": isbn,
                "title": item.get("title", ""),
                "alternative_titles": [],
                "cover_url": cover_url,
                "author": author,
                "status": status,
                "description": description,
                "genres": genres,
                "rating": "0",  # ISBNdb doesn't provide ratings
                "volumes": 1,  # Most books are single volumes
                "chapters": 0,  # ISBNdb doesn't provide chapter info
                "url": f"https://isbndb.com/book/{isbn}",
                "source": self.name,
                "isbn": isbn,
                "published_date": published_date,
                "publisher": publisher,
                "dimensions": dimensions,
                "page_count": pages,
                "volumes": volumes_list
            }
            
        except Exception as e:
            self.logger.error(f"Error getting book details from ISBNdb API: {e}")
        
        return {}

    def get_chapter_list(self, manga_id: str) -> List[Dict[str, Any]]:
        """Get the chapter list for a book on ISBNdb.
        
        Note: ISBNdb API doesn't provide chapter information,
        so we return an empty list.
        
        Args:
            manga_id: The book ID.
            
        Returns:
            An empty list as ISBNdb doesn't provide chapter information.
        """
        return {"chapters": []}

    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter on ISBNdb.
        
        Note: ISBNdb API doesn't provide chapter images,
        so we return an empty list.
        
        Args:
            manga_id: The book ID.
            chapter_id: The chapter ID.
            
        Returns:
            An empty list as ISBNdb doesn't provide chapter images.
        """
        return []

    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest book releases on ISBNdb.
        
        Args:
            page: The page number.
            
        Returns:
            A list of latest releases.
        """
        results: List[Dict[str, Any]] = []
        
        # Check if API key is available
        if not self.api_key:
            self.logger.error("ISBNdb API key is required")
            return results
            
        try:
            # Build the API URL for recent publications
            # ISBNdb doesn't have a direct "latest releases" endpoint,
            # so we search for comics and graphic novels
            url = f"{self.base_url}/books/comics"
            params = {
                "page": page,
                "pageSize": 10
            }
                
            # Make the request
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if "books" not in data:
                return results
                
            for item in data["books"]:
                # Extract authors
                authors = item.get("authors", [])
                author = ", ".join(authors) if authors else "Unknown"
                
                # Extract cover URL
                cover_url = item.get("image", "")
                
                # Extract ISBN
                isbn = item.get("isbn13", item.get("isbn", ""))
                
                # Extract published date
                published_date = item.get("date_published", "")
                
                result = {
                    "manga_id": isbn,
                    "manga_title": item.get("title", ""),
                    "cover_url": cover_url,
                    "author": author,
                    "volumes": 1,
                    "chapters": 0,
                    "rating": "0",  # ISBNdb doesn't provide ratings
                    "url": f"https://isbndb.com/book/{isbn}",
                    "source": self.name,
                    "published_date": published_date
                }
                
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Error getting latest releases from ISBNdb API: {e}")
        
        return results
