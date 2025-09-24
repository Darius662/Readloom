#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum, auto
from typing import Dict, List, NamedTuple, Set, Tuple, Union


class StartType(Enum):
    """The type of (re)start."""
    STARTUP = 131
    RESTART = 132
    UPDATE = 133


class Constants:
    """Constants used throughout the application."""
    MIN_PYTHON_VERSION: Tuple[int, int] = (3, 8)
    SUB_PROCESS_TIMEOUT: int = 10
    DEFAULT_PORT: int = 7227
    DEFAULT_HOST: str = "0.0.0.0"
    DEFAULT_URL_BASE: str = ""
    DEFAULT_LOG_LEVEL: str = "INFO"
    DEFAULT_LOG_ROTATION: int = 5
    DEFAULT_LOG_SIZE: int = 10
    DEFAULT_DB_NAME: str = "readloom.db"
    DEFAULT_LOG_NAME: str = "readloom.log"
    DEFAULT_CONFIG_NAME: str = "config"
    DEFAULT_METADATA_CACHE_DAYS: int = 7
    DEFAULT_CALENDAR_RANGE_DAYS: int = 14
    DEFAULT_CALENDAR_REFRESH_HOURS: int = 12
    DEFAULT_TASK_INTERVAL_MINUTES: int = 60
    DEFAULT_EBOOK_STORAGE: str = "ebooks"
    DEFAULT_ROOT_FOLDERS: List[Dict[str, str]] = []  # Empty list by default


class Settings(NamedTuple):
    """Settings for the application."""
    host: str
    port: int
    url_base: str
    log_level: str
    log_rotation: int
    log_size: int
    metadata_cache_days: int
    calendar_range_days: int
    calendar_refresh_hours: int
    task_interval_minutes: int
    ebook_storage: str
    root_folders: List[Dict[str, str]]  # List of root folders with path and name


class MangaFormat(Enum):
    """Format of manga/comic."""
    PHYSICAL = auto()
    DIGITAL = auto()
    UNKNOWN = auto()


class ReleaseStatus(Enum):
    """Status of a manga/comic release."""
    ANNOUNCED = auto()
    RELEASED = auto()
    DELAYED = auto()
    CANCELLED = auto()


class SeriesStatus(Enum):
    """Status of a manga/comic series."""
    ONGOING = auto()
    COMPLETED = auto()
    HIATUS = auto()
    CANCELLED = auto()
    UNKNOWN = auto()


class ReadStatus(Enum):
    """Read status of a manga/comic."""
    UNREAD = auto()
    READING = auto()
    READ = auto()


class MetadataSource(Enum):
    """Source of metadata."""
    MANGADEX = auto()
    COMICVINE = auto()
    MANUAL = auto()
    UNKNOWN = auto()


class ContentType(Enum):
    """Type of content."""
    MANGA = auto()    # Japanese comics
    MANHWA = auto()   # Korean comics
    MANHUA = auto()   # Chinese comics
    COMICS = auto()   # Western comics
    NOVEL = auto()    # Light novels or text-based stories
    BOOK = auto()     # Regular books
    OTHER = auto()    # Other types of content
