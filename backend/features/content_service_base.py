#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base interface for content services.
Defines the common interface that all content services must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

from backend.base.logging import LOGGER


class ContentServiceBase(ABC):
    """Base interface for content services."""
    
    def __init__(self):
        """Initialize the content service."""
        self.logger = LOGGER
    
    @abstractmethod
    def search(self, query: str, search_type: str = "title", provider: Optional[str] = None, page: int = 1) -> Dict[str, Any]:
        """Search for content.
        
        Args:
            query: The search query.
            search_type: The type of search (title, author, etc.).
            provider: The provider to search with (optional).
            page: The page number.
            
        Returns:
            A dictionary containing search results.
        """
        # Default implementation that should be overridden
        self.logger.warning("Using default search implementation")
        return {
            "query": query,
            "search_type": search_type,
            "page": page,
            "results": {},
            "error": "Not implemented"
        }
    
    @abstractmethod
    def get_details(self, content_id: str, provider: str) -> Dict[str, Any]:
        """Get content details.
        
        Args:
            content_id: The content ID.
            provider: The provider name.
            
        Returns:
            A dictionary containing content details.
        """
        # Default implementation that should be overridden
        self.logger.warning("Using default get_details implementation")
        return {
            "error": "Not implemented"
        }
    
    @abstractmethod
    def import_to_collection(self, content_id: str, provider: str, 
                            collection_id: Optional[int] = None,
                            content_type: Optional[str] = None,
                            root_folder_id: Optional[int] = None) -> Dict[str, Any]:
        """Import content to collection.
        
        Args:
            content_id: The content ID.
            provider: The provider name.
            collection_id: The collection ID (optional).
            content_type: The content type (optional).
            root_folder_id: The root folder ID (optional).
            
        Returns:
            A dictionary containing the result.
        """
        # Default implementation that should be overridden
        self.logger.warning("Using default import_to_collection implementation")
        return {
            "success": False,
            "message": "Not implemented"
        }
    
    @abstractmethod
    def create_folder_structure(self, content_id: Union[int, str], title: str, 
                               content_type: str, collection_id: Optional[int] = None,
                               root_folder_id: Optional[int] = None,
                               author: Optional[str] = None) -> str:
        """Create appropriate folder structure.
        
        Args:
            content_id: The content ID.
            title: The content title.
            content_type: The content type.
            collection_id: The collection ID (optional).
            root_folder_id: The root folder ID (optional).
            author: The author name (optional).
            
        Returns:
            The path to the created folder.
        """
        # Default implementation that should be overridden
        self.logger.warning("Using default create_folder_structure implementation")
        from backend.base.helpers import create_series_folder_structure
        return create_series_folder_structure(content_id, title, content_type, collection_id, root_folder_id)
    
    def get_content_type_group(self, content_type: str) -> str:
        """Get the content type group (book or manga).
        
        Args:
            content_type: The content type.
            
        Returns:
            The content type group.
        """
        from backend.features.content_service_factory import ContentType
        if ContentType.is_book_type(content_type):
            return "book"
        elif ContentType.is_manga_type(content_type):
            return "manga"
        else:
            return "other"
