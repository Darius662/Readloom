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
        # Search MangaDex API
        search_url = f"{MANGADEX_URL}/manga?title={manga_title.replace(' ', '+')}&limit=1"
        
        response = requests.get(search_url, timeout=10)
        if response.status_code != 200:
            return (0, 0)
            
        data = response.json()
        if not data.get('data') or len(data['data']) == 0:
            return (0, 0)
            
        # Get the first manga
        manga = data['data'][0]
        manga_id = manga['id']
        
        # Get chapters count through aggregate endpoint
        agg_url = f"{MANGADEX_URL}/manga/{manga_id}/aggregate"
        agg_response = requests.get(agg_url, timeout=10)
        
        if agg_response.status_code != 200:
            return (0, 0)
            
        agg_data = agg_response.json()
        
        # Count chapters and volumes
        volumes_data = agg_data.get('volumes', {})
        # Make sure volumes_data is a dictionary, not a list
        if isinstance(volumes_data, dict):
            volume_count = len(volumes_data)
            
            chapter_count = 0
            for vol_id, vol_data in volumes_data.items():
                chapter_count += len(vol_data.get('chapters', {}))
        elif isinstance(volumes_data, list):
            # Handle case where volumes data is a list
            volume_count = len(volumes_data)
            
            chapter_count = 0
            # Count chapters in a list format
            for vol_data in volumes_data:
                if isinstance(vol_data, dict) and 'chapters' in vol_data:
                    chapter_count += len(vol_data['chapters'])
        else:
            # If neither dict nor list, assume no data
            volume_count = 0
            chapter_count = 0
            
        if chapter_count > 0:
            LOGGER.info(f"MangaDex data for {manga_title}: {chapter_count} chapters, {volume_count} volumes")
            
        return (chapter_count, volume_count)
        
    except Exception as e:
        LOGGER.error(f"Error getting MangaDex data: {e}")
        return (0, 0)
