#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Content service factory for Readloom.
Provides a factory pattern to route requests to the appropriate service based on content type.
"""

from enum import Enum
from typing import Union, Any, Dict, Optional

from backend.base.logging import LOGGER


class ContentType(Enum):
    """Content type enum for different types of content."""
    BOOK = "BOOK"
    NOVEL = "NOVEL"
    MANGA = "MANGA"
    MANHWA = "MANHWA"
    MANHUA = "MANHUA"
    COMIC = "COMIC"
    OTHER = "OTHER"
    
    @classmethod
    def from_string(cls, content_type_str: str) -> "ContentType":
        """Convert a string to a ContentType enum value.
        
        Args:
            content_type_str: The content type string.
            
        Returns:
            The corresponding ContentType enum value.
        """
        try:
            return cls[content_type_str.upper()]
        except (KeyError, AttributeError):
            LOGGER.warning(f"Unknown content type: {content_type_str}, defaulting to OTHER")
            return cls.OTHER
    
    @classmethod
    def is_book_type(cls, content_type: Union[str, "ContentType"]) -> bool:
        """Check if a content type is a book type.
        
        Args:
            content_type: The content type to check.
            
        Returns:
            True if the content type is a book type, False otherwise.
        """
        if isinstance(content_type, str):
            content_type = cls.from_string(content_type)
        return content_type in [cls.BOOK, cls.NOVEL]
    
    @classmethod
    def is_manga_type(cls, content_type: Union[str, "ContentType"]) -> bool:
        """Check if a content type is a manga type.
        
        Args:
            content_type: The content type to check.
            
        Returns:
            True if the content type is a manga type, False otherwise.
        """
        if isinstance(content_type, str):
            content_type = cls.from_string(content_type)
        return content_type in [cls.MANGA, cls.MANHWA, cls.MANHUA, cls.COMIC]


def get_content_service(content_type: Union[str, ContentType]):
    """Get the appropriate content service based on content type.
    
    Args:
        content_type: The content type.
        
    Returns:
        The appropriate content service.
    """
    # Import here to avoid circular imports
    from backend.features.content_service_base import ContentServiceBase
    
    if isinstance(content_type, str):
        content_type = ContentType.from_string(content_type)
    
    try:
        if ContentType.is_book_type(content_type):
            # Import the book service only when needed
            try:
                from backend.features.book_service import BookService
                return BookService()
            except ImportError:
                LOGGER.warning("BookService not available, falling back to base implementation")
                return ContentServiceBase()
        else:
            # Import the manga service only when needed
            try:
                from backend.features.manga_service import MangaService
                return MangaService()
            except ImportError:
                LOGGER.warning("MangaService not available, falling back to base implementation")
                return ContentServiceBase()
    except Exception as e:
        LOGGER.error(f"Error getting content service: {e}")
        return ContentServiceBase()


def get_service_for_content(content_id: Union[int, str], content_type: Optional[Union[str, ContentType]] = None) -> Any:
    """Get the appropriate service for a specific content item.
    
    Args:
        content_id: The content ID.
        content_type: The content type (optional, will be looked up if not provided).
        
    Returns:
        The appropriate content service.
    """
    if content_type is None:
        # Look up content type from database
        from backend.internals.db import execute_query
        result = execute_query("SELECT content_type FROM series WHERE id = ?", (content_id,))
        if result:
            content_type = result[0]["content_type"]
        else:
            LOGGER.warning(f"Content not found with ID: {content_id}, defaulting to manga service")
            content_type = "MANGA"
    
    return get_content_service(content_type)
