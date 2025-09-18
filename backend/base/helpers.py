#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import Optional, Tuple, Union


def check_min_python_version(major: int, minor: int) -> bool:
    """Check if the current Python version is at least the given version.

    Args:
        major (int): The major version to check.
        minor (int): The minor version to check.

    Returns:
        bool: True if the current Python version is at least the given version.
    """
    current_major, current_minor = sys.version_info[:2]
    if current_major > major:
        return True
    if current_major == major and current_minor >= minor:
        return True
    
    print(f"ERROR: Python {major}.{minor} or higher is required. "
          f"You are using Python {current_major}.{current_minor}.")
    return False


def get_python_exe() -> Optional[str]:
    """Get the path to the Python executable.

    Returns:
        Optional[str]: The path to the Python executable, or None if not found.
    """
    if hasattr(sys, 'executable') and sys.executable:
        return sys.executable
    
    return None


def ensure_dir_exists(path: Union[str, Path]) -> bool:
    """Ensure that the given directory exists.

    Args:
        path (Union[str, Path]): The path to the directory.

    Returns:
        bool: True if the directory exists or was created, False otherwise.
    """
    if isinstance(path, str):
        path = Path(path)
    
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_app_dir() -> Path:
    """Get the application directory.

    Returns:
        Path: The application directory.
    """
    return Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def get_data_dir() -> Path:
    """Get the data directory.

    Returns:
        Path: The data directory.
    """
    app_dir = get_app_dir()
    data_dir = app_dir / "data"
    ensure_dir_exists(data_dir)
    return data_dir


def get_config_dir() -> Path:
    """Get the configuration directory.

    Returns:
        Path: The configuration directory.
    """
    data_dir = get_data_dir()
    config_dir = data_dir / "config"
    ensure_dir_exists(config_dir)
    return config_dir


def get_logs_dir() -> Path:
    """Get the logs directory.

    Returns:
        Path: The logs directory.
    """
    data_dir = get_data_dir()
    logs_dir = data_dir / "logs"
    ensure_dir_exists(logs_dir)
    return logs_dir
