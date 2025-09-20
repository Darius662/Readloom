#!/usr/bin/env python3

import argparse
from datetime import datetime, timedelta
from backend.internals.db import set_db_location, execute_query
from backend.base.logging import LOGGER, setup_logging
from backend.features.calendar import update_calendar

def set_manga_volumes(series_name, volume_count):
    """Set a specific volume count for a manga series."""
    # Set up logging and database
    setup_logging("data/logs", "update_manga_volume.log")
    set_db_location("data/db")
    
    LOGGER.info(f"Setting volume count for '{series_name}' to {volume_count}")
    
    # Find the series
    series = execute_query("""
        SELECT id, title, metadata_source, metadata_id 
        FROM series 
        WHERE title LIKE ?
    """, (f"%{series_name}%",))
    
    if not series:
        print(f"Series '{series_name}' not found")
        return False
    
    # If multiple series match, show options
    if len(series) > 1:
        print(f"Multiple series found matching '{series_name}':")
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
    
    print(f"\nUpdating volume count for: {series_title}")
    
    # Get current volumes for this series
    volumes = execute_query("""
        SELECT COUNT(*) as count
        FROM volumes
        WHERE series_id = ?
    """, (series_id,))
    
    current_count = volumes[0]['count'] if volumes else 0
    
    print(f"Current volume count: {current_count}, New count: {volume_count}")
    
    if current_count > 0:
        confirm = input(f"Delete existing {current_count} volumes and create {volume_count} new ones? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return False
        
        # Delete existing volumes to recreate them
        print(f"Deleting existing {current_count} volumes...")
        execute_query("""
            DELETE FROM volumes
            WHERE series_id = ?
        """, (series_id,), commit=True)
    
    # Create new volumes with proper distribution
    print(f"Creating {volume_count} volumes...")
    
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
        
        print(f"Created Volume {i} with date {release_date_str}")
    
    # Update the calendar
    print("Updating calendar...")
    update_calendar()
    
    print(f"Successfully updated {series_title} to have {volume_count} volumes!")
    return True

def main():
    parser = argparse.ArgumentParser(description='Update manga volume count')
    parser.add_argument('series', help='Series name to update (will search for partial matches)')
    parser.add_argument('count', type=int, help='Number of volumes to set')
    
    args = parser.parse_args()
    set_manga_volumes(args.series, args.count)

if __name__ == '__main__':
    main()
