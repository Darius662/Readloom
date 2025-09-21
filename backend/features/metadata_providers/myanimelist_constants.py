#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MyAnimeList constants.
"""

# Base URLs
BASE_URL = "https://api.myanimelist.net/v2"
MANGA_URL = "https://myanimelist.net/manga"

# Status mapping
STATUS_MAPPING = {
    "currently_publishing": "ONGOING",
    "finished": "COMPLETED",
    "not_yet_published": "ANNOUNCED",
    "on_hiatus": "HIATUS",
    "discontinued": "CANCELLED"
}
