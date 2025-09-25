#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup for metadata providers.
"""

from typing import Dict, Any, Optional
import json

from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from .base import metadata_provider_manager
# Import providers from their respective packages
from .myanimelist import MyAnimeListProvider
from .manga_api import MangaAPIProvider
from .mangadex import MangaDexProvider
from .jikan import JikanProvider
from .anilist import AniListProvider
from .mangafire import MangaFireProvider
# Import new providers
from .googlebooks import GoogleBooksProvider
from .openlibrary import OpenLibraryProvider
from .isbndb import ISBNdbProvider
from .worldcat import WorldCatProvider


def load_provider_settings() -> Dict[str, Any]:
    """Load provider settings from the database.
    
    Returns:
        A dictionary of provider settings.
    """
    try:
        # Check if the metadata_providers table exists
        table_check = execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='metadata_providers'"
        )
        
        if not table_check:
            # Create the table if it doesn't exist
            execute_query("""
                CREATE TABLE metadata_providers (
                    name TEXT PRIMARY KEY,
                    enabled INTEGER DEFAULT 1,
                    settings TEXT
                )
            """)
            
            # Insert default settings
            default_providers = {
                "MyAnimeList": {"enabled": 0, "settings": {"client_id": ""}},
                "MangaAPI": {"enabled": 0, "settings": {"api_url": "https://manga-api.fly.dev"}},
                "AniList": {"enabled": 1, "settings": {}},
                "MangaDex": {"enabled": 0, "settings": {}},
                "MangaFire": {"enabled": 0, "settings": {}},
                "Jikan": {"enabled": 0, "settings": {}},
                "GoogleBooks": {"enabled": 1, "settings": {"api_key": ""}},
                "OpenLibrary": {"enabled": 0, "settings": {}},
                "ISBNdb": {"enabled": 0, "settings": {"api_key": ""}},
                "WorldCat": {"enabled": 0, "settings": {"api_key": ""}}
            }
            
            for name, config in default_providers.items():
                execute_query(
                    "INSERT INTO metadata_providers (name, enabled, settings) VALUES (?, ?, ?)",
                    (name, config["enabled"], json.dumps(config["settings"]))
                )
        
        # Load settings from the database
        providers_data = execute_query("SELECT name, enabled, settings FROM metadata_providers")
        
        settings = {}
        for provider in providers_data:
            settings[provider["name"]] = {
                "enabled": bool(provider["enabled"]),
                "settings": json.loads(provider["settings"])
            }
        
        return settings
    except Exception as e:
        LOGGER.error(f"Error loading provider settings: {e}")
        return {}


def save_provider_settings(name: str, enabled: bool, settings: Dict[str, Any]) -> bool:
    """Save provider settings to the database.
    
    Args:
        name: The provider name.
        enabled: Whether the provider is enabled.
        settings: The provider settings.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        execute_query(
            "UPDATE metadata_providers SET enabled = ?, settings = ? WHERE name = ?",
            (1 if enabled else 0, json.dumps(settings), name)
        )
        return True
    except Exception as e:
        LOGGER.error(f"Error saving provider settings: {e}")
        return False


def initialize_providers() -> None:
    """Initialize and register all metadata providers."""
    try:
        # Load provider settings
        settings = load_provider_settings()
        
        # MangaFire provider has been removed
        
        # Initialize MyAnimeList provider via direct API
        mal_config = settings.get("MyAnimeList", {"enabled": True, "settings": {"client_id": ""}})
        mal_provider = MyAnimeListProvider(
            enabled=False,  # Disable the direct MAL provider as we'll use Jikan instead
            client_id=mal_config["settings"].get("client_id", "")
        )
        metadata_provider_manager.register_provider(mal_provider)
        
        # Initialize MangaAPI provider
        manga_api_config = settings.get("MangaAPI", {"enabled": False, "settings": {"api_url": "https://manga-api.fly.dev"}})
        manga_api_provider = MangaAPIProvider(
            enabled=manga_api_config["enabled"],
            api_url=manga_api_config["settings"].get("api_url", "https://manga-api.fly.dev")
        )
        metadata_provider_manager.register_provider(manga_api_provider)
        
        # Initialize MangaDex provider
        mangadex_config = settings.get("MangaDex", {"enabled": False, "settings": {}})
        mangadex_provider = MangaDexProvider(enabled=mangadex_config["enabled"])
        metadata_provider_manager.register_provider(mangadex_provider)
        
        # Initialize Jikan provider for MyAnimeList
        jikan_config = settings.get("Jikan", {"enabled": False, "settings": {}})
        jikan_provider = JikanProvider(enabled=jikan_config["enabled"])
        metadata_provider_manager.register_provider(jikan_provider)
        
        # Initialize AniList provider
        anilist_config = settings.get("AniList", {"enabled": True, "settings": {}})
        anilist_provider = AniListProvider(enabled=anilist_config["enabled"])
        metadata_provider_manager.register_provider(anilist_provider)
        
        # Initialize MangaFire provider
        mangafire_config = settings.get("MangaFire", {"enabled": False, "settings": {}})
        mangafire_provider = MangaFireProvider(enabled=mangafire_config["enabled"])
        metadata_provider_manager.register_provider(mangafire_provider)
        
        # Initialize Google Books provider
        googlebooks_config = settings.get("GoogleBooks", {"enabled": False, "settings": {"api_key": ""}})
        googlebooks_provider = GoogleBooksProvider(
            enabled=googlebooks_config["enabled"],
            api_key=googlebooks_config["settings"].get("api_key", "")
        )
        metadata_provider_manager.register_provider(googlebooks_provider)
        
        # Initialize Open Library provider
        openlibrary_config = settings.get("OpenLibrary", {"enabled": False, "settings": {}})
        openlibrary_provider = OpenLibraryProvider(enabled=openlibrary_config["enabled"])
        metadata_provider_manager.register_provider(openlibrary_provider)
        
        # Initialize ISBNdb provider
        isbndb_config = settings.get("ISBNdb", {"enabled": False, "settings": {"api_key": ""}})
        isbndb_provider = ISBNdbProvider(
            enabled=isbndb_config["enabled"],
            api_key=isbndb_config["settings"].get("api_key", "")
        )
        metadata_provider_manager.register_provider(isbndb_provider)
        
        # Initialize WorldCat provider
        worldcat_config = settings.get("WorldCat", {"enabled": False, "settings": {"api_key": ""}})
        worldcat_provider = WorldCatProvider(
            enabled=worldcat_config["enabled"],
            api_key=worldcat_config["settings"].get("api_key", "")
        )
        metadata_provider_manager.register_provider(worldcat_provider)
        
        LOGGER.info(f"Initialized {len(metadata_provider_manager.get_all_providers())} metadata providers")
    except Exception as e:
        LOGGER.error(f"Error initializing metadata providers: {e}")


def get_provider_settings() -> Dict[str, Any]:
    """Get all provider settings.
    
    Returns:
        A dictionary of provider settings.
    """
    providers = metadata_provider_manager.get_all_providers()
    
    settings = {}
    for provider in providers:
        provider_settings = {}
        
        if provider.name == "MyAnimeList":
            provider_settings["client_id"] = getattr(provider, "client_id", "")
        elif provider.name == "MangaAPI":
            provider_settings["api_url"] = getattr(provider, "api_url", "https://manga-api.fly.dev")
        elif provider.name == "GoogleBooks":
            provider_settings["api_key"] = getattr(provider, "api_key", "")
        elif provider.name == "ISBNdb":
            provider_settings["api_key"] = getattr(provider, "api_key", "")
        elif provider.name == "WorldCat":
            provider_settings["api_key"] = getattr(provider, "api_key", "")
        
        settings[provider.name] = {
            "enabled": provider.enabled,
            "settings": provider_settings
        }
    
    return settings


def update_provider_settings(name: str, enabled: bool, settings: Dict[str, Any]) -> bool:
    """Update provider settings.
    
    Args:
        name: The provider name.
        enabled: Whether the provider is enabled.
        settings: The provider settings.
        
    Returns:
        True if successful, False otherwise.
    """
    provider = metadata_provider_manager.get_provider(name)
    if not provider:
        LOGGER.error(f"Provider not found: {name}")
        return False
    
    try:
        # Update provider instance
        provider.enabled = enabled
        
        if name == "MyAnimeList" and "client_id" in settings:
            provider.client_id = settings["client_id"]
            provider.headers["X-MAL-CLIENT-ID"] = settings["client_id"]
        elif name == "MangaAPI" and "api_url" in settings:
            provider.api_url = settings["api_url"]
        elif name == "GoogleBooks" and "api_key" in settings:
            provider.api_key = settings["api_key"]
        elif name == "ISBNdb" and "api_key" in settings:
            provider.api_key = settings["api_key"]
            provider.headers["Authorization"] = settings["api_key"]
        elif name == "WorldCat" and "api_key" in settings:
            provider.api_key = settings["api_key"]
        
        # Save to database
        return save_provider_settings(name, enabled, settings)
    except Exception as e:
        LOGGER.error(f"Error updating provider settings: {e}")
        return False
