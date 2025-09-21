#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaFire scraper module for MangaArr - compatibility shim.

This module re-exports MangaInfoProvider from the mangainfo package.
The implementation has been moved to backend.features.scrapers.mangainfo.
"""

from backend.features.scrapers.mangainfo import MangaInfoProvider
