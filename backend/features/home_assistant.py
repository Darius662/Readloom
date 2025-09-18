#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from backend.base.logging import LOGGER
from backend.features.calendar import get_calendar_events
from backend.internals.db import execute_query


def get_home_assistant_sensor_data() -> Dict:
    """Get data for Home Assistant sensors.
    
    Returns:
        Dict: The Home Assistant sensor data.
    """
    try:
        # Get upcoming releases for the next 7 days
        today = datetime.now().strftime('%Y-%m-%d')
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        events = get_calendar_events(today, next_week)
        
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
        
        # Get read volumes count
        read_volumes = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'VOLUME' AND read_status = 'READ'
        """)
        
        # Get collection value
        collection_value = execute_query("""
        SELECT SUM(purchase_price) as total
        FROM collection_items
        WHERE purchase_price IS NOT NULL
        """)
        
        # Group events by date
        events_by_date = {}
        for event in events:
            date = event['date']
            if date not in events_by_date:
                events_by_date[date] = []
            events_by_date[date].append(event)
        
        # Format data for Home Assistant
        data = {
            "stats": {
                "series_count": series_count[0]["count"],
                "volume_count": volume_count[0]["count"],
                "chapter_count": chapter_count[0]["count"],
                "owned_volumes": owned_volumes[0]["count"] if owned_volumes else 0,
                "read_volumes": read_volumes[0]["count"] if read_volumes else 0,
                "collection_value": collection_value[0]["total"] if collection_value and collection_value[0]["total"] else 0
            },
            "upcoming_releases": events,
            "releases_by_date": events_by_date,
            "releases_today": len(events_by_date.get(today, [])),
            "releases_this_week": len(events),
            "last_updated": datetime.now().isoformat()
        }
        
        return data
    
    except Exception as e:
        LOGGER.error(f"Error getting Home Assistant sensor data: {e}")
        return {
            "error": str(e),
            "last_updated": datetime.now().isoformat()
        }


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
