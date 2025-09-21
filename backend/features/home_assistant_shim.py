#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Home Assistant integration module for MangaArr - compatibility shim.

This module re-exports all public functions from the home_assistant package.
The implementation has been moved to backend.features.home_assistant.
"""

from backend.features.home_assistant import (
    get_home_assistant_sensor_data,
    generate_home_assistant_config,
    get_home_assistant_setup_instructions
)

# Re-export all public functions
__all__ = [
    "get_home_assistant_sensor_data",
    "generate_home_assistant_config",
    "get_home_assistant_setup_instructions"
]
