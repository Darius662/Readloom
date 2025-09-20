#!/usr/bin/env python3

import sys
from datetime import datetime, timedelta
from backend.internals.db import set_db_location, execute_query
from backend.base.logging import LOGGER, setup_logging
from backend.features.calendar import update_calendar
from backend.features.scrapers.mangafire_scraper import MangaInfoProvider

def update_manga_volumes(manga_name):
    """Update the volumes for a specific manga."""
    # Set up logging and database
    setup_logging("data/logs", "update_manga.log")
    set_db_location("data/db")
    
    LOGGER.info(f"Updating volumes for manga: {manga_name}")
    
    # Find the series
    series = execute_query("""
        SELECT id, title, metadata_source
        FROM series
        WHERE title LIKE ?
    """, (f"%{manga_name}%",))
    
    if not series:
        print(f"Manga '{manga_name}' not found in the database.")
        return False
    
    # If multiple series match, show options
    if len(series) > 1:
        print(f"Multiple series found matching '{manga_name}':")
        for i, s in enumerate(series):
            print(f"{i+1}. {s['title']} ({s['metadata_source']})")
        
        choice = input("Enter the number of the series to update (or 0 to cancel): ")
        try:
            choice_idx = int(choice) - 1
            if choice_idx < 0 or choice_idx >= len(series):
                print("Invalid choice. Exiting.")
                return False
            series_to_update = series[choice_idx]
        except ValueError:
            print("Invalid input. Exiting.")
            return False
    else:
        series_to_update = series[0]
    
    series_id = series_to_update['id']
    series_title = series_to_update['title']
    metadata_source = series_to_update['metadata_source']
    
    print(f"\nUpdating volumes for: {series_title}")
    
    # Get current volumes for this series
    existing_volumes = execute_query("""
        SELECT COUNT(*) as count
        FROM volumes
        WHERE series_id = ?
    """, (series_id,))
    
    current_count = existing_volumes[0]['count'] if existing_volumes else 0
    print(f"Current volume count: {current_count}")
    
    # Initialize the manga info provider
    provider = MangaInfoProvider()
    
    # Get accurate volume count from scraper
    _, volume_count = provider.get_chapter_count(series_title)
    print(f"Scraped volume count: {volume_count}")
    
    if volume_count <= 0:
        print("Could not get volume count from scraper. Exiting.")
        return False
    
    if volume_count == current_count:
        print("Volume count is already correct. No update needed.")
        return True
    
    # Ask for confirmation
    confirmation = input(f"Update from {current_count} to {volume_count} volumes? (y/n): ")
    if confirmation.lower() != 'y':
        print("Update cancelled.")
        return False
    
    # Delete existing volumes if any
    if current_count > 0:
        print(f"Deleting existing {current_count} volumes...")
        execute_query("""
            DELETE FROM volumes
            WHERE series_id = ?
        """, (series_id,), commit=True)
    
    # Create new volumes
    print(f"Creating {volume_count} volumes...")
    
    # Calculate release dates distribution
    start_date = datetime.now() - timedelta(days=volume_count * 90)
    interval_days = 90
    
    for i in range(1, volume_count + 1):
        volume_date = start_date + timedelta(days=i * interval_days)
        release_date_str = volume_date.strftime("%Y-%m-%d")
        
        # Create new volume
        execute_query("""
            INSERT INTO volumes (
                series_id, volume_number, title, description, 
                cover_url, release_date
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            series_id,
            str(i),
            f"Volume {i}",
            "",
            "",
            release_date_str
        ), commit=True)
        
        print(f"  Created Volume {i}")
    
    # Update the calendar
    print("Updating calendar...")
    update_calendar()
    
    print(f"Successfully updated {series_title} to have {volume_count} volumes!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_manga.py \"Manga Title\"")
        sys.exit(1)
    
    manga_name = sys.argv[1]
    update_manga_volumes(manga_name)
