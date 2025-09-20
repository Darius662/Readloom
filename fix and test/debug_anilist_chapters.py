#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug script to check AniList chapter data
"""

from backend.features.metadata_providers.anilist import AniListProvider
import json

def main():
    # Initialize AniList provider
    anilist = AniListProvider(enabled=True)
    
    # Test manga IDs - using some popular manga
    test_ids = [
        "30002",  # Berserk
        "30013",  # One Piece
        "132475", # Chainsaw Man
        "105778", # Solo Leveling
        "105934"  # Kimetsu no Yaiba
    ]
    
    for manga_id in test_ids:
        print(f"\n{'=' * 40}")
        print(f"Testing manga ID: {manga_id}")
        
        # Get manga details
        manga = anilist.get_manga_details(manga_id)
        print(f"Title: {manga.get('title', 'Unknown')}")
        print(f"Chapters count: {manga.get('chapters', 0)}")
        
        # Get chapter list
        chapter_list = anilist.get_chapter_list(manga_id)
        
        # Check the returned type
        print(f"Return type: {type(chapter_list)}")
        
        # How many chapters are in the list?
        if isinstance(chapter_list, dict) and "chapters" in chapter_list:
            chapters = chapter_list["chapters"]
            print(f"Number of chapters returned: {len(chapters)}")
            # Print first 3 chapters if any
            if chapters:
                print("\nSample chapters:")
                for i, chapter in enumerate(chapters[:3]):
                    print(f"  {i+1}. ID: {chapter.get('id')}, Number: {chapter.get('number')}, Date: {chapter.get('date')}")
        elif isinstance(chapter_list, list):
            print(f"Number of chapters returned: {len(chapter_list)}")
            # Print first 3 chapters if any
            if chapter_list:
                print("\nSample chapters:")
                for i, chapter in enumerate(chapter_list[:3]):
                    print(f"  {i+1}. ID: {chapter.get('id')}, Number: {chapter.get('number')}, Date: {chapter.get('date')}")
        else:
            print(f"Unexpected return type: {chapter_list}")
            
if __name__ == "__main__":
    main()
