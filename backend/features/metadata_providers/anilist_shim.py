#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AniList metadata provider - compatibility shim.

This module re-exports AniListProvider from the anilist package.
The implementation has been moved to backend.features.metadata_providers.anilist.provider.
"""

# Re-export AniListProvider from the package
from .anilist.provider import AniListProvider
