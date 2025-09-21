#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaDex constants.
"""

# Default headers for MangaDex API requests
DEFAULT_HEADERS = {
    "User-Agent": "MangaArr/1.0.0",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Base URLs
BASE_URL = "https://api.mangadex.org"
COVER_URL = "https://uploads.mangadex.org/covers"
MANGA_URL = "https://mangadex.org/title"
CHAPTER_URL = "https://mangadex.org/chapter"

# Status mapping
STATUS_MAPPING = {
    "ongoing": "ONGOING",
    "completed": "COMPLETED",
    "hiatus": "HIATUS",
    "cancelled": "CANCELLED",
    "published": "COMPLETED"
}
