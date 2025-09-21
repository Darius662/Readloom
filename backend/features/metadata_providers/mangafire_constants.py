#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaFire constants.
"""

# Default headers for MangaFire requests
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}

# Base URLs
BASE_URL = "https://mangafire.to"
SEARCH_URL = f"{BASE_URL}/filter"
MANGA_URL = f"{BASE_URL}/manga"
LATEST_URL = f"{BASE_URL}/latest"
