#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def add_volume(series_id, volume_number, title, release_date):
    data = {
        "volume_number": str(volume_number),
        "title": title,
        "release_date": release_date
    }
    
    response = requests.post(
        f"http://127.0.0.1:7227/api/series/{series_id}/volumes",
        json=data
    )
    print(f"Adding volume {volume_number} to series {series_id}: {response.status_code}")
    print(f"Response: {response.text}")

# First, let's get the series IDs
response = requests.get("http://127.0.0.1:7227/api/series")
series_list = response.json().get("series", [])

jjk_id = None
csm_id = None
opm_id = None

for series in series_list:
    if series["title"] == "Jujutsu Kaisen":
        jjk_id = series["id"]
    elif series["title"] == "Chainsaw Man":
        csm_id = series["id"]
    elif series["title"] == "One Punch-Man":
        opm_id = series["id"]

print(f"Found series IDs - JJK: {jjk_id}, CSM: {csm_id}, OPM: {opm_id}")

# Add the volumes
if jjk_id:
    add_volume(jjk_id, 25, "Volume 25", "2025-10-01")

if csm_id:
    add_volume(csm_id, 16, "Volume 16", "2025-10-01")

if opm_id:
    add_volume(opm_id, 28, "Volume 28", "2025-10-15")

# Refresh the calendar
response = requests.post("http://127.0.0.1:7227/api/calendar/refresh")
print(f"\nRefreshing calendar: {response.status_code}")

# Check the calendar events
response = requests.get("http://127.0.0.1:7227/api/calendar?start_date=2025-10-01&end_date=2025-10-31")
print(f"\nCalendar events: {json.dumps(response.json(), indent=2)}")
