#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Metadata providers for Readloom.
This module contains the base classes and implementations for various metadata providers.
"""

from .base import MetadataProvider, MetadataProviderManager
from .mangafire import MangaFireProvider
from .myanimelist import MyAnimeListProvider
from .manga_api import MangaAPIProvider

__all__ = [
    'MetadataProvider',
    'MetadataProviderManager',
    'MangaFireProvider',
    'MyAnimeListProvider',
    'MangaAPIProvider'
]
