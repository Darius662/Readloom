#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provider gateway for metadata service.
Handles provider resolution and dispatching requests to providers.
"""

from typing import Dict, List, Any, Optional, Union

from backend.base.logging import LOGGER
from backend.features.metadata_providers.base import metadata_provider_manager


def get_provider(provider_name: str):
    """Get a provider by name and verify it's enabled.
    
    Args:
        provider_name: The provider name.
        
    Returns:
        The provider instance or None if not found or disabled.
    """
    provider = metadata_provider_manager.get_provider(provider_name)
    if not provider:
        LOGGER.error(f"Provider not found: {provider_name}")
        return None
    
    if not provider.enabled:
        LOGGER.warning(f"Provider is disabled: {provider_name}")
        return None
    
    return provider


def search_with_provider(query: str, provider_name: str, page: int = 1, search_type: str = "title") -> List[Dict[str, Any]]:
    """Search for manga with a specific provider.
    
    Args:
        query: The search query.
        provider_name: The provider name.
        page: The page number.
        search_type: The type of search to perform (title or author).
        
    Returns:
        A list of search results or empty list on error.
    """
    provider = get_provider(provider_name)
    if not provider:
        return []
    
    try:
        # Check if the provider supports the search_type parameter
        if "search_type" in provider.search.__code__.co_varnames:
            return provider.search(query, page, search_type)
        else:
            # Fallback for providers that don't support search_type
            return provider.search(query, page)
    except Exception as e:
        LOGGER.error(f"Error searching with provider {provider_name}: {e}")
        return []


def search_with_all_providers(query: str, page: int = 1, search_type: str = "title") -> Dict[str, List[Dict[str, Any]]]:
    """Search for manga across all enabled providers.
    
    Args:
        query: The search query.
        page: The page number.
        search_type: The type of search to perform (title or author).
        
    Returns:
        A dictionary mapping provider names to search results.
    """
    # Check if the search_all method supports search_type parameter
    if hasattr(metadata_provider_manager, "search_all_with_type"):
        return metadata_provider_manager.search_all_with_type(query, page, search_type)
    
    # Fallback: manually search each provider with search_type support
    results = {}
    for provider_name, provider in metadata_provider_manager.get_enabled_providers().items():
        try:
            # Check if the provider supports the search_type parameter
            if "search_type" in provider.search.__code__.co_varnames:
                results[provider_name] = provider.search(query, page, search_type)
            else:
                # Fallback for providers that don't support search_type
                results[provider_name] = provider.search(query, page)
        except Exception as e:
            LOGGER.error(f"Error searching with provider {provider_name}: {e}")
            results[provider_name] = []
    
    return results


def get_manga_details_from_provider(manga_id: str, provider_name: str) -> Dict[str, Any]:
    """Get manga details from a specific provider.
    
    Args:
        manga_id: The manga ID.
        provider_name: The provider name.
        
    Returns:
        The manga details or empty dict on error.
    """
    provider = get_provider(provider_name)
    if not provider:
        return {}
    
    try:
        return provider.get_manga_details(manga_id)
    except Exception as e:
        LOGGER.error(f"Error getting manga details from provider {provider_name}: {e}")
        return {}


def get_chapter_list_from_provider(manga_id: str, provider_name: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """Get chapter list from a specific provider.
    
    Args:
        manga_id: The manga ID.
        provider_name: The provider name.
        
    Returns:
        The chapter list or empty dict/list on error.
    """
    provider = get_provider(provider_name)
    if not provider:
        return {"chapters": []}
    
    try:
        return provider.get_chapter_list(manga_id)
    except Exception as e:
        LOGGER.error(f"Error getting chapter list from provider {provider_name}: {e}")
        return {"chapters": []}


def get_chapter_images_from_provider(manga_id: str, chapter_id: str, provider_name: str) -> List[str]:
    """Get chapter images from a specific provider.
    
    Args:
        manga_id: The manga ID.
        chapter_id: The chapter ID.
        provider_name: The provider name.
        
    Returns:
        A list of image URLs or empty list on error.
    """
    provider = get_provider(provider_name)
    if not provider:
        return []
    
    try:
        return provider.get_chapter_images(manga_id, chapter_id)
    except Exception as e:
        LOGGER.error(f"Error getting chapter images from provider {provider_name}: {e}")
        return []


def get_latest_releases_from_provider(provider_name: str, page: int = 1) -> List[Dict[str, Any]]:
    """Get latest releases from a specific provider.
    
    Args:
        provider_name: The provider name.
        page: The page number.
        
    Returns:
        A list of latest releases or empty list on error.
    """
    provider = get_provider(provider_name)
    if not provider:
        return []
    
    try:
        return provider.get_latest_releases(page)
    except Exception as e:
        LOGGER.error(f"Error getting latest releases from provider {provider_name}: {e}")
        return []


def get_latest_releases_from_all_providers(page: int = 1) -> Dict[str, List[Dict[str, Any]]]:
    """Get latest releases from all enabled providers.
    
    Args:
        page: The page number.
        
    Returns:
        A dictionary mapping provider names to latest releases.
    """
    return metadata_provider_manager.get_latest_releases_all(page)
