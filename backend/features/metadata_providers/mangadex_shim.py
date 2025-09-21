#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaDex metadata provider - compatibility shim.

This module re-exports MangaDexProvider from the mangadex package.
The implementation has been moved to backend.features.metadata_providers.mangadex.provider.
"""

# Re-export MangaDexProvider from the package
from .mangadex.provider import MangaDexProvider
