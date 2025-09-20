#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# Add a chapter with a release date
data = {
    "title": "Chapter 1",
    "chapter_number": "1",
    "release_date": "2025-08-21",
    "status": "ANNOUNCED",
    "read_status": "UNREAD"
}

response = requests.post(
    "http://127.0.0.1:7227/api/series/10/chapters",
    json=data
)

print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")

# Refresh the calendar
response = requests.post("http://127.0.0.1:7227/api/calendar/refresh")
print(f"Calendar refresh status: {response.status_code}")

# Check if there are any events in the calendar
response = requests.get("http://127.0.0.1:7227/api/calendar?start_date=2025-08-01&end_date=2025-08-31")
print(f"Calendar events: {response.text}")
