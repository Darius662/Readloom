#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Metadata providers for MangaArr.
This module contains the base classes and implementations for various metadata providers.
"""

from .base import MetadataProvider, MetadataProviderManager
from .myanimelist import MyAnimeListProvider
from .manga_api import MangaAPIProvider
from .vizmedia import VizMediaProvider

__all__ = [
    'MetadataProvider',
    'MetadataProviderManager',
    'MyAnimeListProvider',
    'MangaAPIProvider',
    'VizMediaProvider'
]
