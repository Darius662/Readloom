#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for MyAnimeList/Jikan provider and calendar integration.
This will verify that the fixes for MAL calendar entries are working properly.
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.base.logging import LOGGER
from backend.features.metadata_providers.jikan import JikanProvider
from backend.features.calendar import update_calendar, get_calendar_events
from backend.internals.db import execute_query

# Initialize the Jikan provider
jikan_provider = JikanProvider(enabled=True)

def clear_test_data():
    """Clear any test data from previous runs."""
    try:
        # Remove test series
        execute_query("DELETE FROM series WHERE title = 'MAL Calendar Test'", commit=True)
        print("Cleared previous test data")
    except Exception as e:
        print(f"Error clearing test data: {e}")

def add_test_series():
    """Add a test series from MyAnimeList."""
    try:
        # Search for a popular manga on MyAnimeList (e.g., "One Piece")
        print("Searching for test manga...")
        search_results = jikan_provider.search("One Piece", 1)
        
        if not search_results:
            print("No search results found")
            return None
        
        manga = search_results[0]
        manga_id = manga["id"]
        
        print(f"Found manga: {manga['title']} (ID: {manga_id})")
        
        # Get full details
        print("Getting manga details...")
        details = jikan_provider.get_manga_details(manga_id)
        
        if not details:
            print("Could not get manga details")
            return None
            
        # Insert test series
        series_id = execute_query(
            """
            INSERT INTO series (
                title, description, author, cover_url, status, 
                metadata_source, metadata_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "MAL Calendar Test",
                details.get("description", ""),
                details.get("author", ""),
                details.get("cover_url", ""),
                details.get("status", ""),
                "MyAnimeList",
                manga_id
            ),
            commit=True
        )
        
        # Get the newly inserted series ID
        new_series = execute_query("SELECT id FROM series WHERE title = 'MAL Calendar Test'")
        if new_series:
            series_id = new_series[0]['id']
        
        print(f"Added test series with ID {series_id}")
        
        # Get chapter list
        print("Getting chapter list...")
        chapter_data = jikan_provider.get_chapter_list(manga_id)
        
        if not chapter_data or "chapters" not in chapter_data:
            print("Could not get chapter list")
            return series_id
            
        chapters = chapter_data["chapters"]
        print(f"Found {len(chapters)} chapters")
        
        # Add chapters to database (limit to 5 for testing)
        for i, chapter in enumerate(chapters[:5]):
            try:
                # Make sure we have a valid release date
                release_date = chapter.get("date", "")
                if not release_date:
                    release_date = datetime.now().strftime("%Y-%m-%d")
                    print(f"Using today's date for chapter {chapter['number']} since no date was provided")
                
                execute_query(
                    """
                    INSERT INTO chapters (
                        series_id, chapter_number, title, release_date
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        series_id,
                        chapter["number"],
                        chapter["title"],
                        release_date
                    ),
                    commit=True
                )
                print(f"Added chapter {chapter['number']} with release date: {release_date}")
            except Exception as e:
                print(f"Error adding chapter {chapter.get('number', '?')}: {e}")
            
        return series_id
    
    except Exception as e:
        print(f"Error adding test series: {e}")
        return None

def test_calendar():
    """Test the calendar functionality with the MAL series."""
    try:
        # First check if our chapters have proper release dates
        print("Checking chapter release dates in the database...")
        chapters = execute_query(
            """
            SELECT id, chapter_number, title, release_date 
            FROM chapters 
            WHERE series_id = (SELECT id FROM series WHERE title = 'MAL Calendar Test')
            """
        )
        
        for chapter in chapters:
            print(f"Chapter {chapter['chapter_number']}: '{chapter['title']}' with release_date: '{chapter['release_date']}'")
            
        # Update the calendar
        print("Updating calendar...")
        update_calendar()
        
        # Check the calendar_events table directly
        print("Checking calendar_events table...")
        calendar_events = execute_query(
            """
            SELECT ce.id, ce.title, ce.description, ce.event_date, ce.event_type, s.title as series_title 
            FROM calendar_events ce
            JOIN series s ON ce.series_id = s.id
            WHERE s.title = 'MAL Calendar Test'
            """
        )
        
        print(f"Found {len(calendar_events)} events in calendar_events table")
        for event in calendar_events:
            print(f"DB Event: {event['title']} on {event['event_date']}")
        
        # Get calendar events through the API function
        now = datetime.now()
        start_date = (now - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = (now + timedelta(days=30)).strftime("%Y-%m-%d")
        
        print(f"Getting calendar events from {start_date} to {end_date}...")
        events = get_calendar_events(start_date, end_date)
        
        # Check if we have any events from our test series
        test_events = [e for e in events if e["series"]["title"] == "MAL Calendar Test"]
        
        print(f"Found {len(test_events)} calendar events for the test series through API")
        
        # Print the events
        for event in test_events:
            print(f"API Event: {event['title']} on {event['date']}")
            
        # Look for SQL errors in the log
        print("\nLooking for errors in the log file...")
        try:
            with open(os.path.join('data', 'logs', 'readloom.log'), 'r') as log_file:
                last_lines = log_file.readlines()[-20:]  # Get the last 20 lines
                for line in last_lines:
                    if 'ERROR' in line:
                        print(f"LOG ERROR: {line.strip()}")
        except Exception as e:
            print(f"Could not read log file: {e}")
            
        return len(calendar_events) > 0 or len(test_events) > 0
    
    except Exception as e:
        print(f"Error testing calendar: {e}")
        return False

def run_test():
    """Run the full test sequence."""
    print("Starting MyAnimeList calendar integration test...")
    clear_test_data()
    series_id = add_test_series()
    
    if series_id:
        success = test_calendar()
        if success:
            print("TEST PASSED: MyAnimeList chapters are appearing in the calendar!")
        else:
            print("TEST FAILED: MyAnimeList chapters are not appearing in the calendar.")
    else:
        print("TEST FAILED: Could not create test series.")
        
if __name__ == "__main__":
    run_test()
