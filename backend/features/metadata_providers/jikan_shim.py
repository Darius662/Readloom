#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Jikan API metadata provider for MyAnimeList - compatibility shim.

This module re-exports JikanProvider from the jikan package.
The implementation has been moved to backend.features.metadata_providers.jikan.provider.
"""

# Re-export JikanProvider from the package
from .jikan.provider import JikanProvider
