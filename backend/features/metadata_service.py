#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Metadata service for MangaArr.
This module provides services for searching and fetching manga metadata from external sources.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

from backend.base.logging import LOGGER
from backend.internals.db import execute_query, get_db_connection
from backend.features.metadata_providers.base import metadata_provider_manager
from backend.features.metadata_providers.setup import initialize_providers, get_provider_settings, update_provider_settings


def init_metadata_service() -> None:
    """Initialize the metadata service."""
    try:
        # Initialize metadata providers
        initialize_providers()
        
        # Create metadata cache table if it doesn't exist
        execute_query("""
            CREATE TABLE IF NOT EXISTS metadata_cache (
                id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                type TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        LOGGER.info("Metadata service initialized")
    except Exception as e:
        LOGGER.error(f"Error initializing metadata service: {e}")


def search_manga(query: str, provider: Optional[str] = None, page: int = 1) -> Dict[str, Any]:
    """Search for manga across all enabled providers or a specific provider.
    
    Args:
        query: The search query.
        provider: The provider name (optional).
        page: The page number.
        
    Returns:
        A dictionary containing search results.
    """
    try:
        if provider:
            # Search with a specific provider
            provider_instance = metadata_provider_manager.get_provider(provider)
            if not provider_instance:
                return {"error": f"Provider not found: {provider}"}
            
            if not provider_instance.enabled:
                return {"error": f"Provider is disabled: {provider}"}
            
            results = {provider: provider_instance.search(query, page)}
        else:
            # Search with all enabled providers
            results = metadata_provider_manager.search_all(query, page)
        
        # Format the response
        response = {
            "query": query,
            "page": page,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    except Exception as e:
        LOGGER.error(f"Error searching manga: {e}")
        return {"error": str(e)}


def get_manga_details(manga_id: str, provider: str) -> Dict[str, Any]:
    """Get details for a manga.
    
    Args:
        manga_id: The manga ID.
        provider: The provider name.
        
    Returns:
        A dictionary containing manga details.
    """
    try:
        # Check cache first
        cache_key = f"{provider}_{manga_id}"
        cached_data = get_from_cache(cache_key, "manga_details")
        
        if cached_data:
            return cached_data
        
        # Get from provider if not in cache
        provider_instance = metadata_provider_manager.get_provider(provider)
        if not provider_instance:
            return {"error": f"Provider not found: {provider}"}
        
        if not provider_instance.enabled:
            return {"error": f"Provider is disabled: {provider}"}
        
        details = provider_instance.get_manga_details(manga_id)
        
        if details:
            # Add to cache
            save_to_cache(cache_key, "manga_details", details)
        
        return details
    except Exception as e:
        LOGGER.error(f"Error getting manga details: {e}")
        return {"error": str(e)}


def get_chapter_list(manga_id: str, provider: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """Get the chapter list for a manga.
    
    Args:
        manga_id: The manga ID.
        provider: The provider name.
        
    Returns:
        A list of chapters or a dictionary with error information.
    """
    try:
        # Check if we have a cached version
        cache_key = f"{provider}_{manga_id}_chapters"
        cached = get_from_cache(cache_key, "chapters")
        if cached:
            return cached
        
        # Get the provider instance
        provider_instance = metadata_provider_manager.get_provider(provider)
        if not provider_instance:
            return {"error": f"Provider not found: {provider}", "chapters": []}
        
        if not provider_instance.enabled:
            return {"error": f"Provider is disabled: {provider}", "chapters": []}
        
        # Get chapter list from provider
        chapters = provider_instance.get_chapter_list(manga_id)
        
        # Handle different return types
        if isinstance(chapters, dict):
            # Already in the right format
            result = chapters
        elif isinstance(chapters, list):
            # Convert list to dict format
            result = {"chapters": chapters}
        else:
            # Handle unexpected return type
            LOGGER.error(f"Unexpected return type from get_chapter_list: {type(chapters)}")
            result = {"error": f"Unexpected return type: {type(chapters)}", "chapters": []}
        
        # Cache the results
        save_to_cache(cache_key, "chapters", result)
        
        return result
    except Exception as e:
        LOGGER.error(f"Error getting chapter list: {e}")
        return {"error": str(e), "chapters": []}


def get_chapter_images(manga_id: str, chapter_id: str, provider: str) -> Dict[str, Any]:
    """Get the images for a chapter.
    
    Args:
        manga_id: The manga ID.
        chapter_id: The chapter ID.
        provider: The provider name.
        
    Returns:
        A dictionary containing chapter images.
    """
    try:
        # Check cache first
        cache_key = f"{provider}_{manga_id}_{chapter_id}"
        cached_data = get_from_cache(cache_key, "chapter_images")
        
        if cached_data:
            return {"images": cached_data}
        
        # Get from provider if not in cache
        provider_instance = metadata_provider_manager.get_provider(provider)
        if not provider_instance:
            return {"error": f"Provider not found: {provider}"}
        
        if not provider_instance.enabled:
            return {"error": f"Provider is disabled: {provider}"}
        
        images = provider_instance.get_chapter_images(manga_id, chapter_id)
        
        if images:
            # Add to cache
            save_to_cache(cache_key, "chapter_images", images)
        
        return {"images": images}
    except Exception as e:
        LOGGER.error(f"Error getting chapter images: {e}")
        return {"error": str(e)}


def get_latest_releases(provider: Optional[str] = None, page: int = 1) -> Dict[str, Any]:
    """Get the latest manga releases.
    
    Args:
        provider: The provider name (optional).
        page: The page number.
        
    Returns:
        A dictionary containing latest releases.
    """
    try:
        if provider:
            # Get latest releases from a specific provider
            provider_instance = metadata_provider_manager.get_provider(provider)
            if not provider_instance:
                return {"error": f"Provider not found: {provider}"}
            
            if not provider_instance.enabled:
                return {"error": f"Provider is disabled: {provider}"}
            
            results = {provider: provider_instance.get_latest_releases(page)}
        else:
            # Get latest releases from all enabled providers
            results = metadata_provider_manager.get_latest_releases_all(page)
        
        # Format the response
        response = {
            "page": page,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    except Exception as e:
        LOGGER.error(f"Error getting latest releases: {e}")
        return {"error": str(e)}


def get_providers() -> Dict[str, Any]:
    """Get all metadata providers and their settings.
    
    Returns:
        A dictionary containing provider information.
    """
    try:
        providers = get_provider_settings()
        
        return {
            "providers": providers,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        LOGGER.error(f"Error getting providers: {e}")
        return {"error": str(e)}


def update_provider(name: str, enabled: bool, settings: Dict[str, Any]) -> Dict[str, Any]:
    """Update a metadata provider's settings.
    
    Args:
        name: The provider name.
        enabled: Whether the provider is enabled.
        settings: The provider settings.
        
    Returns:
        A dictionary containing the result.
    """
    try:
        success = update_provider_settings(name, enabled, settings)
        
        if success:
            return {
                "success": True,
                "message": f"Provider {name} updated successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Failed to update provider {name}"
            }
    except Exception as e:
        LOGGER.error(f"Error updating provider: {e}")
        return {
            "success": False,
            "message": str(e)
        }


def save_to_cache(id: str, type: str, data: Any) -> bool:
    """Save data to the metadata cache.
    
    Args:
        id: The cache ID.
        type: The cache type.
        data: The data to cache.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        # Convert data to JSON
        json_data = json.dumps(data)
        
        # Check if the cache entry already exists
        existing = execute_query(
            "SELECT id FROM metadata_cache WHERE id = ? AND type = ?",
            (id, type)
        )
        
        if existing:
            # Update existing cache entry
            execute_query(
                "UPDATE metadata_cache SET data = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ? AND type = ?",
                (json_data, id, type)
            )
        else:
            # Insert new cache entry
            execute_query(
                "INSERT INTO metadata_cache (id, provider, type, data) VALUES (?, ?, ?, ?)",
                (id, id.split('_')[0], type, json_data)
            )
        
        return True
    except Exception as e:
        LOGGER.error(f"Error saving to cache: {e}")
        return False


def get_from_cache(id: str, type: str) -> Any:
    """Get data from the metadata cache.
    
    Args:
        id: The cache ID.
        type: The cache type.
        
    Returns:
        The cached data, or None if not found.
    """
    try:
        # Get cache entry
        cache_entry = execute_query(
            "SELECT data, timestamp FROM metadata_cache WHERE id = ? AND type = ?",
            (id, type)
        )
        
        if not cache_entry:
            return None
        
        # Check if cache is expired (7 days)
        cache_time = datetime.fromisoformat(cache_entry[0]["timestamp"])
        current_time = datetime.now()
        
        if (current_time - cache_time).days > 7:
            # Cache is expired, delete it
            execute_query(
                "DELETE FROM metadata_cache WHERE id = ? AND type = ?",
                (id, type)
            )
            return None
        
        # Return cached data
        return json.loads(cache_entry[0]["data"])
    except Exception as e:
        LOGGER.error(f"Error getting from cache: {e}")
        return None


def clear_cache(provider: Optional[str] = None, type: Optional[str] = None) -> Dict[str, Any]:
    """Clear the metadata cache.
    
    Args:
        provider: The provider name (optional).
        type: The cache type (optional).
        
    Returns:
        A dictionary containing the result.
    """
    try:
        if provider and type:
            # Clear specific provider and type
            execute_query(
                "DELETE FROM metadata_cache WHERE provider = ? AND type = ?",
                (provider, type)
            )
        elif provider:
            # Clear specific provider
            execute_query(
                "DELETE FROM metadata_cache WHERE provider = ?",
                (provider,)
            )
        elif type:
            # Clear specific type
            execute_query(
                "DELETE FROM metadata_cache WHERE type = ?",
                (type,)
            )
        else:
            # Clear all cache
            execute_query("DELETE FROM metadata_cache")
        
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        LOGGER.error(f"Error clearing cache: {e}")
        return {
            "success": False,
            "message": str(e)
        }


def import_manga_to_collection(manga_id: str, provider: str) -> Dict[str, Any]:
    """Import a manga from an external source to the collection.
    
    Args:
        manga_id: The manga ID.
        provider: The provider name.
        
    Returns:
        A dictionary containing the result.
    """
    try:
        # Get manga details
        manga_details = get_manga_details(manga_id, provider)
        
        if "error" in manga_details:
            return manga_details
        
        # Check if the series already exists
        existing_series = execute_query(
            "SELECT id FROM series WHERE metadata_source = ? AND metadata_id = ?",
            (provider, manga_id)
        )
        
        if existing_series:
            return {
                "success": False,
                "message": "Series already exists in the collection",
                "series_id": existing_series[0]["id"]
            }
        
        # Insert the series
        try:
            # Get a direct connection to execute the insert and get the last row ID
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO series (
                    title, description, author, publisher, cover_url, status, metadata_source, metadata_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    manga_details.get("title", "Unknown"),
                    manga_details.get("description", ""),
                    manga_details.get("author", "Unknown"),
                    manga_details.get("publisher", "Unknown"),
                    manga_details.get("cover_url", ""),
                    manga_details.get("status", "ONGOING"),
                    provider,
                    manga_id
                )
            )
            conn.commit()
            
            # Get the ID of the last inserted row
            series_id = cursor.lastrowid
            
            if not series_id:
                return {
                    "success": False,
                    "message": "Failed to insert series into database"
                }
        except Exception as e:
            LOGGER.error(f"Error inserting series: {e}")
            return {
                "success": False,
                "message": f"Database error: {str(e)}"
            }
        
        # Get chapter list
        chapter_list_result = get_chapter_list(manga_id, provider)
        
        # Handle different return types (for backward compatibility)
        if isinstance(chapter_list_result, dict):
            if "error" in chapter_list_result:
                return {
                    "success": True,
                    "message": "Series added to collection, but failed to import chapters",
                    "series_id": series_id
                }
            chapter_list = chapter_list_result.get("chapters", [])
        elif isinstance(chapter_list_result, list):
            chapter_list = chapter_list_result
        else:
            # If it's neither a dict nor a list, assume it's an error
            return {
                "success": True,
                "message": "Series added to collection, but failed to import chapters",
                "series_id": series_id
            }
        
        # Insert volumes if available
        volumes = {}
        if "volumes" in manga_details and isinstance(manga_details["volumes"], list) and manga_details["volumes"]:
            LOGGER.info(f"Importing {len(manga_details['volumes'])} volumes from {provider}")
            for volume in manga_details["volumes"]:
                try:
                    # Get a direct connection to execute the insert and get the last row ID
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO volumes (
                            series_id, volume_number, title, description, cover_url, release_date
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            series_id,
                            volume.get("number", "0"),
                            volume.get("title", f"Volume {volume.get('number', '0')}"),
                            volume.get("description", ""),
                            volume.get("cover_url", ""),
                            volume.get("release_date", "") or volume.get("date", "")
                        )
                    )
                    conn.commit()
                    
                    # Get the ID of the last inserted row
                    volume_id = cursor.lastrowid
                    
                    if volume_id:
                        volumes[volume.get("number", "0")] = volume_id
                except Exception as e:
                    LOGGER.error(f"Error inserting volume: {e}")
        
        # Insert chapters
        chapters_added = 0
        for chapter in chapter_list:
            # Try to determine volume number from chapter number
            volume_number = "0"
            if "number" in chapter:
                try:
                    chapter_num = float(chapter["number"])
                    volume_number = str(max(1, int(chapter_num / 10)))
                except (ValueError, TypeError):
                    volume_number = "0"
            
            # Get volume ID if available
            volume_id = volumes.get(volume_number, None)
            
            # Get release date - prioritize standardized format
            chapter_date = chapter.get("date", "") or chapter.get("release_date", "")
            
            # Log chapter data for debugging
            LOGGER.info(f"Importing chapter: {chapter.get('number', 'Unknown')} with date {chapter_date}")
            
            # Validate the date format
            if chapter_date:
                try:
                    # Try to parse the date to verify format
                    test_date = datetime.fromisoformat(chapter_date)
                    # It's valid, keep it
                except (ValueError, TypeError):
                    # Invalid format, log warning but continue with the date
                    LOGGER.warning(f"Potentially invalid date format: {chapter_date} for chapter {chapter.get('number', 'Unknown')}")
            
            execute_query(
                """
                INSERT INTO chapters (
                    series_id, volume_id, chapter_number, title, description, release_date, status, read_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    series_id,
                    volume_id,
                    chapter.get("number", "0") or "0",  # Ensure chapter_number is never null
                    chapter.get("title", f"Chapter {chapter.get('number', '0') or '0'}"),
                    "",
                    chapter_date,  # Use our validated date
                    "ANNOUNCED",
                    "UNREAD"
                )
            )
            
            chapters_added += 1
        
        return {
            "success": True,
            "message": f"Series added to collection with {chapters_added} chapters",
            "series_id": series_id
        }
    except Exception as e:
        LOGGER.error(f"Error importing manga to collection: {e}")
        return {
            "success": False,
            "message": str(e)
        }
