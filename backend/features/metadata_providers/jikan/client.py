#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Jikan API client for MyAnimeList.
"""

import time
from typing import Dict, Any, Optional
import requests
import logging

logger = logging.getLogger(__name__)


def make_request(session: requests.Session, base_url: str, endpoint: str, 
                headers: Dict[str, str], params: Optional[Dict[str, Any]] = None, 
                rate_limit_delay: float = 0.4) -> Dict[str, Any]:
    """Make a request to the Jikan API.
    
    Args:
        session: The requests session.
        base_url: The base URL for the API.
        endpoint: The API endpoint.
        headers: The request headers.
        params: The query parameters.
        rate_limit_delay: Delay between requests to respect rate limits.
        
    Returns:
        The JSON response.
    """
    url = f"{base_url}/{endpoint}"
    try:
        logger.info(f"Making request to {url} with params {params}")
        # Rate limiting
        time.sleep(rate_limit_delay)
        
        response = session.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        logger.info(f"Request successful, status code: {response.status_code}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error making request to {url}: {e}")
        raise
