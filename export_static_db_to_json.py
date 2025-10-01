#!/usr/bin/env python3
"""
Export the existing static database to JSON for easier editing.
"""

import json
import sys
sys.path.insert(0, '.')

from backend.features.scrapers.mangainfo.constants import POPULAR_MANGA_DATA

# Convert to JSON-friendly format
json_db = {}
for key, data in POPULAR_MANGA_DATA.items():
    json_db[key] = {
        'chapters': data['chapters'],
        'volumes': data['volumes']
    }
    if 'aliases' in data:
        json_db[key]['aliases'] = data['aliases']

# Save to JSON
output_file = 'static_manga_database.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(json_db, f, indent=2, ensure_ascii=False)

print(f"✓ Exported {len(json_db)} manga to {output_file}")
print(f"\nYou can now:")
print(f"1. Edit this JSON file to add more manga")
print(f"2. Use it to update constants.py")
print(f"3. Load it dynamically in your code")
