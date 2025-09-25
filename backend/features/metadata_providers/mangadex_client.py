#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaDex API client helper.
"""

import requests
from typing import Dict, Any, Optional, List, Union


def make_request(session: requests.Session, url: str, headers: Dict[str, str], 
                params: Optional[Dict[str, Any]] = None, logger=None) -> Dict[str, Any]:
    """Make an HTTP request to the MangaDex API.
    
    Args:
        session: The requests session to use.
        url: The URL to request.
        headers: HTTP headers to include.
        params: Optional query parameters.
        logger: Logger for error reporting.
            
    Returns:
        The JSON response as a dictionary.
    """
    try:
        if logger:
            logger.info(f"Making request to {url} with params {params}")
        
        response = session.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        if logger:
            logger.info(f"Request successful, status code: {response.status_code}")
            
        return response.json()
    except requests.RequestException as e:
        if logger:
            logger.error(f"Error making request to {url}: {e}")
        return {}


def get_manga_by_id(session: requests.Session, base_url: str, headers: Dict[str, str], 
                   manga_id: str, logger=None) -> Dict[str, Any]:
    """Get manga details by ID from MangaDex API.
    
    Args:
        session: The requests session to use.
        base_url: The base URL for the MangaDex API.
        headers: HTTP headers to include.
        manga_id: The manga ID.
        logger: Logger for error reporting.
            
    Returns:
        The manga details as a dictionary.
    """
    url = f"{base_url}/manga/{manga_id}"
    params = {
        "includes[]": ["cover_art", "author", "artist"]
    }
    
    return make_request(session, url, headers, params, logger)


def search_manga(session: requests.Session, base_url: str, headers: Dict[str, str], 
                query: str, page: int = 1, logger=None) -> Dict[str, Any]:
    """Search for manga on MangaDex API.
    
    Args:
        session: The requests session to use.
        base_url: The base URL for the MangaDex API.
        headers: HTTP headers to include.
        query: The search query.
        page: The page number.
        logger: Logger for error reporting.
            
    Returns:
        The search results as a dictionary.
    """
    url = f"{base_url}/manga"
    params = {
        "title": query,
        "limit": 10,
        "offset": (page - 1) * 10,
        "includes[]": ["cover_art", "author", "artist"],
        "contentRating[]": ["safe", "suggestive", "erotica", "pornographic"]
    }
    
    return make_request(session, url, headers, params, logger)


def get_manga_chapters(session: requests.Session, base_url: str, headers: Dict[str, str], 
                      manga_id: str, logger=None) -> Dict[str, Any]:
    """Get chapters for a manga from MangaDex API.
    
    Args:
        session: The requests session to use.
        base_url: The base URL for the MangaDex API.
        headers: HTTP headers to include.
        manga_id: The manga ID.
        logger: Logger for error reporting.
            
    Returns:
        The chapters as a dictionary.
    """
    url = f"{base_url}/manga/{manga_id}/feed"
    params = {
        "limit": 500,
        "translatedLanguage[]": ["en"],
        "order[chapter]": "asc"
    }
    
    return make_request(session, url, headers, params, logger)


def get_chapter_images(session: requests.Session, base_url: str, headers: Dict[str, str], 
                      chapter_id: str, logger=None) -> Dict[str, Any]:
    """Get images for a chapter from MangaDex API.
    
    Args:
        session: The requests session to use.
        base_url: The base URL for the MangaDex API.
        headers: HTTP headers to include.
        chapter_id: The chapter ID.
        logger: Logger for error reporting.
            
    Returns:
        The chapter images as a dictionary.
    """
    url = f"{base_url}/at-home/server/{chapter_id}"
    
    return make_request(session, url, headers, None, logger)


def get_latest_releases(session: requests.Session, base_url: str, headers: Dict[str, str], 
                       page: int = 1, logger=None) -> Dict[str, Any]:
    """Get latest manga releases from MangaDex API.
    
    Args:
        session: The requests session to use.
        base_url: The base URL for the MangaDex API.
        headers: HTTP headers to include.
        page: The page number.
        logger: Logger for error reporting.
            
    Returns:
        The latest releases as a dictionary.
    """
    url = f"{base_url}/manga"
    params = {
        "limit": 10,
        "offset": (page - 1) * 10,
        "includes[]": ["cover_art", "author", "artist"],
        "contentRating[]": ["safe", "suggestive", "erotica", "pornographic"],
        "order[updatedAt]": "desc"
    }
    
    return make_request(session, url, headers, params, logger)
