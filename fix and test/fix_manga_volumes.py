#!/usr/bin/env python3

from datetime import datetime, timedelta
from backend.internals.db import set_db_location, execute_query
from backend.base.logging import LOGGER, setup_logging

# Define known volume counts for manga that might have incomplete data
KNOWN_VOLUMES = {
    # AniList IDs mapped to their known volume counts
    "86952": 15,  # Kumo desu ga, Nani ka? (based on your statement)
    "30002": 72,  # Naruto (known volume count)
    "31499": 41   # Berserk (known volume count)
}

def fix_manga_volumes():
    """Fix volume data for specific manga series."""
    # Set up logging and database
    setup_logging("data/logs", "fix_manga_volumes.log")
    set_db_location("data/db")
    
    LOGGER.info("Starting manga volume fix...")
    
    # Get all series that need volume fixes
    series_list = execute_query("""
        SELECT id, title, metadata_source, metadata_id 
        FROM series
    """)
    
    # Process each series that needs fixing
    for series in series_list:
        series_id = series['id']
        series_title = series['title']
        metadata_source = series['metadata_source']
        metadata_id = series['metadata_id']
        
        # Check if this series needs volume correction
        if metadata_source == 'AniList' and metadata_id in KNOWN_VOLUMES:
            correct_volume_count = KNOWN_VOLUMES[metadata_id]
            
            # Get current volumes for this series
            volumes = execute_query("""
                SELECT COUNT(*) as count
                FROM volumes
                WHERE series_id = ?
            """, (series_id,))
            
            current_count = volumes[0]['count'] if volumes else 0
            
            LOGGER.info(f"Processing {series_title} (ID: {series_id})")
            LOGGER.info(f"Current volume count: {current_count}, Correct count: {correct_volume_count}")
            
            if current_count == correct_volume_count:
                LOGGER.info(f"Volume count already correct for {series_title}")
                continue
            
            if current_count > 0:
                # Delete existing volumes to recreate them
                LOGGER.info(f"Deleting existing {current_count} volumes for {series_title}")
                execute_query("""
                    DELETE FROM volumes
                    WHERE series_id = ?
                """, (series_id,), commit=True)
            
            # Create new volumes with proper distribution
            LOGGER.info(f"Creating {correct_volume_count} volumes for {series_title}")
            
            # Calculate release dates distribution (one every 3 months)
            start_date = datetime.now() - timedelta(days=correct_volume_count * 90)
            interval_days = 90
            
            for i in range(1, correct_volume_count + 1):
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
                
                LOGGER.info(f"Created Volume {i} with date {release_date_str}")
    
    # Now update the calendar
    LOGGER.info("Updating calendar with new volume information...")
    from backend.features.calendar import update_calendar
    update_calendar()
    
    LOGGER.info("Volume fix complete!")

if __name__ == "__main__":
    fix_manga_volumes()
