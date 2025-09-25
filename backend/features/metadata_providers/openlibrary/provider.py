#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Open Library metadata provider implementation.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

import requests

from ..base import MetadataProvider


class OpenLibraryProvider(MetadataProvider):
    """Open Library metadata provider."""

    def __init__(self, enabled: bool = True):
        """Initialize the Open Library provider.
        
        Args:
            enabled: Whether the provider is enabled.
        """
        super().__init__("OpenLibrary", enabled)
        self.base_url = "https://openlibrary.org"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Readloom/1.0.0",
        }
        self.session = requests.Session()

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for books on Open Library.
        
        Args:
            query: The search query.
            page: The page number (1-indexed).
            
        Returns:
            A list of book search results.
        """
        results: List[Dict[str, Any]] = []
        try:
            # Open Library API uses offset instead of page
            offset = (page - 1) * 10
            
            # Build the API URL
            url = f"{self.base_url}/search.json"
            
            # Try different search approaches for better results
            search_attempts = [
                # Attempt 1: Direct search with query
                {"q": query, "offset": offset, "limit": 10},
                
                # Attempt 2: Search with title field
                {"title": query, "offset": offset, "limit": 10},
                
                # Attempt 3: Search with author field if query might contain author
                {"author": query, "offset": offset, "limit": 10},
                
                # Attempt 4: Search with subject field for comics/manga
                {"q": query, "subject": "comics,graphic novels,manga", "offset": offset, "limit": 10}
            ]
            
            # Try each search approach until we get results
            data = {"docs": []}
            for params in search_attempts:
                self.logger.info(f"Searching OpenLibrary with params: {params}")
                response = self.session.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                if "docs" in data and len(data["docs"]) > 0:
                    self.logger.info(f"Found {len(data['docs'])} results with params: {params}")
                    break
            
            if "docs" not in data or len(data["docs"]) == 0:
                # Final attempt: Use the works API directly
                works_url = f"{self.base_url}/search/works.json"
                params = {"q": query, "offset": offset, "limit": 10}
                self.logger.info(f"Searching OpenLibrary works API with query: {query}")
                response = self.session.get(works_url, params=params, headers=self.headers)
                if response.ok:
                    data = response.json()
                    
            if "docs" not in data:
                return results
                
            for item in data["docs"]:
                # Extract authors
                authors = item.get("author_name", [])
                author = ", ".join(authors) if authors else "Unknown"
                
                # Extract cover URL
                cover_url = ""
                if "cover_i" in item:
                    cover_id = item["cover_i"]
                    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                
                # Extract status
                status = "Unknown"
                if "publish_date" in item:
                    status = "COMPLETED"  # Most books on Open Library are completed
                
                # Extract alternative titles
                alt_titles = item.get("other_titles", [])
                
                # Extract description
                description = item.get("description", "")
                if isinstance(description, dict):
                    description = description.get("value", "")
                
                # Extract genres/subjects
                genres = []
                for subject_field in ["subject", "subject_facet"]:
                    if subject_field in item:
                        genres.extend(item[subject_field])
                
                # Limit to a reasonable number of genres
                genres = list(set(genres))[:10]
                
                # Extract key for ID
                key = item.get("key", "")
                if key.startswith("/works/"):
                    key = key[7:]  # Remove "/works/" prefix
                
                # Extract ISBN
                isbn = ""
                if "isbn" in item and item["isbn"]:
                    isbn = item["isbn"][0]
                
                result = {
                    "id": key,
                    "title": item.get("title", ""),
                    "alternative_titles": alt_titles,
                    "cover_url": cover_url,
                    "author": author,
                    "status": status,
                    "description": description,
                    "genres": genres,
                    "rating": "0",  # Open Library doesn't provide ratings
                    "volumes": 1,  # Most books are single volumes
                    "chapters": 0,  # Open Library doesn't provide chapter info
                    "url": f"{self.base_url}{item.get('key', '')}",
                    "source": self.name,
                    "isbn": isbn,
                    "published_date": item.get("publish_date", [""])[0] if isinstance(item.get("publish_date"), list) else item.get("publish_date", ""),
                    "publisher": ", ".join(item.get("publisher", [])) if isinstance(item.get("publisher"), list) else item.get("publisher", "")
                }
                
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Error searching Open Library API: {e}")
        
        return results

    def get_manga_details(self, manga_id: str) -> Dict[str, Any]:
        """Get details for a book on Open Library.
        
        Args:
            manga_id: The book ID.
            
        Returns:
            The book details.
        """
        try:
            # Check if manga_id is a work ID or an edition ID
            if manga_id.startswith('OL') and manga_id.endswith('W'):
                # It's a work ID
                work_id = manga_id
                url = f"{self.base_url}/works/{work_id}.json"
            elif manga_id.startswith('OL') and manga_id.endswith('M'):
                # It's an edition ID
                edition_id = manga_id
                url = f"{self.base_url}/books/{edition_id}.json"
                edition_response = self.session.get(url, headers=self.headers)
                if not edition_response.ok:
                    return {}
                edition_data = edition_response.json()
                if "works" in edition_data and len(edition_data["works"]) > 0:
                    work_key = edition_data["works"][0]["key"]
                    if work_key.startswith("/works/"):
                        work_id = work_key[7:]  # Remove "/works/" prefix
                        url = f"{self.base_url}/works/{work_id}.json"
                    else:
                        work_id = work_key
                        url = f"{self.base_url}{work_key}.json"
                else:
                    # No work reference, use edition data directly
                    return self._process_edition_data(edition_data, None)
            else:
                # Assume it's a work ID
                work_id = manga_id
                url = f"{self.base_url}/works/{work_id}.json"
                
            # Make the request for work details
            self.logger.info(f"Fetching work details from: {url}")
            response = self.session.get(url, headers=self.headers)
            if not response.ok:
                self.logger.warning(f"Failed to fetch work details: {response.status_code}")
                return {}
                
            work_data = response.json()
            
            # Get the best edition
            edition_data = {}
            edition_keys = []
            
            # Check for editions in work data
            if "editions" in work_data:
                edition_keys = work_data["editions"]
            else:
                # Try to find editions through search
                search_url = f"{self.base_url}/search.json"
                params = {"works": work_id, "limit": 5}
                search_response = self.session.get(search_url, params=params, headers=self.headers)
                if search_response.ok and "docs" in search_response.json():
                    docs = search_response.json()["docs"]
                    for doc in docs:
                        if "edition_key" in doc:
                            edition_keys.extend([key for key in doc["edition_key"]])
            
            # Get details for the first available edition
            for edition_key in edition_keys[:3]:  # Try up to 3 editions
                edition_url = f"{self.base_url}/books/{edition_key}.json"
                self.logger.info(f"Fetching edition details from: {edition_url}")
                edition_response = self.session.get(edition_url, headers=self.headers)
                if edition_response.ok:
                    edition_data = edition_response.json()
                    # Check if this edition has cover image
                    if "covers" in edition_data and edition_data["covers"]:
                        break  # Found a good edition with cover
            
            return self._process_work_data(work_data, edition_data, manga_id)
            
        except Exception as e:
            self.logger.error(f"Error getting book details from Open Library API: {e}")
        
        return {}
    
    def _process_work_data(self, work_data: Dict[str, Any], edition_data: Dict[str, Any], manga_id: str) -> Dict[str, Any]:
        """Process work data to extract book details.
        
        Args:
            work_data: The work data from Open Library API.
            edition_data: The edition data from Open Library API.
            manga_id: The book ID.
            
        Returns:
            The processed book details.
        """
        # Extract title
        title = work_data.get("title", "")
        
        # Extract authors
        authors = []
        if "authors" in work_data:
            for author_ref in work_data["authors"]:
                if "author" in author_ref:
                    author_key = author_ref["author"]["key"]
                    author_url = f"{self.base_url}{author_key}.json"
                    author_response = self.session.get(author_url, headers=self.headers)
                    if author_response.ok:
                        author_data = author_response.json()
                        authors.append(author_data.get("name", "Unknown"))
        
        author = ", ".join(authors) if authors else "Unknown"
        
        # Extract cover URL
        cover_url = ""
        # First try edition covers (usually better quality)
        if edition_data and "covers" in edition_data and edition_data["covers"]:
            cover_id = edition_data["covers"][0]
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
        # Fall back to work covers
        elif "covers" in work_data and work_data["covers"]:
            cover_id = work_data["covers"][0]
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
        
        # Extract status
        status = "Unknown"
        if "first_publish_date" in work_data:
            status = "COMPLETED"  # Most books on Open Library are completed
        
        # Extract alternative titles
        alt_titles = []
        if "other_titles" in work_data:
            alt_titles.extend(work_data["other_titles"])
        
        # Extract description
        description = work_data.get("description", "")
        if isinstance(description, dict):
            description = description.get("value", "")
        
        # Extract genres/subjects
        genres = []
        for subject_field in ["subjects", "subject_places", "subject_times", "subject_people"]:
            if subject_field in work_data:
                genres.extend(work_data[subject_field])
        
        # Limit to a reasonable number of genres
        genres = list(set(genres))[:10]
        
        # Extract ISBN
        isbn = ""
        if edition_data:
            for isbn_field in ["isbn_13", "isbn_10", "isbn"]:
                if isbn_field in edition_data and edition_data[isbn_field]:
                    if isinstance(edition_data[isbn_field], list):
                        isbn = edition_data[isbn_field][0]
                    else:
                        isbn = edition_data[isbn_field]
                    break
        
        # Extract published date
        published_date = work_data.get("first_publish_date", "")
        
        # Extract publisher
        publisher = ""
        if edition_data and "publishers" in edition_data:
            if isinstance(edition_data["publishers"], list):
                publisher = ", ".join(edition_data["publishers"])
            else:
                publisher = str(edition_data["publishers"])
        
        # Create a single volume entry
        volumes_list = []
        if published_date:
            volumes_list.append({
                "number": "1",
                "title": title,
                "description": description,
                "cover_url": cover_url,
                "release_date": published_date
            })
        
        # Get page count
        page_count = 0
        if edition_data:
            if "number_of_pages" in edition_data:
                try:
                    page_count = int(edition_data["number_of_pages"])
                except (ValueError, TypeError):
                    pass
            elif "pagination" in edition_data:
                pagination = edition_data["pagination"]
                if isinstance(pagination, str):
                    # Try to extract page count from pagination string
                    match = re.search(r'(\d+)\s*p', pagination)
                    if match:
                        try:
                            page_count = int(match.group(1))
                        except (ValueError, TypeError):
                            pass
        
        return {
            "id": manga_id,
            "title": title,
            "alternative_titles": alt_titles,
            "cover_url": cover_url,
            "author": author,
            "status": status,
            "description": description,
            "genres": genres,
            "rating": "0",  # Open Library doesn't provide ratings
            "volumes": 1,  # Most books are single volumes
            "chapters": 0,  # Open Library doesn't provide chapter info
            "url": f"{self.base_url}/works/{manga_id}",
            "source": self.name,
            "isbn": isbn,
            "published_date": published_date,
            "publisher": publisher,
            "page_count": page_count,
            "volumes": volumes_list
        }
    
    def _process_edition_data(self, edition_data: Dict[str, Any], work_id: Optional[str]) -> Dict[str, Any]:
        """Process edition data when work data is not available.
        
        Args:
            edition_data: The edition data from Open Library API.
            work_id: The work ID if available.
            
        Returns:
            The processed book details.
        """
        # Extract title
        title = edition_data.get("title", "")
        
        # Extract authors
        authors = []
        if "authors" in edition_data:
            for author_ref in edition_data["authors"]:
                if "key" in author_ref:
                    author_key = author_ref["key"]
                    author_url = f"{self.base_url}{author_key}.json"
                    author_response = self.session.get(author_url, headers=self.headers)
                    if author_response.ok:
                        author_data = author_response.json()
                        authors.append(author_data.get("name", "Unknown"))
        
        author = ", ".join(authors) if authors else "Unknown"
        
        # Extract cover URL
        cover_url = ""
        if "covers" in edition_data and edition_data["covers"]:
            cover_id = edition_data["covers"][0]
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
        
        # Extract status
        status = "Unknown"
        if "publish_date" in edition_data:
            status = "COMPLETED"  # Most books on Open Library are completed
        
        # Extract description
        description = edition_data.get("description", "")
        if isinstance(description, dict):
            description = description.get("value", "")
        
        # Extract genres/subjects
        genres = []
        if "subjects" in edition_data:
            genres.extend(edition_data["subjects"])
        
        # Limit to a reasonable number of genres
        genres = list(set(genres))[:10]
        
        # Extract ISBN
        isbn = ""
        for isbn_field in ["isbn_13", "isbn_10", "isbn"]:
            if isbn_field in edition_data and edition_data[isbn_field]:
                if isinstance(edition_data[isbn_field], list):
                    isbn = edition_data[isbn_field][0]
                else:
                    isbn = edition_data[isbn_field]
                break
        
        # Extract published date
        published_date = edition_data.get("publish_date", "")
        
        # Extract publisher
        publisher = ""
        if "publishers" in edition_data:
            if isinstance(edition_data["publishers"], list):
                publisher = ", ".join(edition_data["publishers"])
            else:
                publisher = str(edition_data["publishers"])
        
        # Create a single volume entry
        volumes_list = []
        if published_date:
            volumes_list.append({
                "number": "1",
                "title": title,
                "description": description,
                "cover_url": cover_url,
                "release_date": published_date
            })
        
        # Get page count
        page_count = 0
        if "number_of_pages" in edition_data:
            try:
                page_count = int(edition_data["number_of_pages"])
            except (ValueError, TypeError):
                pass
        elif "pagination" in edition_data:
            pagination = edition_data["pagination"]
            if isinstance(pagination, str):
                # Try to extract page count from pagination string
                match = re.search(r'(\d+)\s*p', pagination)
                if match:
                    try:
                        page_count = int(match.group(1))
                    except (ValueError, TypeError):
                        pass
        
        # Use edition ID as manga_id if work_id is not available
        manga_id = work_id if work_id else edition_data.get("key", "").split("/")[-1]
        
        return {
            "id": manga_id,
            "title": title,
            "alternative_titles": [],
            "cover_url": cover_url,
            "author": author,
            "status": status,
            "description": description,
            "genres": genres,
            "rating": "0",  # Open Library doesn't provide ratings
            "volumes": 1,  # Most books are single volumes
            "chapters": 0,  # Open Library doesn't provide chapter info
            "url": f"{self.base_url}/books/{edition_data.get('key', '').split('/')[-1]}",
            "source": self.name,
            "isbn": isbn,
            "published_date": published_date,
            "publisher": publisher,
            "page_count": page_count,
            "volumes": volumes_list
        }

    def get_chapter_list(self, manga_id: str) -> List[Dict[str, Any]]:
        """Get the chapter list for a book on Open Library.
        
        Note: Open Library API doesn't provide chapter information,
        so we return an empty list.
        
        Args:
            manga_id: The book ID.
            
        Returns:
            An empty list as Open Library doesn't provide chapter information.
        """
        return {"chapters": []}

    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter on Open Library.
        
        Note: Open Library API doesn't provide chapter images,
        so we return an empty list.
        
        Args:
            manga_id: The book ID.
            chapter_id: The chapter ID.
            
        Returns:
            An empty list as Open Library doesn't provide chapter images.
        """
        return []

    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest book releases on Open Library.
        
        Args:
            page: The page number.
            
        Returns:
            A list of latest releases.
        """
        results: List[Dict[str, Any]] = []
        try:
            # Open Library API uses offset instead of page
            offset = (page - 1) * 10
            
            # Try different approaches to get latest releases
            search_attempts = [
                # Attempt 1: Comics and graphic novels sorted by new
                {
                    "q": "subject:(comics OR graphic novels OR manga)",
                    "offset": offset,
                    "limit": 10,
                    "sort": "new"
                },
                
                # Attempt 2: Recent publications with comic/manga subjects
                {
                    "subject": "comics,graphic novels,manga",
                    "offset": offset,
                    "limit": 10,
                    "sort": "new"
                },
                
                # Attempt 3: General search for manga
                {
                    "q": "manga",
                    "offset": offset,
                    "limit": 10,
                    "sort": "new"
                },
                
                # Attempt 4: General search for comics
                {
                    "q": "comics",
                    "offset": offset,
                    "limit": 10,
                    "sort": "new"
                }
            ]
            
            # Try each approach until we get results
            data = {"docs": []}
            url = f"{self.base_url}/search.json"
            
            for params in search_attempts:
                self.logger.info(f"Searching OpenLibrary latest releases with params: {params}")
                response = self.session.get(url, params=params, headers=self.headers)
                if not response.ok:
                    continue
                    
                data = response.json()
                if "docs" in data and len(data["docs"]) > 0:
                    self.logger.info(f"Found {len(data['docs'])} latest releases with params: {params}")
                    break
            
            if "docs" not in data or len(data["docs"]) == 0:
                # Final attempt: Try trending works
                trending_url = f"{self.base_url}/trending.json"
                self.logger.info("Trying OpenLibrary trending API")
                response = self.session.get(trending_url, headers=self.headers)
                if response.ok:
                    trending_data = response.json()
                    if "works" in trending_data and trending_data["works"]:
                        # Convert trending format to docs format
                        data = {"docs": []}
                        for work in trending_data["works"][:10]:
                            if "key" in work:
                                # Fetch work details
                                work_key = work["key"].split("/")[-1]
                                work_url = f"{self.base_url}/works/{work_key}.json"
                                work_response = self.session.get(work_url, headers=self.headers)
                                if work_response.ok:
                                    work_data = work_response.json()
                                    data["docs"].append(work_data)
            
            if "docs" not in data:                
                return results
                
            for item in data["docs"]:
                # Extract authors
                authors = item.get("author_name", [])
                author = ", ".join(authors) if authors else "Unknown"
                
                # Extract cover URL
                cover_url = ""
                if "cover_i" in item:
                    cover_id = item["cover_i"]
                    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                
                # Extract key for ID
                key = item.get("key", "")
                if key.startswith("/works/"):
                    key = key[7:]  # Remove "/works/" prefix
                
                result = {
                    "manga_id": key,
                    "manga_title": item.get("title", ""),
                    "cover_url": cover_url,
                    "author": author,
                    "volumes": 1,
                    "chapters": 0,
                    "rating": "0",  # Open Library doesn't provide ratings
                    "url": f"{self.base_url}{item.get('key', '')}",
                    "source": self.name,
                    "published_date": item.get("publish_date", [""])[0] if isinstance(item.get("publish_date"), list) else item.get("publish_date", "")
                }
                
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Error getting latest releases from Open Library API: {e}")
        
        return results
