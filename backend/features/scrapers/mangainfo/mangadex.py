#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaDex API client for MangaInfo provider.
"""

import requests
from typing import Tuple

from backend.base.logging import LOGGER
from .constants import MANGADEX_URL


def get_mangadex_data(manga_title: str) -> Tuple[int, int]:
    """
    Get chapter and volume counts from MangaDex API.
    
    Args:
        manga_title: The manga title.
        
    Returns:
        Tuple[int, int]: (chapter_count, volume_count)
    """
    try:
        # Search MangaDex API - get top 5 results to find best match
        search_url = f"{MANGADEX_URL}/manga?title={manga_title.replace(' ', '+')}&limit=5&includes[]=cover_art"
        
        response = requests.get(search_url, timeout=10)
        if response.status_code != 200:
            return (0, 0)
            
        data = response.json()
        if not data.get('data') or len(data['data']) == 0:
            return (0, 0)
        
        # Find the best matching manga (prefer manga over doujinshi, oneshots, etc.)
        best_manga = None
        manga_title_lower = manga_title.lower()
        
        for manga in data['data']:
            attributes = manga.get('attributes', {})
            
            # Get title in various languages
            titles = attributes.get('title', {})
            alt_titles = attributes.get('altTitles', [])
            
            # Check if title matches
            title_match = False
            for lang, title in titles.items():
                if manga_title_lower in title.lower() or title.lower() in manga_title_lower:
                    title_match = True
                    break
            
            # Check alt titles
            if not title_match:
                for alt_title_dict in alt_titles:
                    for lang, alt_title in alt_title_dict.items():
                        if manga_title_lower in alt_title.lower() or alt_title.lower() in manga_title_lower:
                            title_match = True
                            break
            
            # Prefer manga over doujinshi/oneshot
            publication_demographic = attributes.get('publicationDemographic')
            
            # Skip doujinshi and oneshots unless it's the only match
            if title_match:
                if publication_demographic in ['shounen', 'seinen', 'shoujo', 'josei']:
                    best_manga = manga
                    break  # Found a good match
                elif not best_manga:
                    best_manga = manga  # Use as fallback
        
        if not best_manga:
            best_manga = data['data'][0]  # Use first result as last resort
        
        manga_id = best_manga['id']
        attributes = best_manga.get('attributes', {})
        
        # Try to get lastVolume and lastChapter from attributes (most reliable)
        last_volume = attributes.get('lastVolume')
        last_chapter = attributes.get('lastChapter')
        
        # Convert to integers if they exist and are numeric
        volume_count_from_attr = 0
        chapter_count_from_attr = 0
        
        if last_volume and last_volume.isdigit():
            volume_count_from_attr = int(last_volume)
        if last_chapter and last_chapter.isdigit():
            chapter_count_from_attr = int(last_chapter)
        
        # If we have both from attributes, use them (most reliable)
        if volume_count_from_attr > 0 and chapter_count_from_attr > 0:
            LOGGER.info(f"MangaDex data for {manga_title}: {chapter_count_from_attr} chapters, {volume_count_from_attr} volumes (from attributes)")
            return (chapter_count_from_attr, volume_count_from_attr)
        
        # Otherwise, try aggregate endpoint (without language filter to get all volumes)
        agg_url = f"{MANGADEX_URL}/manga/{manga_id}/aggregate"
        agg_response = requests.get(agg_url, timeout=10)
        
        if agg_response.status_code != 200:
            # Fall back to attribute data if available
            if volume_count_from_attr > 0:
                return (chapter_count_from_attr or 0, volume_count_from_attr)
            return (0, 0)
            
        agg_data = agg_response.json()
        
        # Count chapters and volumes from aggregate
        volumes_data = agg_data.get('volumes', {})
        volume_count_from_agg = 0
        chapter_count_from_agg = 0
        
        if isinstance(volumes_data, dict):
            # Filter out 'none' volumes (chapters without volume assignment)
            volume_count_from_agg = len([v for v in volumes_data.keys() if v != 'none'])
            
            for vol_id, vol_data in volumes_data.items():
                chapter_count_from_agg += len(vol_data.get('chapters', {}))
        
        # Use the higher count between attributes and aggregate
        final_volume_count = max(volume_count_from_attr, volume_count_from_agg)
        final_chapter_count = max(chapter_count_from_attr, chapter_count_from_agg)
        
        if final_chapter_count > 0 or final_volume_count > 0:
            source = "attributes" if volume_count_from_attr >= volume_count_from_agg else "aggregate"
            LOGGER.info(f"MangaDex data for {manga_title}: {final_chapter_count} chapters, {final_volume_count} volumes (from {source})")
            
        return (final_chapter_count, final_volume_count)
        
    except Exception as e:
        LOGGER.error(f"Error getting MangaDex data: {e}")
        return (0, 0)
