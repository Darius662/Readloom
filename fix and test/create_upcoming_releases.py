#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to create upcoming releases for MAL series so they appear in the calendar.
This will create fictional upcoming chapters for ongoing series.
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.base.logging import LOGGER
from backend.features.metadata_providers.jikan import JikanProvider
from backend.features.calendar import update_calendar, get_calendar_events
from backend.internals.db import execute_query

# Initialize Jikan provider
jikan_provider = JikanProvider(enabled=True)

def create_upcoming_releases(series_id, series_title, mal_id):
    """Create upcoming releases for a series."""
    print(f"\nCreating upcoming releases for {series_title} (ID: {series_id})...")
    
    try:
        # Get series details to check if it's ongoing
        details = jikan_provider.get_manga_details(mal_id)
        
        if not details:
            print("  Could not get series details")
            return 0
        
        status = details.get("status", "").lower()
        
        if status != "publishing" and status != "ongoing":
            print(f"  Series is not ongoing (status: {status}), skipping")
            return 0
        
        # Get highest chapter number
        chapters = execute_query(
            """
            SELECT MAX(CAST(chapter_number AS REAL)) as max_chapter
            FROM chapters
            WHERE series_id = ?
            """,
            (series_id,)
        )
        
        max_chapter = 0
        if chapters and chapters[0]["max_chapter"] is not None:
            max_chapter = float(chapters[0]["max_chapter"])
        
        print(f"  Current highest chapter: {max_chapter}")
        
        # Create some upcoming chapters
        today = datetime.now()
        added_count = 0
        
        # Create 5 upcoming chapters (one every 7 days)
        for i in range(1, 6):
            new_chapter_num = max_chapter + i
            release_date = (today + timedelta(days=i*7)).strftime("%Y-%m-%d")
            
            # Insert the new chapter
            try:
                execute_query(
                    """
                    INSERT INTO chapters (
                        series_id, chapter_number, title, release_date, status
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        series_id,
                        str(new_chapter_num),
                        f"Chapter {new_chapter_num}",
                        release_date,
                        "UPCOMING"
                    ),
                    commit=True
                )
                print(f"  Added upcoming Chapter {new_chapter_num} with release date {release_date}")
                added_count += 1
            except Exception as e:
                print(f"  Error adding chapter: {e}")
        
        return added_count
    except Exception as e:
        print(f"  Error creating upcoming releases: {e}")
        return 0

def main():
    """Main function."""
    print("Upcoming MAL Releases Creator")
    print("============================")
    
    # Get all MAL series
    mal_series = execute_query(
        """
        SELECT s.id, s.title, s.metadata_id
        FROM series s
        WHERE s.metadata_source = 'MyAnimeList'
        ORDER BY s.title
        """
    )
    
    if not mal_series:
        print("No MyAnimeList series found in database.")
        return
    
    print(f"Found {len(mal_series)} MyAnimeList series:")
    for series in mal_series:
        print(f"  {series['title']} (ID: {series['id']}, MAL ID: {series['metadata_id']})")
    
    total_added = 0
    
    # Process each series
    for series in mal_series:
        added = create_upcoming_releases(series['id'], series['title'], series['metadata_id'])
        total_added += added
    
    print(f"\nAdded {total_added} upcoming chapters across all series")
    
    # Update calendar
    print("\nUpdating calendar...")
    update_calendar()
    print("Calendar updated")
    
    # Show results
    print("\nCalendar Events:")
    
    # Get current date range
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
    
    mal_events = [e for e in events if any(s['title'] == e['series']['title'] for s in mal_series)]
    print(f"Found {len(mal_events)} MAL events in date range {start_date} to {end_date}:")
    
    for event in mal_events:
        print(f"  {event['date']} - {event['title']} ({event['series']['title']})")
    
    print("\nDONE!")

if __name__ == "__main__":
    main()
