#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MyAnimeList metadata provider - compatibility shim.

This module re-exports MyAnimeListProvider from the myanimelist package.
The implementation has been moved to backend.features.metadata_providers.myanimelist.provider.
"""

# Re-export MyAnimeListProvider from the package
from .myanimelist.provider import MyAnimeListProvider
