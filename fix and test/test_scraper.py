#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for the manga info provider.
"""

from backend.features.scrapers.mangafire_scraper import MangaInfoProvider

def main():
    print("Testing manga info provider for all manga...")
    
    # Initialize the provider
    provider = MangaInfoProvider()
    
    # Test popular and less popular manga
    test_manga = [
        # Popular manga with static data
        "One Piece",
        "Naruto",
        "Berserk",
        "Dragon Ball",
        "Attack on Titan",
        
        # Less popular/niche manga that should use web scraping
        "Spy x Family",
        "Dr. Stone",
        "Slam Dunk",
        "Vagabond",
        "Vinland Saga",
        
        # Very specific/obscure titles to test fallback estimation
        "The Beginning After The End",
        "Omniscient Reader's Viewpoint",
        "Solo Leveling",
        "Sono Bisque Doll wa Koi wo Suru",
        "Record of Ragnarok"
    ]
    
    print("\nResults:")
    print("-" * 50)
    
    for manga in test_manga:
        print(f"Fetching data for {manga}...")
        chapters, volumes = provider.get_chapter_count(manga)
        print(f"{manga}: {chapters} chapters, {volumes} volumes")
        print("-" * 50)

if __name__ == "__main__":
    main()
