#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

from backend.base.definitions import ReleaseStatus
from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from backend.internals.settings import Settings


def update_calendar() -> None:
    """Update the calendar with upcoming releases."""
    try:
        settings = Settings().get_settings()
        
        # Get all series that we're tracking
        series_list = execute_query("SELECT id, title FROM series")
        
        for series in series_list:
            series_id = series["id"]
            
            # Check for upcoming volume releases
            volumes = execute_query(
                """
                SELECT id, volume_number, title, release_date 
                FROM volumes 
                WHERE series_id = ? AND release_date IS NOT NULL
                """,
                (series_id,)
            )
            
            for volume in volumes:
                try:
                    release_date = datetime.fromisoformat(volume["release_date"])
                    
                    # Only add to calendar if it's within our range
                    now = datetime.now()
                    if now - timedelta(days=7) <= release_date <= now + timedelta(days=settings.calendar_range_days):
                        # Check if this event already exists
                        existing = execute_query(
                            """
                            SELECT id FROM calendar_events 
                            WHERE series_id = ? AND volume_id = ? AND event_date = ?
                            """,
                            (series_id, volume["id"], volume["release_date"])
                        )
                        
                        if not existing:
                            # Create new calendar event
                            execute_query(
                                """
                                INSERT INTO calendar_events 
                                (series_id, volume_id, title, description, event_date, event_type) 
                                VALUES (?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    series_id,
                                    volume["id"],
                                    f"Volume {volume['volume_number']} - {series['title']}",
                                    f"Release of volume {volume['volume_number']}: {volume['title']}",
                                    volume["release_date"],
                                    "VOLUME_RELEASE"
                                ),
                                commit=True
                            )
                except (ValueError, TypeError):
                    # Skip invalid dates
                    continue
            
            # Check for upcoming chapter releases
            chapters = execute_query(
                """
                SELECT id, chapter_number, title, release_date 
                FROM chapters 
                WHERE series_id = ? AND release_date IS NOT NULL
                """,
                (series_id,)
            )
            
            for chapter in chapters:
                try:
                    release_date = datetime.fromisoformat(chapter["release_date"])
                    
                    # Only add to calendar if it's within our range
                    now = datetime.now()
                    if now - timedelta(days=7) <= release_date <= now + timedelta(days=settings.calendar_range_days):
                        # Check if this event already exists
                        existing = execute_query(
                            """
                            SELECT id FROM calendar_events 
                            WHERE series_id = ? AND chapter_id = ? AND event_date = ?
                            """,
                            (series_id, chapter["id"], chapter["release_date"])
                        )
                        
                        if not existing:
                            # Create new calendar event
                            execute_query(
                                """
                                INSERT INTO calendar_events 
                                (series_id, chapter_id, title, description, event_date, event_type) 
                                VALUES (?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    series_id,
                                    chapter["id"],
                                    f"Chapter {chapter['chapter_number']} - {series['title']}",
                                    f"Release of chapter {chapter['chapter_number']}: {chapter['title']}",
                                    chapter["release_date"],
                                    "CHAPTER_RELEASE"
                                ),
                                commit=True
                            )
                except (ValueError, TypeError):
                    # Skip invalid dates
                    continue
        
        # Clean up old events
        execute_query(
            """
            DELETE FROM calendar_events 
            WHERE event_date < date('now', '-7 days')
            """,
            commit=True
        )
        
        LOGGER.info("Calendar updated successfully")
    except Exception as e:
        LOGGER.error(f"Error updating calendar: {e}")


def get_calendar_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    series_id: Optional[int] = None
) -> List[Dict]:
    """Get calendar events.

    Args:
        start_date (Optional[str], optional): The start date in ISO format.
            Defaults to None.
        end_date (Optional[str], optional): The end date in ISO format.
            Defaults to None.
        series_id (Optional[int], optional): The series ID to filter by.
            Defaults to None.

    Returns:
        List[Dict]: The calendar events.
    """
    query = """
    SELECT 
        ce.id, ce.title, ce.description, ce.event_date, ce.event_type,
        s.id as series_id, s.title as series_title, s.cover_url as series_cover_url,
        v.id as volume_id, v.volume_number, v.title as volume_title,
        c.id as chapter_id, c.chapter_number, c.title as chapter_title
    FROM calendar_events ce
    LEFT JOIN series s ON ce.series_id = s.id
    LEFT JOIN volumes v ON ce.volume_id = v.id
    LEFT JOIN chapters c ON ce.chapter_id = c.id
    WHERE 1=1
    """
    params = []
    
    if start_date:
        query += " AND ce.event_date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND ce.event_date <= ?"
        params.append(end_date)
    
    if series_id:
        query += " AND ce.series_id = ?"
        params.append(series_id)
    
    query += " ORDER BY ce.event_date ASC"
    
    events = execute_query(query, tuple(params))
    
    # Format the events for the frontend
    formatted_events = []
    for event in events:
        formatted_event = {
            "id": event["id"],
            "title": event["title"],
            "description": event["description"],
            "date": event["event_date"],
            "type": event["event_type"],
            "series": {
                "id": event["series_id"],
                "title": event["series_title"],
                "cover_url": event["series_cover_url"]
            }
        }
        
        if event["volume_id"]:
            formatted_event["volume"] = {
                "id": event["volume_id"],
                "number": event["volume_number"],
                "title": event["volume_title"]
            }
        
        if event["chapter_id"]:
            formatted_event["chapter"] = {
                "id": event["chapter_id"],
                "number": event["chapter_number"],
                "title": event["chapter_title"]
            }
        
        formatted_events.append(formatted_event)
    
    return formatted_events
