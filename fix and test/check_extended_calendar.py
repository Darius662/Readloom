#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to check calendar events over an extended period of time.
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.features.calendar import get_calendar_events
from backend.internals.db import execute_query

def main():
    """Main function."""
    print("Extended Calendar Check")
    print("======================")
    
    # Check 90-day range
    now = datetime.now()
    start_date = now.strftime("%Y-%m-%d")
    end_date = (now + timedelta(days=90)).strftime("%Y-%m-%d")
    
    print(f"Checking calendar events from {start_date} to {end_date} (90 days)...")
    
    events = get_calendar_events(start_date, end_date)
    
    print(f"Found {len(events)} total calendar events in this period")
    
    # Group events by series
    series_events = {}
    for event in events:
        series_title = event["series"]["title"]
        if series_title not in series_events:
            series_events[series_title] = []
        series_events[series_title].append(event)
    
    # Display events by series
    for series, events_list in series_events.items():
        print(f"\n{series} ({len(events_list)} events):")
        for event in sorted(events_list, key=lambda e: e["date"]):
            print(f"  {event['date']} - {event['title']}")

if __name__ == "__main__":
    main()
