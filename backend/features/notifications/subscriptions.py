#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subscription management for notifications.
"""

from typing import Dict, List

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def subscribe_to_series(series_id: int, notify_new_volumes: bool = True, notify_new_chapters: bool = True) -> int:
    """Subscribe to a series.
    
    Args:
        series_id: The series ID.
        notify_new_volumes: Whether to notify for new volumes. Defaults to True.
        notify_new_chapters: Whether to notify for new chapters. Defaults to True.
        
    Returns:
        int: The ID of the created subscription.
    """
    try:
        # Check if series exists
        series = execute_query("SELECT id FROM series WHERE id = ?", (series_id,))
        if not series:
            raise ValueError(f"Series with ID {series_id} not found")
        
        # Check if subscription already exists
        existing = execute_query("SELECT id FROM subscriptions WHERE series_id = ?", (series_id,))
        
        if existing:
            # Update existing subscription
            execute_query("""
            UPDATE subscriptions
            SET notify_new_volumes = ?, notify_new_chapters = ?
            WHERE series_id = ?
            """, (int(notify_new_volumes), int(notify_new_chapters), series_id), commit=True)
            
            return existing[0]['id']
        else:
            # Create new subscription
            subscription_id = execute_query("""
            INSERT INTO subscriptions (series_id, notify_new_volumes, notify_new_chapters)
            VALUES (?, ?, ?)
            """, (series_id, int(notify_new_volumes), int(notify_new_chapters)), commit=True)
            
            return subscription_id
    
    except Exception as e:
        LOGGER.error(f"Error subscribing to series: {e}")
        raise


def unsubscribe_from_series(series_id: int) -> bool:
    """Unsubscribe from a series.
    
    Args:
        series_id: The series ID.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        execute_query("""
        DELETE FROM subscriptions
        WHERE series_id = ?
        """, (series_id,), commit=True)
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error unsubscribing from series: {e}")
        return False


def get_subscriptions() -> List[Dict]:
    """Get all subscriptions.
    
    Returns:
        List[Dict]: The subscriptions.
    """
    try:
        return execute_query("""
        SELECT 
            s.id, s.series_id, s.notify_new_volumes, s.notify_new_chapters, s.created_at,
            series.title as series_title, series.author as series_author, series.cover_url as series_cover_url
        FROM subscriptions s
        JOIN series ON s.series_id = series.id
        ORDER BY series.title
        """)
    
    except Exception as e:
        LOGGER.error(f"Error getting subscriptions: {e}")
        return []


def is_subscribed(series_id: int) -> bool:
    """Check if a series is subscribed to.
    
    Args:
        series_id: The series ID.
        
    Returns:
        bool: True if subscribed, False otherwise.
    """
    try:
        result = execute_query("SELECT id FROM subscriptions WHERE series_id = ?", (series_id,))
        return len(result) > 0
    
    except Exception as e:
        LOGGER.error(f"Error checking subscription: {e}")
        return False
