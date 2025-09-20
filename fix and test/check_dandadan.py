#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to check and fix specific series that should appear in the calendar
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.features.calendar import update_calendar, get_calendar_events
from backend.internals.db import execute_query

def check_series_by_name(series_name):
    """Check a series by name."""
    print(f"\nChecking series with name '{series_name}'...")
    
    # Find the series
    series = execute_query(
        """
        SELECT id, title, metadata_source, metadata_id
        FROM series
        WHERE title LIKE ?
        """,
        (f"%{series_name}%",)
    )
    
    if not series:
        print(f"  No series found with name containing '{series_name}'")
        return
    
    # Process each matching series
    for s in series:
        print(f"\nFound series: {s['title']} (ID: {s['id']}, Source: {s['metadata_source']})")
        
        # Check if it's from MAL
        if s['metadata_source'] == 'MyAnimeList':
            print("  This is a MyAnimeList series - running the fix_myanimelist_releases.py script on it")
            
            # We'll run the script manually for now to see the details
            print("\nTo fix this series, run:")
            print(f"python fix_myanimelist_releases.py --series-id {s['id']}")
        else:
            print(f"  This is a {s['metadata_source']} series, not MAL")
        
        # Check the chapters
        chapters = execute_query(
            """
            SELECT id, chapter_number, title, release_date 
            FROM chapters
            WHERE series_id = ?
            ORDER BY CAST(chapter_number AS REAL) DESC
            LIMIT 10
            """, 
            (s['id'],)
        )
        
        print(f"\n  Latest chapters for {s['title']}:")
        chapters_with_dates = 0
        for chapter in chapters:
            release_date = chapter['release_date'] or 'NULL'
            if release_date != 'NULL':
                chapters_with_dates += 1
            print(f"    Chapter {chapter['chapter_number']}: '{chapter['title']}' - Release Date: {release_date}")
        
        # Check calendar events
        calendar_events = execute_query(
            """
            SELECT ce.id, ce.title, ce.event_date, ce.event_type
            FROM calendar_events ce
            WHERE ce.series_id = ?
            ORDER BY ce.event_date DESC
            LIMIT 10
            """,
            (s['id'],)
        )
        
        print(f"\n  Calendar events for {s['title']}:")
        for event in calendar_events:
            print(f"    Event: {event['title']} - Date: {event['event_date']} - Type: {event['event_type']}")
        
        if not calendar_events:
            print("    No calendar events found for this series")
    
    # Check what's in the calendar for the current period
    calendar_range = 30  # Default
    settings = execute_query("SELECT value FROM settings WHERE key = 'calendar_range_days'")
    if settings:
        try:
            calendar_range = int(settings[0]['value'])
        except (ValueError, KeyError, IndexError):
            pass
    
    now = datetime.now()
    start_date = (now - timedelta(days=14)).strftime("%Y-%m-%d")  # Show past 2 weeks too
    end_date = (now + timedelta(days=calendar_range)).strftime("%Y-%m-%d")
    
    print(f"\nCurrent calendar events from {start_date} to {end_date}:")
    
    events = get_calendar_events(start_date, end_date)
    
    print(f"Found {len(events)} total events in this date range")
    for event in events:
        print(f"  {event['date']} - {event['title']} ({event['series']['title']})")

if __name__ == "__main__":
    # Check Dandadan specifically
    check_series_by_name("Dandadan")
    
    # You can also check any other series by uncommenting and changing the name:
    # check_series_by_name("One-Punch Man")
