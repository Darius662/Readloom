#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base classes for metadata providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
import logging

from backend.base.logging import LOGGER


class MetadataProvider(ABC):
    """Base class for metadata providers."""

    def __init__(self, name: str, enabled: bool = True):
        """Initialize the metadata provider.
        
        Args:
            name: The name of the provider.
            enabled: Whether the provider is enabled.
        """
        self.name = name
        self.enabled = enabled
        self.logger = LOGGER

    @abstractmethod
    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for manga.
        
        Args:
            query: The search query.
            page: The page number.
            
        Returns:
            A list of manga search results.
        """
        pass

    @abstractmethod
    def get_manga_details(self, manga_id: str) -> Dict[str, Any]:
        """Get details for a manga.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            The manga details.
        """
        pass

    @abstractmethod
    def get_chapter_list(self, manga_id: str) -> List[Dict[str, Any]]:
        """Get the chapter list for a manga.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            A list of chapters.
        """
        pass

    @abstractmethod
    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter.
        
        Args:
            manga_id: The manga ID.
            chapter_id: The chapter ID.
            
        Returns:
            A list of image URLs.
        """
        pass

    @abstractmethod
    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest manga releases.
        
        Args:
            page: The page number.
            
        Returns:
            A list of latest releases.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert the provider to a dictionary.
        
        Returns:
            A dictionary representation of the provider.
        """
        return {
            "name": self.name,
            "enabled": self.enabled
        }


class MetadataProviderManager:
    """Manager for metadata providers."""

    def __init__(self):
        """Initialize the metadata provider manager."""
        self.providers: Dict[str, MetadataProvider] = {}
        self.logger = LOGGER

    def register_provider(self, provider: MetadataProvider) -> None:
        """Register a metadata provider.
        
        Args:
            provider: The provider to register.
        """
        self.providers[provider.name] = provider
        self.logger.info(f"Registered metadata provider: {provider.name}")

    def get_provider(self, name: str) -> Optional[MetadataProvider]:
        """Get a metadata provider by name.
        
        Args:
            name: The name of the provider.
            
        Returns:
            The provider, or None if not found.
        """
        return self.providers.get(name)

    def get_all_providers(self) -> List[MetadataProvider]:
        """Get all registered providers.
        
        Returns:
            A list of all providers.
        """
        return list(self.providers.values())

    def get_enabled_providers(self) -> Dict[str, MetadataProvider]:
        """Get all enabled providers.
        
        Returns:
            A dictionary of enabled providers with name as key.
        """
        return {name: provider for name, provider in self.providers.items() if provider.enabled}

    def search_all(self, query: str, page: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """Search for manga across all enabled providers.
        
        Args:
            query: The search query.
            page: The page number.
            
        Returns:
            A dictionary mapping provider names to search results.
        """
        results = {}
        for name, provider in self.get_enabled_providers().items():
            try:
                results[name] = provider.search(query, page)
            except Exception as e:
                self.logger.error(f"Error searching with provider {name}: {e}")
                results[name] = []
        return results
        
    def search_all_with_type(self, query: str, page: int = 1, search_type: str = "title") -> Dict[str, List[Dict[str, Any]]]:
        """Search for manga across all enabled providers with search type.
        
        Args:
            query: The search query.
            page: The page number.
            search_type: The type of search to perform (title or author).
            
        Returns:
            A dictionary mapping provider names to search results.
        """
        results = {}
        for name, provider in self.get_enabled_providers().items():
            try:
                # Check if the provider supports the search_type parameter
                if "search_type" in provider.search.__code__.co_varnames:
                    results[name] = provider.search(query, page, search_type)
                else:
                    # Fallback for providers that don't support search_type
                    results[name] = provider.search(query, page)
            except Exception as e:
                self.logger.error(f"Error searching with provider {name}: {e}")
                results[name] = []
        return results

    def get_latest_releases_all(self, page: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """Get the latest manga releases across all enabled providers.
        
        Args:
            page: The page number.
            
        Returns:
            A dictionary mapping provider names to latest releases.
        """
        results = {}
        for name, provider in self.get_enabled_providers().items():
            try:
                results[name] = provider.get_latest_releases(page)
            except Exception as e:
                self.logger.error(f"Error getting latest releases with provider {name}: {e}")
                results[name] = []
        return results


# Create a global instance of the metadata provider manager
metadata_provider_manager = MetadataProviderManager()
