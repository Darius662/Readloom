#!/usr/bin/env python3

from backend.features.scrapers.mangafire_scraper import MangaInfoProvider
from backend.base.logging import setup_logging

def test_scrapers(manga_titles):
    # Set up logging
    setup_logging("data/logs", "test_scraper.log")
    
    # Initialize the manga info provider
    provider = MangaInfoProvider()
    
    for title in manga_titles:
        print(f"\nTesting: {title}")
        
        # Get data from scraper
        chapters, volumes = provider.get_chapter_count(title)
        
        print(f"  Chapters: {chapters}")
        print(f"  Volumes: {volumes}")

if __name__ == "__main__":
    # Test a variety of manga titles
    test_manga = [
        "Kumo desu ga, Nani ka?",
        "One Piece",
        "Naruto",
        "Jujutsu Kaisen",
        "Berserk",
        "Attack on Titan",
        "Spy x Family",
        "Kaguya-sama",
        "Made in Abyss",
        "Solo Leveling"
    ]
    
    test_scrapers(test_manga)
