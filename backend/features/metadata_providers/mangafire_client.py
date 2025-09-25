#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaFire HTTP client helper.
"""

import requests
from typing import Dict, Any, Optional


def make_request(session: requests.Session, url: str, headers: Dict[str, str], 
                params: Optional[Dict[str, Any]] = None, logger=None) -> requests.Response:
    """Make an HTTP request to the MangaFire API.
    
    Args:
        session: The requests session to use.
        url: The URL to request.
        headers: HTTP headers to include.
        params: Optional query parameters.
        logger: Logger for error reporting.
            
    Returns:
        The HTTP response.
        
    Raises:
        requests.RequestException: If the request fails.
    """
    try:
        if logger:
            logger.info(f"Making request to {url} with params {params}")
        
        response = session.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        if logger:
            logger.info(f"Request successful, status code: {response.status_code}")
            
        return response
    except requests.RequestException as e:
        if logger:
            logger.error(f"Error making request to {url}: {e}")
        raise
