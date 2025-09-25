#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collection query functions.
"""

from typing import Dict, List, Optional

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def get_collection_items(
    series_id: Optional[int] = None,
    item_type: Optional[str] = None,
    ownership_status: Optional[str] = None,
    read_status: Optional[str] = None,
    format: Optional[str] = None
) -> List[Dict]:
    """Get collection items with optional filters.
    
    Args:
        series_id: Filter by series ID.
        item_type: Filter by item type.
        ownership_status: Filter by ownership status.
        read_status: Filter by read status.
        format: Filter by format.
        
    Returns:
        List[Dict]: The collection items.
    """
    try:
        query = """
        SELECT 
            ci.*,
            s.title as series_title, s.author as series_author, s.cover_url as series_cover_url,
            v.volume_number, v.title as volume_title,
            c.chapter_number, c.title as chapter_title
        FROM collection_items ci
        LEFT JOIN series s ON ci.series_id = s.id
        LEFT JOIN volumes v ON ci.volume_id = v.id
        LEFT JOIN chapters c ON ci.chapter_id = c.id
        WHERE 1=1
        """
        params = []
        
        if series_id:
            query += " AND ci.series_id = ?"
            params.append(series_id)
        
        if item_type:
            query += " AND ci.item_type = ?"
            params.append(item_type)
        
        if ownership_status:
            query += " AND ci.ownership_status = ?"
            params.append(ownership_status)
        
        if read_status:
            query += " AND ci.read_status = ?"
            params.append(read_status)
        
        if format:
            query += " AND ci.format = ?"
            params.append(format)
        
        query += " ORDER BY s.title, v.volume_number, c.chapter_number"
        
        return execute_query(query, tuple(params))
    
    except Exception as e:
        LOGGER.error(f"Error getting collection items: {e}")
        return []


def export_collection() -> List[Dict]:
    """Export collection data.
    
    Returns:
        List[Dict]: The collection data.
    """
    try:
        return execute_query("""
        SELECT
            id, series_id, volume_id, chapter_id, item_type,
            ownership_status, read_status, format, condition,
            purchase_date, purchase_price, purchase_location,
            notes, custom_tags, created_at, updated_at
        FROM collection_items
        ORDER BY series_id, volume_id, chapter_id
        """)
    
    except Exception as e:
        LOGGER.error(f"Error exporting collection: {e}")
        return []
