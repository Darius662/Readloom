#!/usr/bin/env python3
"""
Helper script to add manga to the static database.
This makes it easy to add accurate volume counts for manga that aren't in the database yet.
"""

import sys
import re

def add_manga_to_database():
    """Interactive script to add manga to the static database."""
    print("\n" + "="*80)
    print("ADD MANGA TO STATIC DATABASE")
    print("="*80 + "\n")
    
    print("This script will help you add manga to the static database.")
    print("You'll need to know the accurate chapter and volume counts.\n")
    
    # Get manga information
    title = input("Enter manga title (lowercase, e.g., 'dandadan'): ").strip().lower()
    if not title:
        print("Error: Title cannot be empty")
        return
    
    try:
        chapters = int(input("Enter total chapters: ").strip())
        volumes = int(input("Enter total volumes: ").strip())
    except ValueError:
        print("Error: Chapters and volumes must be numbers")
        return
    
    # Get aliases
    print("\nEnter alternative titles/aliases (optional):")
    print("  Examples: 'shingeki no kyojin' for 'attack on titan'")
    print("  Press Enter without typing anything when done")
    
    aliases = []
    while True:
        alias = input(f"  Alias {len(aliases) + 1} (or press Enter to skip): ").strip().lower()
        if not alias:
            break
        aliases.append(alias)
    
    # Generate the entry
    print("\n" + "="*80)
    print("GENERATED ENTRY")
    print("="*80 + "\n")
    
    if aliases:
        entry = f'    "{title}": {{"chapters": {chapters}, "volumes": {volumes}, "aliases": {aliases}}}'
    else:
        entry = f'    "{title}": {{"chapters": {chapters}, "volumes": {volumes}}}'
    
    print("Add this line to backend/features/scrapers/mangainfo/constants.py")
    print("in the POPULAR_MANGA_DATA dictionary:\n")
    print(entry)
    
    print("\n" + "="*80)
    print("INSTRUCTIONS")
    print("="*80 + "\n")
    print("1. Open: backend/features/scrapers/mangainfo/constants.py")
    print("2. Find the POPULAR_MANGA_DATA dictionary")
    print("3. Add the entry above (make sure to add a comma after the previous entry)")
    print("4. Save the file")
    print("5. Restart your application or re-import the series\n")
    
    # Offer to show the file location
    file_path = "backend\\features\\scrapers\\mangainfo\\constants.py"
    print(f"File location: {file_path}\n")
    
    # Show example of where to add it
    print("Example:")
    print("="*80)
    print('POPULAR_MANGA_DATA = {')
    print('    "one piece": {"chapters": 1112, "volumes": 108},')
    print('    "naruto": {"chapters": 700, "volumes": 72},')
    print('    # ... other entries ...')
    print(entry + ',  # <-- Add your new entry here')
    print('}')
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        add_manga_to_database()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\nError: {e}")
