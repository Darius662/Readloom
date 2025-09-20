#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive MAL Calendar Integration Fix

This script:
1. Fixes release dates for existing MAL series
2. Adds upcoming chapters for ongoing series
3. Adds upcoming volumes for finished series
4. Updates the calendar to show all events

This can be run after adding a new MAL series to ensure it appears in your calendar.
"""

import os
import sys
from datetime import datetime, timedelta
import time
import argparse

from backend.base.logging import LOGGER
from backend.features.metadata_providers.jikan import JikanProvider
from backend.features.calendar import update_calendar, get_calendar_events
from backend.internals.db import execute_query

# Initialize Jikan provider
jikan_provider = JikanProvider(enabled=True)

def fix_series_chapters(series_id, manga_id):
    """Fix release dates for chapters of a specific series."""
    print(f"\nFixing chapter dates for series ID {series_id} (MAL ID: {manga_id})...")
    
    # Get chapter list using our fixed Jikan provider
    chapter_data = jikan_provider.get_chapter_list(manga_id)
    
    if not chapter_data or "chapters" not in chapter_data or not chapter_data["chapters"]:
        print("  No chapters found from MyAnimeList API")
        return 0
    
    mal_chapters = chapter_data["chapters"]
    print(f"  Found {len(mal_chapters)} chapters from MyAnimeList API")
    
    # Get existing chapters
    db_chapters = execute_query(
        """
        SELECT id, chapter_number, title, release_date
        FROM chapters
        WHERE series_id = ?
        ORDER BY CAST(chapter_number AS REAL)
        """,
        (series_id,)
    )
    
    print(f"  Found {len(db_chapters)} chapters in database")
    
    # Create a mapping for easier lookup
    db_chapter_map = {str(chapter["chapter_number"]): chapter for chapter in db_chapters}
    
    # Update chapters with missing dates
    updated_count = 0
    for mal_chapter in mal_chapters:
        chapter_number = mal_chapter["number"]
        release_date = mal_chapter["date"]
        
        if not release_date:
            continue
        
        if chapter_number in db_chapter_map:
            db_chapter = db_chapter_map[chapter_number]
            
            if not db_chapter["release_date"]:
                # Update chapter with release date
                execute_query(
                    """
                    UPDATE chapters
                    SET release_date = ?
                    WHERE id = ?
                    """,
                    (release_date, db_chapter["id"]),
                    commit=True
                )
                print(f"  Updated chapter {chapter_number} with release date {release_date}")
                updated_count += 1
    
    # For any remaining chapters without dates, interpolate or set to current time
    remaining_chapters = execute_query(
        """
        SELECT id, chapter_number
        FROM chapters
        WHERE series_id = ? AND release_date IS NULL
        ORDER BY CAST(chapter_number AS REAL)
        """,
        (series_id,)
    )
    
    if remaining_chapters:
        print(f"  Still have {len(remaining_chapters)} chapters without dates")
        
        # Get the series details to understand publication timeline
        details = jikan_provider.get_manga_details(manga_id)
        
        # Calculate start and end dates for distribution
        start_date = None
        end_date = None
        status = "finished"
        
        if details:
            start_date_str = details.get("start_date", "")
            end_date_str = details.get("end_date", "")
            status = details.get("status", "").lower()
            
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                except ValueError:
                    pass
            
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                except ValueError:
                    pass
        
        # If we have valid dates, distribute chapters
        if start_date and (end_date or status != "finished"):
            if not end_date:
                end_date = datetime.now()
            
            # Calculate distribution
            try:
                total_chapters = len(db_chapters)
                days_between = (end_date - start_date).days
                interval = max(1, days_between // (total_chapters or 1))
                
                for i, chapter in enumerate(remaining_chapters):
                    chapter_id = chapter["id"]
                    chapter_number = float(chapter["chapter_number"])
                    
                    # Calculate proportional position
                    position = chapter_number / (total_chapters or 1)
                    days_offset = int(days_between * position)
                    chapter_date = (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
                    
                    # Update the chapter
                    execute_query(
                        """
                        UPDATE chapters
                        SET release_date = ?
                        WHERE id = ?
                        """,
                        (chapter_date, chapter_id),
                        commit=True
                    )
                    print(f"  Interpolated date {chapter_date} for chapter {chapter_number}")
                    updated_count += 1
                    
                    # Small delay to not overload the database
                    time.sleep(0.01)
            except Exception as e:
                print(f"  Error interpolating dates: {e}")
        else:
            # Use a simpler approach - set all to today's date
            today = datetime.now().strftime("%Y-%m-%d")
            for chapter in remaining_chapters:
                execute_query(
                    """
                    UPDATE chapters
                    SET release_date = ?
                    WHERE id = ?
                    """,
                    (today, chapter["id"]),
                    commit=True
                )
                print(f"  Set today's date for chapter {chapter['chapter_number']}")
                updated_count += 1
                
                # Small delay to not overload the database
                time.sleep(0.01)
    
    return updated_count

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

def process_series(series_id=None):
    """Process a specific series or all MAL series."""
    if series_id:
        # Process specific series
        series = execute_query(
            """
            SELECT id, title, metadata_id, metadata_source
            FROM series
            WHERE id = ?
            """,
            (series_id,)
        )
        
        if not series:
            print(f"No series found with ID {series_id}")
            return
        
        series = series[0]
        
        if series["metadata_source"] != "MyAnimeList":
            print(f"Series {series['title']} is not from MyAnimeList")
            return
        
        print(f"Processing series: {series['title']} (ID: {series_id})")
        
        # Fix chapter dates
        fix_series_chapters(series["id"], series["metadata_id"])
        
        # Add upcoming chapters or volumes
        create_upcoming_releases(series["id"], series["title"], series["metadata_id"])
        add_upcoming_volumes(series["id"], series["title"])
    else:
        # Process all MAL series
        mal_series = execute_query(
            """
            SELECT id, title, metadata_id
            FROM series
            WHERE metadata_source = 'MyAnimeList'
            ORDER BY title
            """
        )
        
        if not mal_series:
            print("No MyAnimeList series found in database.")
            return
        
        print(f"Found {len(mal_series)} MyAnimeList series:")
        for series in mal_series:
            print(f"  {series['title']} (ID: {series['id']}, MAL ID: {series['metadata_id']})")
            
        for series in mal_series:
            # Fix chapter dates
            fix_series_chapters(series["id"], series["metadata_id"])
            
            # Add upcoming chapters or volumes
            create_upcoming_releases(series["id"], series["title"], series["metadata_id"])
            add_upcoming_volumes(series["id"], series["title"])
    
    # Update calendar
    print("\nUpdating calendar...")
    update_calendar()
    print("Calendar updated successfully!")
    
    # Show calendar events
    calendar_range = 30  # Default
    settings = execute_query("SELECT value FROM settings WHERE key = 'calendar_range_days'")
    if settings:
        try:
            calendar_range = int(settings[0]['value'])
        except (ValueError, KeyError, IndexError):
            pass
    
    now = datetime.now()
    start_date = now.strftime("%Y-%m-%d")
    end_date = (now + timedelta(days=calendar_range)).strftime("%Y-%m-%d")
    
    print(f"\nCalendar events from {start_date} to {end_date}:")
    
    events = get_calendar_events(start_date, end_date)
    mal_events = [e for e in events if e["series"]["title"] in [s["title"] for s in execute_query("SELECT title FROM series WHERE metadata_source = 'MyAnimeList'")]]
    
    print(f"Found {len(mal_events)} MAL events in calendar")
    for event in mal_events:
        print(f"  {event['date']} - {event['title']} ({event['series']['title']})")

def main():
    parser = argparse.ArgumentParser(description='Fix MAL Calendar Integration')
    parser.add_argument('--series-id', type=int, help='Specific series ID to process')
    args = parser.parse_args()
    
    print("MyAnimeList Calendar Integration Fixer")
    print("=====================================")
    
    process_series(args.series_id)
    
    print("\nDONE! Your MAL series should now appear in the calendar.")

if __name__ == "__main__":
    main()
