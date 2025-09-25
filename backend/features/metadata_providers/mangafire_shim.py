#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaFire metadata provider - compatibility shim.

This module re-exports MangaFireProvider from the mangafire package.
The implementation has been moved to backend.features.metadata_providers.mangafire.provider.
"""

# Re-export MangaFireProvider from the package
from .mangafire.provider import MangaFireProvider
