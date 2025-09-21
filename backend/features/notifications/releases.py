#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Release notification management.
"""

from datetime import datetime, timedelta
from typing import Dict, List

from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from .settings import get_notification_settings
from .subscriptions import get_subscriptions
from .notifications import send_notification


def check_upcoming_releases() -> List[Dict]:
    """Check for upcoming releases and send notifications if needed.
    
    Returns:
        List[Dict]: The upcoming releases that were notified about.
    """
    try:
        settings = get_notification_settings()
        days_before = settings.get('notify_releases_days_before', 1)
        
        # Get date range
        today = datetime.now().strftime('%Y-%m-%d')
        future_date = (datetime.now() + timedelta(days=days_before)).strftime('%Y-%m-%d')
        
        # Get subscribed series
        subscriptions = get_subscriptions()
        subscribed_series_ids = [sub['series_id'] for sub in subscriptions]
        
        if not subscribed_series_ids:
            return []
        
        # Get upcoming volume releases
        upcoming_volumes = []
        if settings.get('notify_new_volumes', True):
            volume_query = """
            SELECT 
                v.id, v.series_id, v.volume_number, v.title, v.release_date,
                s.title as series_title, s.author as series_author
            FROM volumes v
            JOIN series s ON v.series_id = s.id
            WHERE v.series_id IN ({}) AND v.release_date BETWEEN ? AND ?
            """.format(','.join('?' * len(subscribed_series_ids)))
            
            upcoming_volumes = execute_query(
                volume_query,
                tuple(subscribed_series_ids) + (today, future_date)
            )
        
        # Get upcoming chapter releases
        upcoming_chapters = []
        if settings.get('notify_new_chapters', True):
            chapter_query = """
            SELECT 
                c.id, c.series_id, c.volume_id, c.chapter_number, c.title, c.release_date,
                s.title as series_title, s.author as series_author
            FROM chapters c
            JOIN series s ON c.series_id = s.id
            WHERE c.series_id IN ({}) AND c.release_date BETWEEN ? AND ?
            """.format(','.join('?' * len(subscribed_series_ids)))
            
            upcoming_chapters = execute_query(
                chapter_query,
                tuple(subscribed_series_ids) + (today, future_date)
            )
        
        # Send notifications for upcoming releases
        notified_releases = []
        
        for volume in upcoming_volumes:
            # Check if this series subscription has volume notifications enabled
            for sub in subscriptions:
                if sub['series_id'] == volume['series_id'] and sub['notify_new_volumes']:
                    # Send notification
                    release_date = datetime.fromisoformat(volume['release_date']).strftime('%Y-%m-%d')
                    title = f"Upcoming Volume Release: {volume['series_title']}"
                    message = f"Volume {volume['volume_number']} of {volume['series_title']} will be released on {release_date}."
                    
                    send_notification(title, message, 'INFO')
                    notified_releases.append(volume)
                    break
        
        for chapter in upcoming_chapters:
            # Check if this series subscription has chapter notifications enabled
            for sub in subscriptions:
                if sub['series_id'] == chapter['series_id'] and sub['notify_new_chapters']:
                    # Send notification
                    release_date = datetime.fromisoformat(chapter['release_date']).strftime('%Y-%m-%d')
                    title = f"Upcoming Chapter Release: {chapter['series_title']}"
                    message = f"Chapter {chapter['chapter_number']} of {chapter['series_title']} will be released on {release_date}."
                    
                    send_notification(title, message, 'INFO')
                    notified_releases.append(chapter)
                    break
        
        return notified_releases
    
    except Exception as e:
        LOGGER.error(f"Error checking upcoming releases: {e}")
        return []
