#!/usr/bin/env python3

from datetime import datetime, timedelta
from backend.internals.db import set_db_location, execute_query
from backend.base.logging import LOGGER, setup_logging

def fix_anilist_volumes():
    """Update AniList volume release dates to have better distribution."""
    # Set up logging and database
    setup_logging("data/logs", "fix_anilist_volumes.log")
    set_db_location("data/db")
    
    LOGGER.info("Starting AniList volume date fix...")
    
    # Get all AniList series
    anilist_series = execute_query(
        "SELECT id, title, metadata_id FROM series WHERE metadata_source = 'AniList'"
    )
    
    LOGGER.info(f"Found {len(anilist_series)} AniList series")
    
    # Process each series
    for series in anilist_series:
        series_id = series['id']
        series_title = series['title']
        # Use a default start date since we don't have it in the series table
        start_date_str = None
        
        LOGGER.info(f"Processing {series_title} (ID: {series_id})")
        
        # Get volumes for this series
        volumes = execute_query(
            "SELECT id, volume_number FROM volumes WHERE series_id = ? ORDER BY CAST(volume_number AS INTEGER)",
            (series_id,)
        )
        
        volume_count = len(volumes)
        if volume_count == 0:
            LOGGER.info(f"No volumes found for {series_title}, skipping")
            continue
            
        LOGGER.info(f"Found {volume_count} volumes for {series_title}")
        
        # Parse start date or use default
        try:
            if start_date_str:
                start_date = datetime.fromisoformat(start_date_str)
            else:
                start_date = datetime.now() - timedelta(days=volume_count * 90)
        except (ValueError, TypeError):
            start_date = datetime.now() - timedelta(days=volume_count * 90)
            
        # Calculate interval (approximately 3 months between volumes)
        interval_days = 90
        
        # Update each volume
        for i, volume in enumerate(volumes):
            volume_date = start_date + timedelta(days=i * interval_days)
            release_date_str = volume_date.strftime("%Y-%m-%d")
            
            # Update the volume release date
            execute_query(
                "UPDATE volumes SET release_date = ? WHERE id = ?",
                (release_date_str, volume['id']),
                commit=True
            )
            
            LOGGER.info(f"Updated Volume {volume['volume_number']} date to {release_date_str}")
    
    # Now update the calendar
    LOGGER.info("Updating calendar with new volume dates...")
    from backend.features.calendar import update_calendar
    update_calendar()
    
    LOGGER.info("Fix complete!")

if __name__ == "__main__":
    fix_anilist_volumes()
