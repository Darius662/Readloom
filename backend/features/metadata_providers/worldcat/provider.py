#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WorldCat metadata provider implementation.
"""

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from urllib.parse import quote_plus

import requests

from ..base import MetadataProvider


class WorldCatProvider(MetadataProvider):
    """WorldCat metadata provider."""

    def __init__(self, enabled: bool = True, api_key: str = ""):
        """Initialize the WorldCat provider.
        
        Args:
            enabled: Whether the provider is enabled.
            api_key: API key for WorldCat API (required).
        """
        super().__init__("WorldCat", enabled)
        self.base_url = "https://www.worldcat.org/webservices/catalog/search/opensearch"
        self.api_key = api_key
        self.headers = {
            "Accept": "application/atom+xml",
            "User-Agent": "Readloom/1.0.0",
        }
        self.session = requests.Session()
        
        # Define namespaces for XML parsing
        self.namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
            'content': 'http://purl.org/rss/1.0/modules/content/'
        }

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for books on WorldCat.
        
        Args:
            query: The search query.
            page: The page number (1-indexed).
            
        Returns:
            A list of book search results.
        """
        results: List[Dict[str, Any]] = []
        
        # Check if API key is available
        if not self.api_key:
            self.logger.error("WorldCat API key is required")
            return results
            
        try:
            # Build the API URL
            url = f"{self.base_url}"
            params = {
                "q": query,
                "wskey": self.api_key,
                "start": (page - 1) * 10 + 1,  # WorldCat uses 1-indexed start parameter
                "count": 10,
                "format": "atom"
            }
                
            # Make the request
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Process entries
            entries = root.findall('.//atom:entry', self.namespaces)
            
            for entry in entries:
                # Extract book ID from the ID field (last part of the URL)
                id_elem = entry.find('./atom:id', self.namespaces)
                book_id = id_elem.text.split('/')[-1] if id_elem is not None and id_elem.text else ""
                
                # Extract title
                title_elem = entry.find('./atom:title', self.namespaces)
                title = title_elem.text if title_elem is not None and title_elem.text else "Unknown Title"
                
                # Extract authors
                authors = []
                author_elems = entry.findall('./atom:author/atom:name', self.namespaces)
                for author_elem in author_elems:
                    if author_elem.text:
                        authors.append(author_elem.text)
                
                # Extract description
                summary_elem = entry.find('./atom:summary', self.namespaces)
                description = summary_elem.text if summary_elem is not None and summary_elem.text else ""
                
                # Extract cover URL
                cover_url = ""
                link_elems = entry.findall('./atom:link', self.namespaces)
                for link in link_elems:
                    rel = link.get('rel')
                    if rel == 'icon' or rel == 'http://www.w3.org/2005/Atom/icon':
                        cover_url = link.get('href', '')
                        break
                
                # Extract publication date
                pub_date = ""
                date_elem = entry.find('./dc:date', self.namespaces)
                if date_elem is not None and date_elem.text:
                    pub_date = date_elem.text
                
                # Extract publisher
                publisher = ""
                publisher_elem = entry.find('./dc:publisher', self.namespaces)
                if publisher_elem is not None and publisher_elem.text:
                    publisher = publisher_elem.text
                
                # Extract ISBN
                isbn = ""
                identifier_elems = entry.findall('./dc:identifier', self.namespaces)
                for identifier in identifier_elems:
                    if identifier.text and 'isbn' in identifier.text.lower():
                        isbn = identifier.text.split(':')[-1].strip()
                        break
                
                # Extract genres/subjects
                genres = []
                subject_elems = entry.findall('./dc:subject', self.namespaces)
                for subject in subject_elems:
                    if subject.text:
                        genres.append(subject.text)
                
                # Limit to a reasonable number of genres
                genres = list(set(genres))[:10]
                
                # Create result
                result = {
                    "id": book_id,
                    "title": title,
                    "alternative_titles": [],
                    "cover_url": cover_url,
                    "author": ", ".join(authors) if authors else "Unknown",
                    "status": "COMPLETED" if pub_date else "Unknown",
                    "description": description,
                    "genres": genres,
                    "rating": "0",  # WorldCat doesn't provide ratings
                    "volumes": 1,  # Most books are single volumes
                    "chapters": 0,  # WorldCat doesn't provide chapter info
                    "url": f"https://www.worldcat.org/title/{book_id}",
                    "source": self.name,
                    "isbn": isbn,
                    "published_date": pub_date,
                    "publisher": publisher
                }
                
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Error searching WorldCat API: {e}")
        
        return results

    def get_manga_details(self, manga_id: str) -> Dict[str, Any]:
        """Get details for a book on WorldCat.
        
        Args:
            manga_id: The book ID.
            
        Returns:
            The book details.
        """
        # Check if API key is available
        if not self.api_key:
            self.logger.error("WorldCat API key is required")
            return {}
            
        try:
            # For detailed info, we'll search by ID
            url = f"{self.base_url}"
            params = {
                "q": f"no:{manga_id}",  # Search by OCLC number
                "wskey": self.api_key,
                "count": 1,
                "format": "atom"
            }
                
            # Make the request
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Get the first entry
            entry = root.find('.//atom:entry', self.namespaces)
            if entry is None:
                return {}
            
            # Extract book ID from the ID field (last part of the URL)
            id_elem = entry.find('./atom:id', self.namespaces)
            book_id = id_elem.text.split('/')[-1] if id_elem is not None and id_elem.text else ""
            
            # Extract title
            title_elem = entry.find('./atom:title', self.namespaces)
            title = title_elem.text if title_elem is not None and title_elem.text else "Unknown Title"
            
            # Extract authors
            authors = []
            author_elems = entry.findall('./atom:author/atom:name', self.namespaces)
            for author_elem in author_elems:
                if author_elem.text:
                    authors.append(author_elem.text)
            
            # Extract description
            summary_elem = entry.find('./atom:summary', self.namespaces)
            description = summary_elem.text if summary_elem is not None and summary_elem.text else ""
            
            # Extract cover URL
            cover_url = ""
            link_elems = entry.findall('./atom:link', self.namespaces)
            for link in link_elems:
                rel = link.get('rel')
                if rel == 'icon' or rel == 'http://www.w3.org/2005/Atom/icon':
                    cover_url = link.get('href', '')
                    break
            
            # Extract publication date
            pub_date = ""
            date_elem = entry.find('./dc:date', self.namespaces)
            if date_elem is not None and date_elem.text:
                pub_date = date_elem.text
            
            # Extract publisher
            publisher = ""
            publisher_elem = entry.find('./dc:publisher', self.namespaces)
            if publisher_elem is not None and publisher_elem.text:
                publisher = publisher_elem.text
            
            # Extract ISBN
            isbn = ""
            identifier_elems = entry.findall('./dc:identifier', self.namespaces)
            for identifier in identifier_elems:
                if identifier.text and 'isbn' in identifier.text.lower():
                    isbn = identifier.text.split(':')[-1].strip()
                    break
            
            # Extract genres/subjects
            genres = []
            subject_elems = entry.findall('./dc:subject', self.namespaces)
            for subject in subject_elems:
                if subject.text:
                    genres.append(subject.text)
            
            # Limit to a reasonable number of genres
            genres = list(set(genres))[:10]
            
            # Extract format/type
            format_type = ""
            type_elem = entry.find('./dc:type', self.namespaces)
            if type_elem is not None and type_elem.text:
                format_type = type_elem.text
            
            # Extract language
            language = ""
            lang_elem = entry.find('./dc:language', self.namespaces)
            if lang_elem is not None and lang_elem.text:
                language = lang_elem.text
            
            # Create a single volume entry
            volumes_list = []
            if pub_date:
                volumes_list.append({
                    "number": "1",
                    "title": title,
                    "description": description,
                    "cover_url": cover_url,
                    "release_date": pub_date
                })
            
            return {
                "id": book_id,
                "title": title,
                "alternative_titles": [],
                "cover_url": cover_url,
                "author": ", ".join(authors) if authors else "Unknown",
                "status": "COMPLETED" if pub_date else "Unknown",
                "description": description,
                "genres": genres,
                "rating": "0",  # WorldCat doesn't provide ratings
                "volumes": 1,  # Most books are single volumes
                "chapters": 0,  # WorldCat doesn't provide chapter info
                "url": f"https://www.worldcat.org/title/{book_id}",
                "source": self.name,
                "isbn": isbn,
                "published_date": pub_date,
                "publisher": publisher,
                "format": format_type,
                "language": language,
                "volumes": volumes_list
            }
            
        except Exception as e:
            self.logger.error(f"Error getting book details from WorldCat API: {e}")
        
        return {}

    def get_chapter_list(self, manga_id: str) -> List[Dict[str, Any]]:
        """Get the chapter list for a book on WorldCat.
        
        Note: WorldCat API doesn't provide chapter information,
        so we return an empty list.
        
        Args:
            manga_id: The book ID.
            
        Returns:
            An empty list as WorldCat doesn't provide chapter information.
        """
        return {"chapters": []}

    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter on WorldCat.
        
        Note: WorldCat API doesn't provide chapter images,
        so we return an empty list.
        
        Args:
            manga_id: The book ID.
            chapter_id: The chapter ID.
            
        Returns:
            An empty list as WorldCat doesn't provide chapter images.
        """
        return []

    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest book releases on WorldCat.
        
        Args:
            page: The page number.
            
        Returns:
            A list of latest releases.
        """
        results: List[Dict[str, Any]] = []
        
        # Check if API key is available
        if not self.api_key:
            self.logger.error("WorldCat API key is required")
            return results
            
        try:
            # WorldCat doesn't have a direct "latest releases" endpoint,
            # so we'll search for recent publications with a broad query
            current_year = datetime.now().year
            
            # Build the API URL for recent publications
            url = f"{self.base_url}"
            params = {
                "q": f"yr:{current_year}",  # Search for books published this year
                "wskey": self.api_key,
                "start": (page - 1) * 10 + 1,
                "count": 10,
                "format": "atom"
            }
                
            # Make the request
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Process entries
            entries = root.findall('.//atom:entry', self.namespaces)
            
            for entry in entries:
                # Extract book ID from the ID field (last part of the URL)
                id_elem = entry.find('./atom:id', self.namespaces)
                book_id = id_elem.text.split('/')[-1] if id_elem is not None and id_elem.text else ""
                
                # Extract title
                title_elem = entry.find('./atom:title', self.namespaces)
                title = title_elem.text if title_elem is not None and title_elem.text else "Unknown Title"
                
                # Extract authors
                authors = []
                author_elems = entry.findall('./atom:author/atom:name', self.namespaces)
                for author_elem in author_elems:
                    if author_elem.text:
                        authors.append(author_elem.text)
                
                # Extract cover URL
                cover_url = ""
                link_elems = entry.findall('./atom:link', self.namespaces)
                for link in link_elems:
                    rel = link.get('rel')
                    if rel == 'icon' or rel == 'http://www.w3.org/2005/Atom/icon':
                        cover_url = link.get('href', '')
                        break
                
                # Extract publication date
                pub_date = ""
                date_elem = entry.find('./dc:date', self.namespaces)
                if date_elem is not None and date_elem.text:
                    pub_date = date_elem.text
                
                result = {
                    "manga_id": book_id,
                    "manga_title": title,
                    "cover_url": cover_url,
                    "author": ", ".join(authors) if authors else "Unknown",
                    "volumes": 1,
                    "chapters": 0,
                    "rating": "0",  # WorldCat doesn't provide ratings
                    "url": f"https://www.worldcat.org/title/{book_id}",
                    "source": self.name,
                    "published_date": pub_date
                }
                
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Error getting latest releases from WorldCat API: {e}")
        
        return results
