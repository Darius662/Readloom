#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def search_manga(title, provider="MangaDex"):
    response = requests.get(
        f"http://127.0.0.1:7227/api/metadata/search",
        params={"query": title, "provider": provider}
    )
    if response.status_code == 200:
        results = response.json()
        if provider in results.get("results", {}):
            return results["results"][provider][0]  # Return first match
    return None

def import_manga(manga_id, provider):
    response = requests.post(
        f"http://127.0.0.1:7227/api/metadata/import/{provider}/{manga_id}"
    )
    print(f"Import response: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code == 200:
        result = response.json()
        return result.get("series_id")
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

# Search and import manga
print("Searching and importing manga...")

# Jujutsu Kaisen
print("\nProcessing Jujutsu Kaisen...")
jjk = search_manga("Jujutsu Kaisen")
if jjk:
    print(f"Found JJK: {jjk['title']} ({jjk['id']})")
    jjk_id = import_manga(jjk['id'], "MangaDex")
    if jjk_id:
        add_volume(jjk_id, 25, "Volume 25", "2025-10-01")

# Chainsaw Man
print("\nProcessing Chainsaw Man...")
csm = search_manga("Chainsaw Man")
if csm:
    print(f"Found CSM: {csm['title']} ({csm['id']})")
    csm_id = import_manga(csm['id'], "MangaDex")
    if csm_id:
        add_volume(csm_id, 16, "Volume 16", "2025-10-01")

# One Punch-Man
print("\nProcessing One Punch-Man...")
opm = search_manga("One Punch-Man")
if opm:
    print(f"Found OPM: {opm['title']} ({opm['id']})")
    opm_id = import_manga(opm['id'], "MangaDex")
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
