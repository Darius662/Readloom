#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Caching helpers for metadata_service.
"""

import json
from datetime import datetime
from typing import Any, Optional

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


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
        json_data = json.dumps(data)

        existing = execute_query(
            "SELECT id FROM metadata_cache WHERE id = ? AND type = ?",
            (id, type),
        )

        if existing:
            execute_query(
                "UPDATE metadata_cache SET data = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ? AND type = ?",
                (json_data, id, type),
            )
        else:
            execute_query(
                "INSERT INTO metadata_cache (id, provider, type, data) VALUES (?, ?, ?, ?)",
                (id, id.split('_')[0], type, json_data),
            )

        return True
    except Exception as e:
        LOGGER.error(f"Error saving to cache: {e}")
        return False


def get_from_cache(id: str, type: str) -> Optional[Any]:
    """Get data from the metadata cache.

    Args:
        id: The cache ID.
        type: The cache type.

    Returns:
        The cached data, or None if not found.
    """
    try:
        cache_entry = execute_query(
            "SELECT data, timestamp FROM metadata_cache WHERE id = ? AND type = ?",
            (id, type),
        )

        if not cache_entry:
            return None

        cache_time = datetime.fromisoformat(cache_entry[0]["timestamp"])  # type: ignore[index]
        current_time = datetime.now()

        if (current_time - cache_time).days > 7:
            execute_query(
                "DELETE FROM metadata_cache WHERE id = ? AND type = ?",
                (id, type),
            )
            return None

        return json.loads(cache_entry[0]["data"])  # type: ignore[index]
    except Exception as e:
        LOGGER.error(f"Error getting from cache: {e}")
        return None


def clear_cache(provider: Optional[str] = None, type: Optional[str] = None):
    """Clear entries from the metadata cache."""
    try:
        if provider and type:
            execute_query(
                "DELETE FROM metadata_cache WHERE provider = ? AND type = ?",
                (provider, type),
            )
        elif provider:
            execute_query(
                "DELETE FROM metadata_cache WHERE provider = ?",
                (provider,),
            )
        elif type:
            execute_query(
                "DELETE FROM metadata_cache WHERE type = ?",
                (type,),
            )
        else:
            execute_query("DELETE FROM metadata_cache")

        return {
            "success": True,
            "message": "Cache cleared successfully",
        }
    except Exception as e:
        LOGGER.error(f"Error clearing cache: {e}")
        return {
            "success": False,
            "message": str(e),
        }
