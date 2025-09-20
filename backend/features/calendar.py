#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

from backend.base.definitions import ReleaseStatus
from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from backend.internals.settings import Settings


def update_calendar(series_id: Optional[int] = None) -> None:
    """Update the calendar with upcoming releases.
    
    Args:
        series_id: Optional series ID to update only one specific series.
                  If None, updates all series in the collection.
    """
    try:
        settings = Settings().get_settings()
        
        # Get either a specific series or all series that we're tracking
        if series_id is not None:
            series_list = execute_query("SELECT id, title FROM series WHERE id = ?", (series_id,))
            LOGGER.info(f"Updating calendar for specific series ID: {series_id}")
        else:
            series_list = execute_query("SELECT id, title FROM series")
            LOGGER.info(f"Updating calendar for all {len(series_list)} series")
        
        # If updating a specific series, first remove its existing calendar entries
        if series_id is not None:
            execute_query(
                "DELETE FROM calendar_events WHERE series_id = ?",
                (series_id,),
                commit=True
            )
            LOGGER.info(f"Cleared existing calendar events for series ID: {series_id}")
        
        for series in series_list:
            series_id = series["id"]
            
            # Check for upcoming volume releases
            volumes = execute_query(
                """
                SELECT id, volume_number, title, release_date,
                       (SELECT metadata_source FROM series WHERE id = ?) as provider 
                FROM volumes 
                WHERE series_id = ? AND release_date IS NOT NULL
                """,
                (series_id, series_id)
            )
            
            for volume in volumes:
                try:
                    release_date = datetime.fromisoformat(volume["release_date"])
                    
                    # Check if this is from AniList (which needs special handling)
                    provider = volume.get('provider', '')
                    is_anilist = provider == 'AniList'
                    
                    # For normal providers, only include upcoming releases
                    now = datetime.now()
                    upcoming_days = settings.calendar_range_days  # Use the calendar range from settings
                    
                    # Include all AniList volumes or only upcoming ones for other providers
                    is_valid_for_calendar = is_anilist or (release_date >= now and release_date <= now + timedelta(days=upcoming_days))
                    
                    # If it's a valid entry for the calendar, add it
                    if is_valid_for_calendar:
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
            
            # Check for all chapter releases with dates
            chapters = execute_query(
                """
                SELECT id, chapter_number, title, release_date, 
                       (SELECT metadata_source FROM series WHERE id = ?) as provider
                FROM chapters 
                WHERE series_id = ? AND release_date IS NOT NULL
                """,
                (series_id, series_id)
            )
            
            for chapter in chapters:
                try:
                    # Debug logging
                    LOGGER.info(f"Processing chapter: {chapter.get('id')} - {chapter.get('chapter_number')} - {chapter.get('title')} - Date: {chapter.get('release_date')}")
                    
                    # Check if release_date is valid
                    if not chapter.get("release_date"):
                        LOGGER.warning(f"Missing release date for chapter {chapter.get('chapter_number')} in series {series_id}")
                        continue
                    
                    try:
                        release_date = datetime.fromisoformat(chapter["release_date"])
                    except ValueError:
                        LOGGER.warning(f"Invalid date format for chapter {chapter.get('chapter_number')}: {chapter.get('release_date')}")
                        continue
                    
                    # Check if this is from AniList (which needs special handling)
                    provider = chapter.get('provider', '')
                    is_anilist = provider == 'AniList'
                    
                    # For normal providers, only include upcoming releases
                    now = datetime.now()
                    upcoming_days = settings.calendar_range_days  # Use the calendar range from settings
                    
                    # Include all AniList chapters or only upcoming ones for other providers
                    is_valid_for_calendar = is_anilist or (release_date >= now and release_date <= now + timedelta(days=upcoming_days))
                    
                    # If it's a valid entry for the calendar, add it
                    if is_valid_for_calendar:
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
                            event_title = f"Chapter {chapter['chapter_number']} - {series['title']}"
                            event_desc = f"Release of chapter {chapter['chapter_number']}: {chapter['title']}"
                            
                            LOGGER.info(f"Adding calendar event: {event_title} on {chapter['release_date']}")
                            
                            execute_query(
                                """
                                INSERT INTO calendar_events 
                                (series_id, chapter_id, title, description, event_date, event_type) 
                                VALUES (?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    series_id,
                                    chapter["id"],
                                    event_title,
                                    event_desc,
                                    chapter["release_date"],
                                    "CHAPTER_RELEASE"
                                ),
                                commit=True
                            )
                except (ValueError, TypeError):
                    # Skip invalid dates
                    continue
        
        # For AniList series, ensure volumes are included in the calendar
        # This helps ensure our volume date distribution logic takes effect
        if series_id is not None:
            # If we're updating a specific series, check if it's from AniList
            specific_series = execute_query(
                "SELECT id, title, metadata_source FROM series WHERE id = ?",
                (series_id,)
            )
            
            if specific_series and specific_series[0].get('metadata_source') == 'AniList':
                # Process only this specific AniList series
                anilist_series = [{'id': series_id, 'title': specific_series[0].get('title')}]
            else:
                # Not an AniList series, skip AniList-specific processing
                anilist_series = []
        else:
            # Processing all series, get all AniList series
            anilist_series = execute_query(
                "SELECT id, title FROM series WHERE metadata_source = 'AniList'"
            )
        
        # Process AniList volumes
        for series in anilist_series:
            series_id = series['id']
            series_title = series.get('title')
            
            LOGGER.info(f"Special processing for AniList series: {series_title}")
            
            # Get volumes for this series
            volumes = execute_query(
                """
                SELECT id, volume_number, title, release_date
                FROM volumes 
                WHERE series_id = ? AND release_date IS NOT NULL
                """,
                (series_id,)
            )
            
            # Re-add all volumes to calendar
            for volume in volumes:
                try:
                    release_date = datetime.fromisoformat(volume["release_date"])
                    
                    # Check if this event already exists
                    existing = execute_query(
                        """
                        SELECT id FROM calendar_events 
                        WHERE series_id = ? AND volume_id = ? AND event_date = ?
                        """,
                        (series_id, volume["id"], volume["release_date"])
                    )
                    
                    if not existing:
                        # Always include AniList volumes
                        execute_query(
                            """
                            INSERT INTO calendar_events 
                            (series_id, volume_id, title, description, event_date, event_type) 
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                series_id,
                                volume["id"],
                                f"Volume {volume['volume_number']} - {series_title}",
                                f"Release of volume {volume['volume_number']}: {volume['title']}",
                                volume["release_date"],
                                "VOLUME_RELEASE"
                            ),
                            commit=True
                        )
                        LOGGER.info(f"Added AniList volume {volume['volume_number']} for {series_title} to calendar")
                except (ValueError, TypeError) as e:
                    LOGGER.warning(f"Skipped AniList volume due to date error: {e}")
        
        # Comment out cleanup to keep all events for testing
        # execute_query(
        #     """
        #     DELETE FROM calendar_events 
        #     WHERE event_date < date('now', '-7 days')
        #     """,
        #     commit=True
        # )
        
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
