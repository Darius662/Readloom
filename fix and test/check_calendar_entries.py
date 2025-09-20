#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Non-interactive debug script for calendar issues with MAL entries.
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.base.logging import LOGGER
from backend.features.calendar import update_calendar, get_calendar_events
from backend.internals.db import execute_query

def main():
    """Main function."""
    print("Calendar Debugging Tool")
    print("======================")
    
    # Show all series
    series = execute_query("SELECT id, title, metadata_source FROM series ORDER BY title")
    print(f"Found {len(series)} series in database:")
    for s in series:
        print(f"ID: {s['id']}, Title: {s['title']}, Source: {s['metadata_source']}")
    
    # Check all MAL series
    mal_series = execute_query("SELECT id, title FROM series WHERE metadata_source = 'MyAnimeList'")
    
    for series in mal_series:
        series_id = series['id']
        
        # Get series info
        print(f"\nChecking series: {series['title']} (ID: {series_id})")
        
        # Check chapters
        chapters = execute_query(
            """
            SELECT id, chapter_number, title, release_date 
            FROM chapters 
            WHERE series_id = ?
            ORDER BY CAST(chapter_number AS REAL)
            """, 
            (series_id,)
        )
        
        print(f"Found {len(chapters)} chapters:")
        chapters_with_dates = 0
        for chapter in chapters:
            release_date = chapter['release_date'] or 'NULL'
            if release_date != 'NULL':
                chapters_with_dates += 1
            print(f"  Chapter {chapter['chapter_number']}: '{chapter['title']}' - Release Date: {release_date}")
        
        if len(chapters) > 0:
            print(f"Summary: {chapters_with_dates} out of {len(chapters)} chapters have release dates ({(chapters_with_dates/len(chapters))*100:.1f}%)")
        
        # Check calendar events
        calendar_events = execute_query(
            """
            SELECT id, title, event_date, event_type
            FROM calendar_events
            WHERE series_id = ?
            ORDER BY event_date
            """,
            (series_id,)
        )
        
        print(f"Found {len(calendar_events)} calendar events:")
        for event in calendar_events:
            print(f"  Event: {event['title']} - Date: {event['event_date']} - Type: {event['event_type']}")
    
    # Get calendar range from settings
    settings = execute_query("SELECT value FROM settings WHERE key = 'calendar_range_days'")
    calendar_range = 30  # Default
    if settings:
        try:
            calendar_range = int(settings[0]['value'])
        except (ValueError, KeyError, IndexError):
            pass
    
    print(f"\nCurrent calendar range setting: {calendar_range} days")
    
    # Check what's currently being displayed in the calendar
    now = datetime.now()
    start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = (now + timedelta(days=calendar_range)).strftime("%Y-%m-%d")
    
    print(f"\nChecking calendar events in date range {start_date} to {end_date}...")
    
    cal_events = get_calendar_events(start_date, end_date)
    print(f"Calendar currently shows {len(cal_events)} events in this range")
    
    for event in cal_events:
        print(f"  {event['date']} - {event['title']} ({event['series']['title']})")
    
    # Check for MAL chapters in this date range
    print("\nChecking for MAL chapters in calendar range...")
    in_range_chapters = execute_query(
        """
        SELECT c.id, c.chapter_number, c.title, c.release_date, s.title as series_title
        FROM chapters c
        JOIN series s ON c.series_id = s.id
        WHERE s.metadata_source = 'MyAnimeList'
          AND c.release_date IS NOT NULL
          AND c.release_date BETWEEN ? AND ?
        ORDER BY c.release_date
        """,
        (start_date, end_date)
    )
    
    print(f"Found {len(in_range_chapters)} MAL chapters with dates in calendar range:")
    for chapter in in_range_chapters:
        print(f"  {chapter['release_date']} - Chapter {chapter['chapter_number']} ({chapter['series_title']})")
    
    # Force update the calendar
    print("\nForcing calendar update...")
    try:
        update_calendar()
        print("Calendar updated successfully")
    except Exception as e:
        print(f"Error updating calendar: {e}")
    
    # Check calendar events after update
    print("\nChecking calendar events after update...")
    after_events = get_calendar_events(start_date, end_date)
    print(f"Calendar now shows {len(after_events)} events in date range")
    
    for event in after_events:
        print(f"  {event['date']} - {event['title']} ({event['series']['title']})")
    
    # If there's a difference, highlight it
    if len(after_events) != len(cal_events):
        print(f"\nCalendar update created {len(after_events) - len(cal_events)} new events")
    else:
        print("\nNo new events were created after update")

if __name__ == "__main__":
    main()
