#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calendar module for MangaArr - compatibility shim.

This module re-exports all public functions from the calendar package.
The implementation has been moved to backend.features.calendar.
"""

from backend.features.calendar import (
    update_calendar,
    get_calendar_events,
)

# Re-export all public functions
__all__ = [
    "update_calendar",
    "get_calendar_events",
]
