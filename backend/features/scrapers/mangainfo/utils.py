#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility functions for MangaInfo provider.
"""

import random
from typing import Dict

from .constants import USER_AGENTS


def get_random_headers() -> Dict[str, str]:
    """
    Get randomized headers to avoid detection.
    
    Returns:
        Dict[str, str]: Random HTTP headers.
    """
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }


def get_estimated_data(manga_title: str) -> tuple[int, int]:
    """
    Get estimated chapter and volume counts based on title and common patterns.
    
    Args:
        manga_title: The manga title.
        
    Returns:
        tuple[int, int]: Estimated (chapter_count, volume_count).
    """
    words = len(manga_title.split())
    word_count_factor = 1.0
    
    # Adjust based on word count (shorter titles often have more chapters)
    if words == 1:
        word_count_factor = 1.5  # One-word titles often have more chapters
    elif words >= 4:
        word_count_factor = 0.6  # Long titles usually have fewer chapters
        
    # Check for common patterns that suggest longer series
    if any(term in manga_title.lower() for term in ['chronicles', 'saga', 'legend', 'adventure']):
        word_count_factor *= 1.3
        
    # Base estimate
    base_chapters = 75
    
    # Final calculation
    chapter_estimate = int(base_chapters * word_count_factor)
    volume_estimate = max(1, chapter_estimate // 10)
    
    return (chapter_estimate, volume_estimate)
