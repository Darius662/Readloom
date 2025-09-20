#!/usr/bin/env python3
"""
Bulk update script for manga volumes.

This script is meant to be run manually when you want to refresh the volume data
for your entire collection. During normal operation, the application will only update
the calendar for the specific manga you're adding, not the entire collection.

Use this script if:
- You've just updated the application and want to apply new volume scraping to existing manga
- You want to ensure all manga have proper volumes in your collection
- You notice volumes are missing from some manga in your collection

This is much more efficient than re-adding each series individually.
"""

from datetime import datetime, timedelta
from backend.internals.db import set_db_location, execute_query
from backend.base.logging import LOGGER, setup_logging
from backend.features.calendar import update_calendar
from backend.features.scrapers.mangafire_scraper import MangaInfoProvider
import time

def refresh_all_manga_volumes():
    """Re-fetch volume data for all manga series in the database."""
    # Set up logging and database
    setup_logging("data/logs", "refresh_volumes.log")
    set_db_location("data/db")
    
    LOGGER.info("Starting volume refresh for all manga...")
    
    # Get all series in the database
    series_list = execute_query("""
        SELECT id, title, metadata_source
        FROM series
        ORDER BY id
    """)
    
    LOGGER.info(f"Found {len(series_list)} series in the database")
    
    # Initialize the manga info provider
    provider = MangaInfoProvider()
    
    # Process each series
    for idx, series in enumerate(series_list):
        series_id = series['id']
        series_title = series['title']
        metadata_source = series['metadata_source']
        
        print(f"[{idx+1}/{len(series_list)}] Processing {series_title} ({metadata_source})...")
        LOGGER.info(f"Processing {series_title} (ID: {series_id}, Source: {metadata_source})")
        
        # Get current volumes for this series
        existing_volumes = execute_query("""
            SELECT COUNT(*) as count
            FROM volumes
            WHERE series_id = ?
        """, (series_id,))
        
        current_count = existing_volumes[0]['count'] if existing_volumes else 0
        LOGGER.info(f"Current volume count: {current_count}")
        
        # Get accurate volume count from scraper
        try:
            _, volume_count = provider.get_chapter_count(series_title)
            LOGGER.info(f"Scraped volume count: {volume_count}")
            
            if volume_count > 0 and volume_count != current_count:
                print(f"  Updating volumes: {current_count} -> {volume_count}")
                
                # Delete existing volumes
                if current_count > 0:
                    LOGGER.info(f"Deleting existing {current_count} volumes")
                    execute_query("""
                        DELETE FROM volumes
                        WHERE series_id = ?
                    """, (series_id,), commit=True)
                
                # Create new volumes with proper distribution
                LOGGER.info(f"Creating {volume_count} new volumes")
                
                # Calculate release dates distribution (one every 3 months)
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
            else:
                print(f"  No volume update needed ({volume_count})")
                
        except Exception as e:
            LOGGER.error(f"Error processing {series_title}: {e}")
            print(f"  Error: {e}")
        
        # Small delay to be nice to the scraper services
        time.sleep(1)
    
    # Update the calendar
    print("Updating calendar with new volume information...")
    update_calendar()
    
    print("Volume refresh complete!")
    LOGGER.info("Volume refresh complete!")

if __name__ == "__main__":
    refresh_all_manga_volumes()
