#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Home Assistant sensor data provider.
"""

from datetime import datetime, timedelta
from typing import Dict, List

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
