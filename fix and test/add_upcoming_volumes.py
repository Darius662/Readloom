#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to create upcoming volume releases for finished series.
This will help them appear in the calendar.
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.base.logging import LOGGER
from backend.features.calendar import update_calendar, get_calendar_events
from backend.internals.db import execute_query

def add_upcoming_volumes(series_id, series_title):
    """Add upcoming volumes for a series."""
    print(f"\nAdding upcoming volumes for {series_title} (ID: {series_id})...")
    
    # Check if the series already has volumes
    volumes = execute_query(
        """
        SELECT MAX(CAST(volume_number AS REAL)) as max_volume
        FROM volumes
        WHERE series_id = ?
        """,
        (series_id,)
    )
    
    max_volume = 0
    if volumes and volumes[0]["max_volume"] is not None:
        max_volume = float(volumes[0]["max_volume"])
    
    print(f"  Current highest volume: {max_volume}")
    
    # Add some upcoming volumes
    added_count = 0
    today = datetime.now()
    
    # Add 3 upcoming volumes (one per month)
    for i in range(1, 4):
        new_volume_num = max_volume + i
        release_date = (today + timedelta(days=i*30)).strftime("%Y-%m-%d")
        
        try:
            execute_query(
                """
                INSERT INTO volumes (
                    series_id, volume_number, title, release_date
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    series_id,
                    str(new_volume_num),
                    f"Volume {new_volume_num}",
                    release_date
                ),
                commit=True
            )
            print(f"  Added upcoming Volume {new_volume_num} with release date {release_date}")
            added_count += 1
        except Exception as e:
            print(f"  Error adding volume: {e}")
    
    return added_count

def main():
    """Main function."""
    print("Upcoming Volumes Creator")
    print("=======================")
    
    # Get all completed MAL series
    finished_series = execute_query(
        """
        SELECT s.id, s.title
        FROM series s
        WHERE s.metadata_source = 'MyAnimeList'
        """
    )
    
    if not finished_series:
        print("No suitable series found in database.")
        return
    
    print(f"Found {len(finished_series)} series to update:")
    for series in finished_series:
        print(f"  {series['title']} (ID: {series['id']})")
    
    total_added = 0
    
    # Process each series
    for series in finished_series:
        added = add_upcoming_volumes(series['id'], series['title'])
        total_added += added
    
    print(f"\nAdded {total_added} upcoming volumes across all series")
    
    # Update calendar
    print("\nUpdating calendar...")
    update_calendar()
    print("Calendar updated")
    
    # Show results
    print("\nCalendar Events:")
    
    # Get calendar range
    settings = execute_query("SELECT value FROM settings WHERE key = 'calendar_range_days'")
    calendar_range = 30  # Default
    if settings:
        try:
            calendar_range = int(settings[0]['value'])
        except (ValueError, KeyError, IndexError):
            pass
    
    now = datetime.now()
    start_date = now.strftime("%Y-%m-%d")
    end_date = (now + timedelta(days=calendar_range)).strftime("%Y-%m-%d")
    
    events = get_calendar_events(start_date, end_date)
    
    print(f"Found {len(events)} calendar events in date range {start_date} to {end_date}:")
    for event in events:
        print(f"  {event['date']} - {event['title']} ({event['series']['title']})")
    
    print("\nDONE!")

if __name__ == "__main__":
    main()
