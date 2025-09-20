#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug script for calendar issues with specific series.
This will help diagnose why MAL entries aren't showing in the calendar.
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.base.logging import LOGGER
from backend.features.calendar import update_calendar, get_calendar_events
from backend.internals.db import execute_query

def show_all_series():
    """Show all series in the database."""
    series = execute_query("SELECT id, title, metadata_source FROM series ORDER BY title")
    print(f"Found {len(series)} series in database:")
    for s in series:
        print(f"ID: {s['id']}, Title: {s['title']}, Source: {s['metadata_source']}")
    return series

def check_specific_series(series_id=None):
    """Check a specific series for calendar issues."""
    if series_id is None:
        # Ask for series ID
        series_id = input("Enter series ID to check (or press Enter to check all MAL series): ")
        if not series_id:
            # Check all MAL series
            series = execute_query("SELECT id, title FROM series WHERE metadata_source = 'MyAnimeList'")
            for s in series:
                check_specific_series(s['id'])
            return
    
    try:
        series_id = int(series_id)
    except ValueError:
        print("Invalid series ID")
        return
    
    # Get series info
    series = execute_query("SELECT id, title, metadata_source FROM series WHERE id = ?", (series_id,))
    if not series:
        print(f"No series found with ID {series_id}")
        return
    
    series = series[0]
    print(f"\nChecking series: {series['title']} (ID: {series_id}, Source: {series['metadata_source']})")
    
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
    
    print(f"Summary: {chapters_with_dates} out of {len(chapters)} chapters have release dates ({(chapters_with_dates/max(1,len(chapters)))*100:.1f}%)")
    
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
    
    # Update calendar and check again
    print("\nUpdating calendar...")
    update_calendar()
    
    calendar_events_after = execute_query(
        """
        SELECT id, title, event_date, event_type
        FROM calendar_events
        WHERE series_id = ?
        ORDER BY event_date
        """,
        (series_id,)
    )
    
    print(f"After update: {len(calendar_events_after)} calendar events:")
    for event in calendar_events_after:
        print(f"  Event: {event['title']} - Date: {event['event_date']} - Type: {event['event_type']}")
    
    # Check if there are any new events
    new_events = len(calendar_events_after) - len(calendar_events)
    if new_events > 0:
        print(f"Calendar update created {new_events} new events.")
    else:
        print("No new events were created.")
        
        if len(chapters) > 0 and chapters_with_dates > 0:
            print("\nPossible reasons for no events:")
            print("1. The release dates may be outside the calendar range")
            print("2. Events may already exist for these chapters/volumes")
            print("3. There might be an issue with the calendar update logic")
            
            # Check calendar range in settings
            settings = execute_query("SELECT value FROM settings WHERE key = 'calendar_range_days'")
            if settings:
                calendar_range = int(settings[0]['value'])
                print(f"\nCurrent calendar range is {calendar_range} days")
                
                # Check if any chapters are within range
                now = datetime.now()
                start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
                end_date = (now + timedelta(days=calendar_range)).strftime("%Y-%m-%d")
                print(f"Calendar shows dates from {start_date} to {end_date}")
                
                in_range = 0
                for chapter in chapters:
                    if chapter['release_date'] and start_date <= chapter['release_date'] <= end_date:
                        in_range += 1
                
                if in_range > 0:
                    print(f"{in_range} chapters have release dates within calendar range")
                else:
                    print("No chapters have release dates within calendar range")
                    print("Try setting a larger calendar_range_days value or updating chapter dates")
            else:
                print("Could not find calendar range setting")

if __name__ == "__main__":
    print("Calendar Debugging Tool")
    print("======================")
    
    series = show_all_series()
    
    if series:
        check_specific_series()
    else:
        print("No series found in database")
