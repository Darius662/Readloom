#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chapter generation utilities for the Jikan API provider.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from .constants import MAL_URL

logger = logging.getLogger(__name__)


def add_simple_chapters(chapters: List[Dict[str, Any]], manga_id: str, 
                      chapter_count: int, start_date: str, end_date: str):
    """Add chapters with simple date assignment logic.
    
    Args:
        chapters: The list to add chapters to
        manga_id: The manga ID
        chapter_count: Number of chapters
        start_date: Publication start date
        end_date: Publication end date
    """
    # If we have publishing dates but can't interpolate, assign logically
    for i in range(1, chapter_count + 1):
        if i == 1 and start_date:
            chapter_date = start_date
        elif i == chapter_count and end_date:
            chapter_date = end_date
        elif start_date:  # For middle chapters, use start_date if available
            chapter_date = start_date
        else:  # No dates available
            chapter_date = datetime.now().strftime("%Y-%m-%d")  # Use current date as fallback
        
        chapters.append({
            "id": f"{manga_id}_{i}",
            "title": f"Chapter {i}",
            "number": str(i),
            "date": chapter_date,
            "url": f"{MAL_URL}/{manga_id}",
            "manga_id": manga_id
        })


def generate_chapter_list(manga_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a chapter list from manga data.
    
    Args:
        manga_id: The manga ID
        data: The manga data from Jikan API
        
    Returns:
        A dictionary containing chapters and other information
    """
    chapters = []
    start_date = None
    end_date = None
    publishing_status = "finished"
    
    if "data" in data:
        item = data["data"]
        chapter_count = item.get("chapters", 0)
        
        # Get publication dates and status
        if "published" in item:
            if "from" in item["published"] and item["published"]["from"]:
                start_date = item["published"]["from"].split("T")[0]
            if "to" in item["published"] and item["published"]["to"]:
                end_date = item["published"]["to"].split("T")[0]
        
        # Get the publishing status
        publishing_status = item.get("status", "finished").lower()
        
        if chapter_count:
            # If we have both start and end dates and a chapter count, we can estimate release dates
            if start_date and end_date and publishing_status == "finished" and chapter_count > 1:
                try:
                    # Calculate an estimated interval between releases
                    start = datetime.strptime(start_date, "%Y-%m-%d")
                    end = datetime.strptime(end_date, "%Y-%m-%d")
                    days_between = (end - start).days
                    interval = max(1, days_between // (chapter_count - 1))  # At least 1 day between chapters
                    
                    for i in range(1, chapter_count + 1):
                        # For first chapter, use start_date
                        # For last chapter, use end_date
                        # For others, interpolate dates between
                        if i == 1:
                            chapter_date = start_date
                        elif i == chapter_count:
                            chapter_date = end_date
                        else:
                            # Calculate an estimated date for this chapter
                            estimated_date = start + timedelta(days=interval * (i-1))
                            chapter_date = estimated_date.strftime("%Y-%m-%d")
                        
                        chapters.append({
                            "id": f"{manga_id}_{i}",
                            "title": f"Chapter {i}",
                            "number": str(i),
                            "date": chapter_date,
                            "url": f"{MAL_URL}/{manga_id}",
                            "manga_id": manga_id
                        })
                except Exception as date_error:
                    logger.warning(f"Error calculating chapter dates: {date_error}")
                    # Fall back to simpler method if date calculation fails
                    add_simple_chapters(chapters, manga_id, chapter_count, start_date, end_date)
            else:
                # Simpler method without date interpolation
                add_simple_chapters(chapters, manga_id, chapter_count, start_date, end_date)
        elif start_date:  # No chapter count but we have a start date
            # If no chapter count, create at least one chapter with the release date
            chapters.append({
                "id": f"{manga_id}_1",
                "title": "Chapter 1",
                "number": "1",
                "date": start_date,
                "url": f"{MAL_URL}/{manga_id}",
                "manga_id": manga_id
            })
        else:  # No chapter count, no dates
            chapters.append({
                "id": f"{manga_id}_1",
                "title": "Chapter 1",
                "number": "1",
                "date": datetime.now().strftime("%Y-%m-%d"),  # Use current date
                "url": f"{MAL_URL}/{manga_id}",
                "manga_id": manga_id
            })
    
    return {"chapters": chapters}
