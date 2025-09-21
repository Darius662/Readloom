#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MyAnimeList API client helper.
"""

import requests
from typing import Dict, Any, Optional, List, Union


def make_request(session: requests.Session, url: str, headers: Dict[str, str], 
                params: Optional[Dict[str, Any]] = None, logger=None) -> Dict[str, Any]:
    """Make an HTTP request to the MyAnimeList API.
    
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


def search_manga(session: requests.Session, base_url: str, headers: Dict[str, str], 
                query: str, limit: int = 10, logger=None) -> Dict[str, Any]:
    """Search for manga on MyAnimeList API.
    
    Args:
        session: The requests session to use.
        base_url: The base URL for the MyAnimeList API.
        headers: HTTP headers to include.
        query: The search query.
        limit: Maximum number of results.
        logger: Logger for error reporting.
            
    Returns:
        The search results as a dictionary.
    """
    url = f"{base_url}/manga"
    params = {
        "q": query,
        "limit": limit,
        "fields": "id,title,main_picture,alternative_titles,synopsis,mean,status,genres,authors{first_name,last_name},num_volumes,num_chapters,start_date,end_date"
    }
    
    return make_request(session, url, headers, params, logger)


def get_manga_details(session: requests.Session, base_url: str, headers: Dict[str, str], 
                     manga_id: str, logger=None) -> Dict[str, Any]:
    """Get manga details from MyAnimeList API.
    
    Args:
        session: The requests session to use.
        base_url: The base URL for the MyAnimeList API.
        headers: HTTP headers to include.
        manga_id: The manga ID.
        logger: Logger for error reporting.
            
    Returns:
        The manga details as a dictionary.
    """
    url = f"{base_url}/manga/{manga_id}"
    params = {
        "fields": "id,title,main_picture,alternative_titles,synopsis,mean,status,genres,authors{first_name,last_name},num_volumes,num_chapters,start_date,end_date,related_manga,recommendations"
    }
    
    return make_request(session, url, headers, params, logger)


def get_manga_ranking(session: requests.Session, base_url: str, headers: Dict[str, str], 
                     ranking_type: str = "all", limit: int = 10, logger=None) -> Dict[str, Any]:
    """Get manga ranking from MyAnimeList API.
    
    Args:
        session: The requests session to use.
        base_url: The base URL for the MyAnimeList API.
        headers: HTTP headers to include.
        ranking_type: The ranking type.
        limit: Maximum number of results.
        logger: Logger for error reporting.
            
    Returns:
        The manga ranking as a dictionary.
    """
    url = f"{base_url}/manga/ranking"
    params = {
        "ranking_type": ranking_type,
        "limit": limit,
        "fields": "id,title,main_picture,alternative_titles,synopsis,mean,status,genres,authors{first_name,last_name},num_volumes,num_chapters"
    }
    
    return make_request(session, url, headers, params, logger)
