#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import timedelta
from typing import Any, Dict, Tuple


def determine_publication_schedule(manga_details: Dict[str, Any]) -> Tuple[int, timedelta]:
    """
    Determine the publication schedule based on manga metadata.

    Args:
        manga_details: The manga details.

    Returns:
        A tuple of (publication_day, interval) where publication_day is the day of week (0=Monday, 6=Sunday)
        and interval is the timedelta between chapters.
    """
    # Get relevant metadata
    title = str(manga_details.get("title", "")).lower()
    genres = [str(g).lower() for g in manga_details.get("genres", [])] if isinstance(manga_details.get("genres"), list) else []
    status = str(manga_details.get("status", "")).lower()

    # Default schedule: Monday release every 14 days (bi-weekly)
    default_day = 0  # Monday (0=Monday, 6=Sunday in Python's datetime)
    default_interval = timedelta(days=14)  # Bi-weekly

    # Detect if it's a Weekly Shonen Jump series (releases on Sunday in Japan, Monday in most Western countries)
    weekly_jump_patterns = ["one piece", "my hero academia", "black clover", "jujutsu kaisen", "chainsaw man"]
    if any(pattern in title for pattern in weekly_jump_patterns):
        return (0, timedelta(days=7))  # Monday, Weekly

    # Monthly seinen/josei magazines often release mid-month
    monthly_patterns = ["berserk", "vinland saga", "vagabond"]
    if any(pattern in title for pattern in monthly_patterns) or "seinen" in genres:
        return (3, timedelta(days=30))  # Thursday, Monthly

    # Detect manhwa (Korean comics) which often update on specific weekdays
    manhwa_patterns = ["solo leveling", "tower of god", "god of high school"]
    if any(pattern in title for pattern in manhwa_patterns):
        return (2, timedelta(days=7))  # Wednesday, Weekly

    # Detect if it's likely a weekly series based on genre and status
    if "shounen" in genres and status in ["ongoing", "releasing"]:
        # Many weekly shounen release on Sunday/Monday
        return (6, timedelta(days=7))  # Sunday, Weekly

    # Detect if it's likely a monthly series
    if any(g in genres for g in ["seinen", "josei"]) or "monthly" in title:
        # Monthly series, pick a consistent day (15th of month)
        return (4, timedelta(days=30))  # Friday, Monthly

    # Use default for everything else
    return (default_day, default_interval)
