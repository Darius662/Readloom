#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collection statistics functions.
"""

from typing import Dict

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def get_collection_stats() -> Dict:
    """Get collection statistics.
    
    Returns:
        Dict: The collection statistics.
    """
    try:
        stats = execute_query("SELECT * FROM collection_stats WHERE user_id = 1")
        
        if stats:
            return stats[0]
        
        return {}
    
    except Exception as e:
        LOGGER.error(f"Error getting collection stats: {e}")
        return {}


def update_collection_stats() -> bool:
    """Update collection statistics.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Count total series, volumes, and chapters
        total_series = execute_query("""
        SELECT COUNT(DISTINCT series_id) as count
        FROM collection_items
        """)
        
        total_volumes = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'VOLUME'
        """)
        
        total_chapters = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'CHAPTER'
        """)
        
        # Count owned series, volumes, and chapters
        owned_series = execute_query("""
        SELECT COUNT(DISTINCT series_id) as count
        FROM collection_items
        WHERE ownership_status = 'OWNED'
        """)
        
        owned_volumes = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'VOLUME' AND ownership_status = 'OWNED'
        """)
        
        owned_chapters = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'CHAPTER' AND ownership_status = 'OWNED'
        """)
        
        # Count read volumes and chapters
        read_volumes = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'VOLUME' AND read_status = 'READ'
        """)
        
        read_chapters = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'CHAPTER' AND read_status = 'READ'
        """)
        
        # Calculate total value
        total_value = execute_query("""
        SELECT SUM(purchase_price) as total
        FROM collection_items
        WHERE purchase_price IS NOT NULL
        """)
        
        # Update stats
        execute_query("""
        UPDATE collection_stats
        SET
            total_series = ?,
            total_volumes = ?,
            total_chapters = ?,
            owned_series = ?,
            owned_volumes = ?,
            owned_chapters = ?,
            read_volumes = ?,
            read_chapters = ?,
            total_value = ?,
            last_updated = CURRENT_TIMESTAMP
        WHERE user_id = 1
        """, (
            total_series[0]['count'] if total_series else 0,
            total_volumes[0]['count'] if total_volumes else 0,
            total_chapters[0]['count'] if total_chapters else 0,
            owned_series[0]['count'] if owned_series else 0,
            owned_volumes[0]['count'] if owned_volumes else 0,
            owned_chapters[0]['count'] if owned_chapters else 0,
            read_volumes[0]['count'] if read_volumes else 0,
            read_chapters[0]['count'] if read_chapters else 0,
            total_value[0]['total'] if total_value and total_value[0]['total'] else 0.0
        ), commit=True)
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error updating collection stats: {e}")
        return False
