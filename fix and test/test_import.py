#!/usr/bin/env python3

from backend.internals.db import set_db_location, execute_query
from backend.features.metadata_service import import_manga_to_collection
from backend.base.logging import LOGGER, setup_logging
import sys

def test_import_manga(title, provider="AniList"):
    """Test importing a manga to check if chapters and volumes are created."""
    # Set up logging and database
    setup_logging("data/logs", "test_import.log")
    set_db_location("data/db")
    
    print(f"Testing import of '{title}' from {provider}")
    
    # First, search for the manga ID
    from backend.features.metadata_service import search_manga
    search_results = search_manga(title, provider)
    
    if "error" in search_results:
        print(f"Error searching for manga: {search_results['error']}")
        return False
    
    if provider not in search_results["results"]:
        print(f"No results found for {title} in {provider}")
        return False
    
    manga_results = search_results["results"][provider]
    if not manga_results:
        print(f"No manga found matching '{title}'")
        return False
    
    # Take the first result
    manga = manga_results[0]
    manga_id = manga["id"]
    
    print(f"Found manga: {manga.get('title', 'Unknown')} (ID: {manga_id})")
    
    # Now try to import it
    print("Importing manga...")
    result = import_manga_to_collection(manga_id, provider)
    
    if result.get("success", False):
        print(f"Import successful: {result.get('message', '')}")
        series_id = result.get("series_id")
        
        # Check if volumes were created
        volumes = execute_query(
            "SELECT COUNT(*) as count FROM volumes WHERE series_id = ?",
            (series_id,)
        )
        volume_count = volumes[0]["count"] if volumes else 0
        
        # Check if chapters were created
        chapters = execute_query(
            "SELECT COUNT(*) as count FROM chapters WHERE series_id = ?",
            (series_id,)
        )
        chapter_count = chapters[0]["count"] if chapters else 0
        
        print(f"Series ID: {series_id}")
        print(f"Volumes created: {volume_count}")
        print(f"Chapters created: {chapter_count}")
        
        # Check calendar entries
        calendar_events = execute_query(
            """
            SELECT COUNT(*) as count, event_type 
            FROM calendar_events 
            WHERE series_id = ? 
            GROUP BY event_type
            """,
            (series_id,)
        )
        
        print("Calendar events:")
        for event in calendar_events:
            print(f"  - {event['event_type']}: {event['count']}")
        
        return True
    else:
        print(f"Import failed: {result.get('message', 'Unknown error')}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_import_manga(sys.argv[1])
    else:
        test_import_manga("Taiyou yori mo Mabushii Hoshi")
