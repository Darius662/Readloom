#!/usr/bin/env python3

from backend.internals.db import set_db_location, execute_query

def check_calendar_events():
    # Set DB location
    set_db_location("data/db")
    
    # Check volume events
    volume_events = execute_query("""
        SELECT COUNT(*) as count 
        FROM calendar_events 
        WHERE event_type = 'VOLUME_RELEASE'
    """)
    
    print(f"Volume events in calendar: {volume_events[0]['count'] if volume_events else 0}")
    
    # Check chapter events
    chapter_events = execute_query("""
        SELECT COUNT(*) as count 
        FROM calendar_events 
        WHERE event_type = 'CHAPTER_RELEASE'
    """)
    
    print(f"Chapter events in calendar: {chapter_events[0]['count'] if chapter_events else 0}")
    
    # Check AniList volume entries
    anilist_volumes = execute_query("""
        SELECT COUNT(*) as count 
        FROM volumes v
        JOIN series s ON v.series_id = s.id
        WHERE s.metadata_source = 'AniList'
    """)
    
    print(f"AniList volumes in database: {anilist_volumes[0]['count'] if anilist_volumes else 0}")
    
    # Check all volumes
    all_volumes = execute_query("""
        SELECT COUNT(*) as count 
        FROM volumes
    """)
    
    print(f"Total volumes in database: {all_volumes[0]['count'] if all_volumes else 0}")
    
    # Check AniList volumes with release dates
    anilist_volumes_with_dates = execute_query("""
        SELECT COUNT(*) as count 
        FROM volumes v
        JOIN series s ON v.series_id = s.id
        WHERE s.metadata_source = 'AniList' AND v.release_date IS NOT NULL
    """)
    
    print(f"AniList volumes with release dates: {anilist_volumes_with_dates[0]['count'] if anilist_volumes_with_dates else 0}")

if __name__ == "__main__":
    check_calendar_events()
