#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Books metadata provider implementation.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

import requests

from ..base import MetadataProvider


class GoogleBooksProvider(MetadataProvider):
    """Google Books metadata provider."""

    def __init__(self, enabled: bool = True, api_key: str = ""):
        """Initialize the Google Books provider.
        
        Args:
            enabled: Whether the provider is enabled.
            api_key: Optional API key for Google Books API.
        """
        super().__init__("GoogleBooks", enabled)
        self.base_url = "https://www.googleapis.com/books/v1"
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Readloom/1.0.0",
        }
        self.session = requests.Session()

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for books on Google Books API.
        
        Args:
            query: The search query.
            page: The page number (1-indexed).
            
        Returns:
            A list of book search results.
        """
        results: List[Dict[str, Any]] = []
        try:
            # Google Books API uses startIndex (0-indexed) instead of page
            start_index = (page - 1) * 10
            
            # Build the API URL
            url = f"{self.base_url}/volumes"
            params = {
                "q": query,
                "startIndex": start_index,
                "maxResults": 10,
                "printType": "books"
            }
            
            # Add API key if available
            if self.api_key:
                params["key"] = self.api_key
                
            # Make the request
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if "items" not in data:
                return results
                
            for item in data["items"]:
                volume_info = item.get("volumeInfo", {})
                
                # Extract authors
                authors = volume_info.get("authors", [])
                author = ", ".join(authors) if authors else "Unknown"
                
                # Extract cover URL
                cover_url = ""
                if "imageLinks" in volume_info:
                    cover_url = volume_info["imageLinks"].get("thumbnail", "")
                    # Convert to HTTPS if needed
                    if cover_url.startswith("http://"):
                        cover_url = "https" + cover_url[4:]
                
                # Extract status
                status = "Unknown"
                if "publishedDate" in volume_info:
                    status = "COMPLETED"  # Most books on Google Books are completed
                
                # Extract alternative titles
                alt_titles = []
                if "subtitle" in volume_info and volume_info["subtitle"]:
                    alt_titles.append(volume_info["subtitle"])
                
                # Extract description
                description = volume_info.get("description", "")
                # Clean up HTML tags
                description = re.sub(r'<[^>]+>', '', description)
                
                # Extract genres
                genres = volume_info.get("categories", [])
                
                # Extract rating
                rating = "0"
                if "averageRating" in volume_info:
                    rating = str(volume_info["averageRating"])
                
                result = {
                    "id": item.get("id", ""),
                    "title": volume_info.get("title", ""),
                    "alternative_titles": alt_titles,
                    "cover_url": cover_url,
                    "author": author,
                    "status": status,
                    "description": description,
                    "genres": genres,
                    "rating": rating,
                    "volumes": 1,  # Most books are single volumes
                    "chapters": 0,  # Google Books doesn't provide chapter info
                    "url": volume_info.get("infoLink", f"https://books.google.com/books?id={item.get('id')}"),
                    "source": self.name,
                    "isbn": volume_info.get("industryIdentifiers", [{}])[0].get("identifier", ""),
                    "published_date": volume_info.get("publishedDate", ""),
                    "publisher": volume_info.get("publisher", "")
                }
                
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Error searching Google Books API: {e}")
        
        return results

    def get_manga_details(self, manga_id: str) -> Dict[str, Any]:
        """Get details for a book on Google Books.
        
        Args:
            manga_id: The book ID.
            
        Returns:
            The book details.
        """
        try:
            url = f"{self.base_url}/volumes/{manga_id}"
            params = {}
            
            # Add API key if available
            if self.api_key:
                params["key"] = self.api_key
                
            # Make the request
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            item = response.json()
            
            volume_info = item.get("volumeInfo", {})
            
            # Extract authors
            authors = volume_info.get("authors", [])
            author = ", ".join(authors) if authors else "Unknown"
            
            # Extract cover URL
            cover_url = ""
            if "imageLinks" in volume_info:
                # Try to get the highest quality image available
                for img_type in ["extraLarge", "large", "medium", "thumbnail"]:
                    if img_type in volume_info["imageLinks"]:
                        cover_url = volume_info["imageLinks"][img_type]
                        # Convert to HTTPS if needed
                        if cover_url.startswith("http://"):
                            cover_url = "https" + cover_url[4:]
                        break
            
            # Extract status
            status = "Unknown"
            if "publishedDate" in volume_info:
                status = "COMPLETED"  # Most books on Google Books are completed
            
            # Extract alternative titles
            alt_titles = []
            if "subtitle" in volume_info and volume_info["subtitle"]:
                alt_titles.append(volume_info["subtitle"])
            
            # Extract description
            description = volume_info.get("description", "")
            # Clean up HTML tags
            description = re.sub(r'<[^>]+>', '', description)
            
            # Extract genres
            genres = volume_info.get("categories", [])
            
            # Extract rating
            rating = "0"
            if "averageRating" in volume_info:
                rating = str(volume_info["averageRating"])
            
            # Extract ISBNs
            isbns = []
            for identifier in volume_info.get("industryIdentifiers", []):
                if identifier.get("type") in ["ISBN_10", "ISBN_13"]:
                    isbns.append(identifier.get("identifier", ""))
            
            # Create a single volume entry
            volumes_list = []
            if "publishedDate" in volume_info:
                volumes_list.append({
                    "number": "1",
                    "title": volume_info.get("title", ""),
                    "description": description,
                    "cover_url": cover_url,
                    "release_date": volume_info.get("publishedDate", "")
                })
            
            return {
                "id": item.get("id", ""),
                "title": volume_info.get("title", ""),
                "alternative_titles": alt_titles,
                "cover_url": cover_url,
                "author": author,
                "status": status,
                "description": description,
                "genres": genres,
                "rating": rating,
                "volumes": 1,  # Most books are single volumes
                "chapters": 0,  # Google Books doesn't provide chapter info
                "url": volume_info.get("infoLink", f"https://books.google.com/books?id={item.get('id')}"),
                "source": self.name,
                "isbn": ", ".join(isbns),
                "published_date": volume_info.get("publishedDate", ""),
                "publisher": volume_info.get("publisher", ""),
                "page_count": volume_info.get("pageCount", 0),
                "volumes": volumes_list
            }
            
        except Exception as e:
            self.logger.error(f"Error getting book details from Google Books API: {e}")
        
        return {}

    def get_chapter_list(self, manga_id: str) -> List[Dict[str, Any]]:
        """Get the chapter list for a book on Google Books.
        
        Note: Google Books API doesn't provide chapter information,
        so we return an empty list.
        
        Args:
            manga_id: The book ID.
            
        Returns:
            An empty list as Google Books doesn't provide chapter information.
        """
        return {"chapters": []}

    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter on Google Books.
        
        Note: Google Books API doesn't provide chapter images,
        so we return an empty list.
        
        Args:
            manga_id: The book ID.
            chapter_id: The chapter ID.
            
        Returns:
            An empty list as Google Books doesn't provide chapter images.
        """
        return []

    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest book releases on Google Books.
        
        Args:
            page: The page number.
            
        Returns:
            A list of latest releases.
        """
        results: List[Dict[str, Any]] = []
        try:
            # Google Books API uses startIndex (0-indexed) instead of page
            start_index = (page - 1) * 10
            
            # Build the API URL for recent publications
            url = f"{self.base_url}/volumes"
            
            # Get books published in the last year
            current_year = datetime.now().year
            
            params = {
                "q": f"inpublisher:manga OR comics OR graphic novel",
                "startIndex": start_index,
                "maxResults": 10,
                "printType": "books",
                "orderBy": "newest"
            }
            
            # Add API key if available
            if self.api_key:
                params["key"] = self.api_key
                
            # Make the request
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if "items" not in data:
                return results
                
            for item in data["items"]:
                volume_info = item.get("volumeInfo", {})
                
                # Extract authors
                authors = volume_info.get("authors", [])
                author = ", ".join(authors) if authors else "Unknown"
                
                # Extract cover URL
                cover_url = ""
                if "imageLinks" in volume_info:
                    cover_url = volume_info["imageLinks"].get("thumbnail", "")
                    # Convert to HTTPS if needed
                    if cover_url.startswith("http://"):
                        cover_url = "https" + cover_url[4:]
                
                # Extract rating
                rating = "0"
                if "averageRating" in volume_info:
                    rating = str(volume_info["averageRating"])
                
                result = {
                    "manga_id": item.get("id", ""),
                    "manga_title": volume_info.get("title", ""),
                    "cover_url": cover_url,
                    "author": author,
                    "volumes": 1,
                    "chapters": 0,
                    "rating": rating,
                    "url": volume_info.get("infoLink", f"https://books.google.com/books?id={item.get('id')}"),
                    "source": self.name,
                    "published_date": volume_info.get("publishedDate", "")
                }
                
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Error getting latest releases from Google Books API: {e}")
        
        return results
