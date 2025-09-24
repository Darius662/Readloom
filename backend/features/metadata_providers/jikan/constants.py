#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Constants for the Jikan API provider.
"""

# Base URLs
BASE_URL = "https://api.jikan.moe/v4"
MAL_URL = "https://myanimelist.net/manga"

# Headers
DEFAULT_HEADERS = {
    "User-Agent": "Readloom/1.0.0",
    "Accept": "application/json"
}

# Rate limiting
RATE_LIMIT_DELAY = 0.4  # seconds, Jikan API has a rate limit of 3 requests per second
