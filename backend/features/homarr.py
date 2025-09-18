#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from backend.base.logging import LOGGER
from backend.features.calendar import get_calendar_events
from backend.internals.db import execute_query


def get_homarr_data() -> Dict:
    """Get data for Homarr integration.
    
    Returns:
        Dict: The Homarr data.
    """
    try:
        # Get upcoming releases for today
        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        today_events = get_calendar_events(today, today)
        
        # Get series count
        series_count = execute_query("SELECT COUNT(*) as count FROM series")
        
        # Get volume count
        volume_count = execute_query("SELECT COUNT(*) as count FROM volumes")
        
        # Get chapter count
        chapter_count = execute_query("SELECT COUNT(*) as count FROM chapters")
        
        # Get owned volumes count
        owned_volumes = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'VOLUME' AND ownership_status = 'OWNED'
        """)
        
        # Get collection value
        collection_value = execute_query("""
        SELECT SUM(purchase_price) as total
        FROM collection_items
        WHERE purchase_price IS NOT NULL
        """)
        
        # Get app version
        app_version = "1.0.0"  # This should be retrieved from a central version file
        
        # Determine status
        status = "ok"
        
        # Format data for Homarr
        data = {
            "app": "MangaArr",
            "version": app_version,
            "status": status,
            "info": {
                "series_count": series_count[0]["count"],
                "volume_count": volume_count[0]["count"],
                "chapter_count": chapter_count[0]["count"],
                "owned_volumes": owned_volumes[0]["count"] if owned_volumes else 0,
                "collection_value": collection_value[0]["total"] if collection_value and collection_value[0]["total"] else 0,
                "releases_today": len(today_events)
            }
        }
        
        return data
    
    except Exception as e:
        LOGGER.error(f"Error getting Homarr data: {e}")
        return {
            "app": "MangaArr",
            "version": "1.0.0",
            "status": "error",
            "error": str(e)
        }


def get_homarr_setup_instructions() -> Dict:
    """Get Homarr setup instructions.
    
    Returns:
        Dict: The Homarr setup instructions.
    """
    try:
        # Get base URL from settings
        settings = execute_query("SELECT value FROM settings WHERE key = 'base_url'")
        base_url = settings[0]["value"] if settings else "http://localhost:7227"
        
        # Format instructions
        instructions = {
            "title": "MangaArr Homarr Integration",
            "description": "Follow these steps to integrate MangaArr with your Homarr dashboard.",
            "base_url": base_url,
            "api_endpoint": f"{base_url}/api/integrations/homarr",
            "steps": [
                {
                    "title": "Add MangaArr to Homarr",
                    "description": "In your Homarr dashboard, add MangaArr as a service with the following configuration:",
                    "fields": [
                        {
                            "name": "Name",
                            "value": "MangaArr"
                        },
                        {
                            "name": "Icon",
                            "value": "fas fa-book"
                        },
                        {
                            "name": "URL",
                            "value": base_url
                        },
                        {
                            "name": "Status Endpoint",
                            "value": "/api/integrations/homarr"
                        }
                    ]
                }
            ],
            "notes": [
                "Make sure your Homarr instance can reach your MangaArr instance at the base URL.",
                "The status endpoint will return information about your MangaArr instance, including the number of series, volumes, and chapters.",
                "Homarr will display the number of releases today in the dashboard."
            ]
        }
        
        return instructions
    
    except Exception as e:
        LOGGER.error(f"Error generating Homarr setup instructions: {e}")
        return {"error": str(e)}
