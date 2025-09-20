#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to fix release dates for MAL manga entries already in the database.
"""

import os
import sys
from datetime import datetime, timedelta
import time

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

def main():
    """Main function."""
    print("MAL Release Date Fixer")
    print("=====================")
    
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
    
    total_updated = 0
    
    # Process each series
    for series in mal_series:
        updated = fix_series_chapters(series['id'], series['metadata_id'])
        total_updated += updated
    
    print(f"\nUpdated {total_updated} chapters with release dates")
    
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
    start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = (now + timedelta(days=calendar_range)).strftime("%Y-%m-%d")
    
    events = get_calendar_events(start_date, end_date)
    
    mal_events = [e for e in events if e['series']['title'] in [s['title'] for s in mal_series]]
    print(f"Found {len(mal_events)} MAL events in date range {start_date} to {end_date}:")
    
    for event in mal_events:
        print(f"  {event['date']} - {event['title']} ({event['series']['title']})")
    
    print("\nDONE!")

if __name__ == "__main__":
    main()
