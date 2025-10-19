#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Facade for metadata service.
Exposes public API and delegates to cache and provider gateway.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from backend.base.logging import LOGGER
from backend.features.metadata_providers.setup import initialize_providers, get_provider_settings, update_provider_settings
from .cache import save_to_cache, get_from_cache, clear_cache
from .provider_gateway import (
    search_with_provider,
    search_with_all_providers,
    get_manga_details_from_provider,
    get_chapter_list_from_provider,
    get_chapter_images_from_provider,
    get_latest_releases_from_provider,
    get_latest_releases_from_all_providers,
)


def init_metadata_service() -> None:
    """Initialize the metadata service."""
    try:
        # Initialize metadata providers
        initialize_providers()
        
        # Drop and recreate metadata cache table to ensure proper schema
        from backend.internals.db import execute_query
        execute_query("DROP TABLE IF EXISTS metadata_cache")
        
        # Create metadata cache table with proper schema
        execute_query("""
            CREATE TABLE IF NOT EXISTS metadata_cache (
                id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                type TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """, commit=True)
        
        LOGGER.info("Metadata service initialized")
    except Exception as e:
        LOGGER.error(f"Error initializing metadata service: {e}")


def search_manga(query: str, provider: Optional[str] = None, page: int = 1, search_type: str = "title") -> Dict[str, Any]:
    """Search for manga across all enabled providers or a specific provider.
    
    Args:
        query: The search query.
        provider: The provider name (optional).
        page: The page number.
        search_type: The type of search to perform (title or author).
        
    Returns:
        A dictionary containing search results.
    """
    try:
        if provider:
            # Search with a specific provider
            results = {provider: search_with_provider(query, provider, page, search_type)}
        else:
            # Search with all enabled providers
            results = search_with_all_providers(query, page, search_type)
        
        # Format the response
        response = {
            "query": query,
            "page": page,
            "search_type": search_type,
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
        details = get_manga_details_from_provider(manga_id, provider)
        
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
        
        # Get chapter list from provider
        chapters = get_chapter_list_from_provider(manga_id, provider)
        
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
        images = get_chapter_images_from_provider(manga_id, chapter_id, provider)
        
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
            results = {provider: get_latest_releases_from_provider(provider, page)}
        else:
            # Get latest releases from all enabled providers
            results = get_latest_releases_from_all_providers(page)
        
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


def import_manga_to_collection(
    manga_id: str,
    provider: str,
    collection_id: Optional[int] = None,
    content_type: Optional[str] = None,
    root_folder_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Import a manga from an external source to the collection.
    
    Args:
        manga_id: The manga ID.
        provider: The provider name.
        
    Returns:
        A dictionary containing the result.
    """
    # Import LOGGER at the top of the function to ensure it's available in all code paths
    from backend.base.logging import LOGGER
    
    try:
        # Get manga details
        manga_details = get_manga_details(manga_id, provider)
        
        if "error" in manga_details:
            return manga_details
        
        # Check if the series already exists
        from backend.internals.db import execute_query, get_db_connection
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
        
        # Determine inferred content type using metadata heuristics
        def infer_from_metadata(details: Dict[str, Any]) -> Optional[str]:
            try:
                text_bins: List[str] = []
                # Common fields across providers
                for key in [
                    "categories", "subjects", "tags", "genres", "topic",
                    "topic_list", "genre_list"
                ]:
                    val = details.get(key)
                    if isinstance(val, list):
                        text_bins.extend([str(v) for v in val])
                    elif isinstance(val, str):
                        text_bins.append(val)
                # Title/description hints
                for key in ["title", "description"]:
                    v = details.get(key)
                    if isinstance(v, str):
                        text_bins.append(v)

                blob = " ".join(text_bins).lower()
                if any(tok in blob for tok in ["manga", "manhwa", "manhua", "shonen", "seinen", "shojo", "shoujo"]):
                    return "MANGA"
                if any(tok in blob for tok in ["graphic novel", "comics", "comic", "bd "]):
                    return "COMIC"
                return None
            except Exception:
                return None

        if content_type:
            inferred_type = (content_type or "MANGA").upper()
        else:
            heur = infer_from_metadata(manga_details) if isinstance(manga_details, dict) else None
            if heur:
                inferred_type = heur
            else:
                # Provider-based fallback
                provider_upper = (provider or "").upper()
                if provider_upper in {"GOOGLEBOOKS", "OPENLIBRARY", "ISBNDB", "WORLDCAT"}:
                    inferred_type = "BOOK"
                else:
                    inferred_type = "MANGA"

        # Insert the series
        try:
            # Get a direct connection to execute the insert and get the last row ID
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO series (
                    title, description, author, publisher, cover_url, status, content_type, metadata_source, metadata_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    manga_details.get("title", "Unknown"),
                    manga_details.get("description", ""),
                    manga_details.get("author", "Unknown"),
                    manga_details.get("publisher", "Unknown"),
                    manga_details.get("cover_url", ""),
                    manga_details.get("status", "ONGOING"),
                    manga_details.get("content_type", inferred_type),
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
        from datetime import timedelta
        chapter_list_result = get_chapter_list(manga_id, provider)
        
        # Handle different return types (for backward compatibility)
        if isinstance(chapter_list_result, dict):
            if "error" in chapter_list_result:
                LOGGER.warning(f"Error getting chapters from provider: {chapter_list_result.get('error')}")
                # Create at least 3 placeholder chapters
                chapter_list = [
                    {"number": "1", "title": "Chapter 1", "date": datetime.now().strftime("%Y-%m-%d")},
                    {"number": "2", "title": "Chapter 2", "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")},
                    {"number": "3", "title": "Chapter 3", "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")}
                ]
                LOGGER.info("Created 3 placeholder chapters since provider failed")
            else:
                chapter_list = chapter_list_result.get("chapters", [])
        elif isinstance(chapter_list_result, list):
            chapter_list = chapter_list_result
        else:
            # If it's neither a dict nor a list, create placeholder chapters
            LOGGER.warning(f"Unexpected chapter list result type: {type(chapter_list_result)}")
            chapter_list = [
                {"number": "1", "title": "Chapter 1", "date": datetime.now().strftime("%Y-%m-%d")},
                {"number": "2", "title": "Chapter 2", "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")},
                {"number": "3", "title": "Chapter 3", "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")}
            ]
            LOGGER.info("Created 3 placeholder chapters due to unexpected result type")
        
        # Insert volumes - ensure we create them even if provider doesn't give them
        volumes = {}
        create_volumes = True
        volume_count = 4  # Default minimum volume count
        
        if "volumes" in manga_details and isinstance(manga_details["volumes"], list) and manga_details["volumes"]:
            LOGGER.info(f"Importing {len(manga_details['volumes'])} volumes from {provider}")
            for volume in manga_details["volumes"]:
                create_volumes = False  # We're creating them from the provider data
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
        
        # Create default volumes if none provided by the API
        if create_volumes:
            LOGGER.info(f"Creating {volume_count} default volumes since none provided by {provider}")
            start_date = datetime.now() - timedelta(days=volume_count * 90)
            
            for i in range(1, volume_count + 1):
                volume_date = start_date + timedelta(days=i * 90)
                release_date_str = volume_date.strftime("%Y-%m-%d")
                
                try:
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
                            str(i),
                            f"Volume {i}",
                            "",
                            "",
                            release_date_str
                        )
                    )
                    conn.commit()
                    volume_id = cursor.lastrowid
                    
                    if volume_id:
                        volumes[str(i)] = volume_id
                        LOGGER.info(f"Created default volume {i} with date {release_date_str}")
                except Exception as e:
                    LOGGER.error(f"Error creating default volume {i}: {e}")
        
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
            
            # If no matching volume, try to use volume 1
            if volume_id is None and "1" in volumes:
                volume_id = volumes.get("1", None)
            
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
        
        # Link to a collection (selected or default by type)
        try:
            from backend.features.collection import add_series_to_collection, get_default_collection
            target_collection_id = None
            if collection_id:
                try:
                    target_collection_id = int(collection_id)
                except Exception:
                    target_collection_id = None
            if not target_collection_id:
                default_coll = get_default_collection(manga_details.get("content_type", inferred_type))
                if default_coll and default_coll.get("id"):
                    target_collection_id = default_coll["id"]
            if target_collection_id:
                add_series_to_collection(target_collection_id, series_id)
        except Exception as e:
            LOGGER.warning(f"Failed linking series to collection: {e}")

        # Create folder structure for the series
        try:
            from backend.base.helpers import create_series_folder_structure, get_safe_folder_name
            from pathlib import Path
            
            LOGGER.info(f"Creating folder structure for imported series: {manga_details.get('title', 'Unknown')} (ID: {series_id})")
            
            # Get the safe folder name
            safe_title = get_safe_folder_name(manga_details.get('title', 'Unknown'))
            
            # Check if folder already exists in any root folder
            folder_already_exists = False
            existing_folder_path = None
            
            # Get root folders from settings
            from backend.internals.settings import Settings
            settings = Settings().get_settings()
            root_folders = settings.root_folders
            
            if root_folders:
                for root_folder in root_folders:
                    root_path = Path(root_folder['path'])
                    potential_series_dir = root_path / safe_title
                    LOGGER.info(f"Checking if folder already exists: {potential_series_dir}")
                    
                    if potential_series_dir.exists() and potential_series_dir.is_dir():
                        folder_already_exists = True
                        existing_folder_path = potential_series_dir
                        LOGGER.info(f"Found existing folder: {existing_folder_path}")
                        break
            
            # Create the folder if it doesn't exist
            if not folder_already_exists:
                series_path = create_series_folder_structure(
                    series_id,
                    manga_details.get('title', 'Unknown'),
                    manga_details.get('content_type', inferred_type),
                    collection_id,
                    root_folder_id
                )
                LOGGER.info(f"Folder structure created at: {series_path}")
            else:
                series_path = existing_folder_path
                LOGGER.info(f"Using existing folder: {series_path}")
            
            # Add the series to the collection
            # No-op: linking performed above with add_series_to_collection
            
            # If the folder already existed, scan it for e-books
            if folder_already_exists:
                LOGGER.info(f"Scanning existing folder for e-books: {series_path}")
                from backend.features.ebook_files import scan_for_ebooks
                scan_stats = scan_for_ebooks(specific_series_id=series_id)
                LOGGER.info(f"Scan results: {scan_stats}")
        except Exception as e:
            LOGGER.error(f"Error creating folder structure or adding to collection: {e}")
            import traceback
            LOGGER.error(traceback.format_exc())
            # Continue even if folder creation fails
        
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
