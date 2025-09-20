#!/usr/bin/env python3

from backend.internals.db import set_db_location, execute_query
from backend.base.logging import LOGGER, setup_logging

def check_series_volumes(series_name):
    """Check volumes for a specific series."""
    # Set up logging and database
    setup_logging("data/logs", "check_series.log")
    set_db_location("data/db")
    
    print(f"Checking series: {series_name}")
    
    # Find the series
    series = execute_query(
        """
        SELECT id, title, metadata_source, metadata_id 
        FROM series 
        WHERE title LIKE ?
        """, 
        (f"%{series_name}%",)
    )
    
    if not series:
        print(f"Series '{series_name}' not found")
        return
    
    for s in series:
        print(f"\nFound series: {s['title']}")
        print(f"  ID: {s['id']}")
        print(f"  Metadata Source: {s['metadata_source']}")
        print(f"  Metadata ID: {s['metadata_id']}")
        
        # Check volumes
        volumes = execute_query(
            "SELECT id, volume_number, title, release_date FROM volumes WHERE series_id = ?",
            (s['id'],)
        )
        
        print(f"  Volumes count: {len(volumes)}")
        
        if volumes:
            print("\nVolumes:")
            for v in volumes:
                print(f"  - Vol {v['volume_number']}: {v['title']} (Release: {v['release_date']})")
        
        # Check chapters
        chapters = execute_query(
            "SELECT id, chapter_number, title FROM chapters WHERE series_id = ? LIMIT 5",
            (s['id'],)
        )
        
        chapter_count = execute_query(
            "SELECT COUNT(*) as count FROM chapters WHERE series_id = ?",
            (s['id'],)
        )[0]['count']
        
        print(f"\n  Total chapters: {chapter_count}")
        if chapters:
            print("  Sample chapters:")
            for c in chapters:
                print(f"  - Ch {c['chapter_number']}: {c['title']}")
        
        # Check if this is from AniList
        if s['metadata_source'] == 'AniList':
            # Check the original metadata
            from backend.features.metadata_service import get_manga_details
            print("\nFetching original metadata from AniList...")
            
            try:
                details = get_manga_details(s['metadata_id'], 'AniList')
                volumes_from_api = details.get('volumes', 0)
                volumes_list = details.get('volumes', [])
                
                print(f"  Reported volume count from AniList API: {volumes_from_api}")
                print(f"  Volumes list length: {len(volumes_list)}")
                
                if isinstance(volumes_list, list) and volumes_list:
                    print("  Sample volume data:")
                    for i, vol in enumerate(volumes_list[:3]):
                        print(f"    - {vol}")
                        if i >= 2:
                            break
            except Exception as e:
                print(f"  Error getting metadata: {e}")

if __name__ == "__main__":
    check_series_volumes("Kumo desu ga")
