#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Home Assistant configuration generator.
"""

import json
from typing import Dict

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def generate_home_assistant_config() -> Dict:
    """Generate Home Assistant configuration.
    
    Returns:
        Dict: The Home Assistant configuration.
    """
    try:
        # Get base URL from settings
        settings = execute_query("SELECT value FROM settings WHERE key = 'base_url'")
        base_url = settings[0]["value"] if settings else "http://localhost:7227"
        
        # Generate configuration
        config = {
            "sensor": [
                {
                    "platform": "rest",
                    "name": "mangarr_stats",
                    "resource": f"{base_url}/api/integrations/home-assistant",
                    "scan_interval": 300,
                    "json_attributes_path": "$.stats",
                    "json_attributes": [
                        "series_count",
                        "volume_count",
                        "chapter_count",
                        "owned_volumes",
                        "read_volumes",
                        "collection_value"
                    ],
                    "value_template": "{{ value_json.stats.series_count }}"
                },
                {
                    "platform": "rest",
                    "name": "mangarr_releases",
                    "resource": f"{base_url}/api/integrations/home-assistant",
                    "scan_interval": 300,
                    "json_attributes_path": "$",
                    "json_attributes": [
                        "releases_today",
                        "releases_this_week",
                        "last_updated"
                    ],
                    "value_template": "{{ value_json.releases_today }}"
                }
            ],
            "automation": [
                {
                    "alias": "MangaArr Daily Release Notification",
                    "description": "Send a notification when there are new manga/comic releases today",
                    "trigger": {
                        "platform": "state",
                        "entity_id": "sensor.mangarr_releases",
                        "attribute": "releases_today"
                    },
                    "condition": {
                        "condition": "numeric_state",
                        "entity_id": "sensor.mangarr_releases",
                        "attribute": "releases_today",
                        "above": 0
                    },
                    "action": {
                        "service": "notify.mobile_app",
                        "data": {
                            "title": "MangaArr - New Releases Today",
                            "message": "{{ states.sensor.mangarr_releases.attributes.releases_today }} new manga/comic releases today!"
                        }
                    }
                }
            ],
            "lovelace": {
                "title": "MangaArr",
                "cards": [
                    {
                        "type": "entities",
                        "title": "MangaArr Collection",
                        "entities": [
                            {
                                "entity": "sensor.mangarr_stats",
                                "name": "Series Count",
                                "icon": "mdi:book-multiple"
                            },
                            {
                                "entity": "sensor.mangarr_stats",
                                "name": "Volume Count",
                                "icon": "mdi:book",
                                "attribute": "volume_count"
                            },
                            {
                                "entity": "sensor.mangarr_stats",
                                "name": "Chapter Count",
                                "icon": "mdi:file-document",
                                "attribute": "chapter_count"
                            },
                            {
                                "entity": "sensor.mangarr_stats",
                                "name": "Owned Volumes",
                                "icon": "mdi:bookshelf",
                                "attribute": "owned_volumes"
                            },
                            {
                                "entity": "sensor.mangarr_stats",
                                "name": "Read Volumes",
                                "icon": "mdi:book-open-variant",
                                "attribute": "read_volumes"
                            },
                            {
                                "entity": "sensor.mangarr_stats",
                                "name": "Collection Value",
                                "icon": "mdi:currency-usd",
                                "attribute": "collection_value"
                            }
                        ]
                    },
                    {
                        "type": "entity",
                        "entity": "sensor.mangarr_releases",
                        "name": "Releases Today",
                        "icon": "mdi:calendar-today"
                    },
                    {
                        "type": "entity",
                        "entity": "sensor.mangarr_releases",
                        "name": "Releases This Week",
                        "icon": "mdi:calendar-week",
                        "attribute": "releases_this_week"
                    }
                ]
            }
        }
        
        return config
    
    except Exception as e:
        LOGGER.error(f"Error generating Home Assistant configuration: {e}")
        return {"error": str(e)}


def get_home_assistant_setup_instructions() -> Dict:
    """Get Home Assistant setup instructions.
    
    Returns:
        Dict: The Home Assistant setup instructions.
    """
    try:
        # Get base URL from settings
        settings = execute_query("SELECT value FROM settings WHERE key = 'base_url'")
        base_url = settings[0]["value"] if settings else "http://localhost:7227"
        
        # Generate configuration
        config = generate_home_assistant_config()
        
        # Format instructions
        instructions = {
            "title": "MangaArr Home Assistant Integration",
            "description": "Follow these steps to integrate MangaArr with your Home Assistant instance.",
            "base_url": base_url,
            "api_endpoint": f"{base_url}/api/integrations/home-assistant",
            "steps": [
                {
                    "title": "Add REST Sensors",
                    "description": "Add the following configuration to your Home Assistant configuration.yaml file:",
                    "code": "sensor:\n" + json.dumps(config["sensor"], indent=2)
                },
                {
                    "title": "Add Automation (Optional)",
                    "description": "Add the following automation to get notifications for new releases:",
                    "code": "automation:\n" + json.dumps(config["automation"], indent=2)
                },
                {
                    "title": "Add Lovelace Dashboard (Optional)",
                    "description": "Create a new dashboard with the following cards:",
                    "code": json.dumps(config["lovelace"]["cards"], indent=2)
                }
            ],
            "notes": [
                "Make sure your Home Assistant instance can reach your MangaArr instance at the base URL.",
                "Adjust the scan_interval value (in seconds) based on your needs.",
                "Customize the automation to use your preferred notification service."
            ]
        }
        
        return instructions
    
    except Exception as e:
        LOGGER.error(f"Error generating Home Assistant setup instructions: {e}")
        return {"error": str(e)}
