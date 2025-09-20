#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def add_series(title, author, status="PUBLISHING"):
    data = {
        "title": title,
        "author": author,
        "status": status
    }
    
    response = requests.post(
        "http://127.0.0.1:7227/api/series",
        json=data
    )
    if response.status_code == 201:
        return response.json()["series"]["id"]
    print(f"Error adding series {title}: {response.status_code}")
    print(f"Response: {response.text}")
    return None

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

# Add series
print("Adding series...")
jjk_id = add_series("Jujutsu Kaisen", "Akutami, Gege")
csm_id = add_series("Chainsaw Man", "Fujimoto, Tatsuki")
opm_id = add_series("One Punch-Man", "ONE, Murata Yusuke")

print(f"\nSeries IDs - JJK: {jjk_id}, CSM: {csm_id}, OPM: {opm_id}")

# Add the volumes
print("\nAdding volumes...")
if jjk_id:
    add_volume(jjk_id, 25, "Volume 25", "2025-10-01")

if csm_id:
    add_volume(csm_id, 16, "Volume 16", "2025-10-01")

if opm_id:
    add_volume(opm_id, 28, "Volume 28", "2025-10-15")

# Refresh the calendar
print("\nRefreshing calendar...")
response = requests.post("http://127.0.0.1:7227/api/calendar/refresh")
print(f"Calendar refresh status: {response.status_code}")

# Check the calendar events
print("\nChecking calendar events...")
response = requests.get("http://127.0.0.1:7227/api/calendar?start_date=2025-10-01&end_date=2025-10-31")
print(f"Calendar events: {json.dumps(response.json(), indent=2)}")
