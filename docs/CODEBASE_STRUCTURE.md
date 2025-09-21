# MangaArr Codebase Structure

This document provides an overview of the MangaArr codebase structure after the modularization refactoring.

## Overview

MangaArr's backend has been refactored to follow a modular package-based structure. Large monolithic files have been split into smaller, focused modules organized into packages. This improves maintainability, readability, and makes the codebase easier to extend.

## Directory Structure

```
backend/
├── base/                     # Base utilities and common functionality
│   ├── custom_exceptions.py  # Custom exception classes
│   ├── definitions.py        # Constant definitions and enums
│   ├── helpers.py            # Helper functions
│   └── logging.py            # Logging configuration
│
├── features/                 # Core application features
│   ├── calendar/             # Calendar functionality
│   │   ├── __init__.py       # Package exports
│   │   └── calendar.py       # Calendar implementation
│   │
│   ├── collection/           # Collection management
│   │   ├── __init__.py       # Package exports
│   │   ├── mutations.py      # Write operations
│   │   ├── queries.py        # Read operations
│   │   ├── schema.py         # Table definitions
│   │   └── stats.py          # Collection statistics
│   │
│   ├── home_assistant/       # Home Assistant integration
│   │   ├── __init__.py       # Package exports
│   │   ├── config.py         # Configuration generation
│   │   └── data.py           # Sensor data collection
│   │
│   ├── metadata_providers/   # Metadata providers
│   │   ├── anilist/          # AniList provider
│   │   │   ├── __init__.py   # Package exports
│   │   │   ├── client.py     # GraphQL client
│   │   │   ├── constants.py  # Constants and patterns
│   │   │   ├── provider.py   # Provider implementation
│   │   │   └── schedule.py   # Publication schedule logic
│   │   │
│   │   ├── jikan/            # Jikan (MyAnimeList) provider
│   │   │   ├── __init__.py   # Package exports
│   │   │   ├── chapters.py   # Chapter generation
│   │   │   ├── client.py     # API client
│   │   │   ├── constants.py  # Constants and URLs
│   │   │   ├── mapper.py     # Data mapping
│   │   │   └── provider.py   # Provider implementation
│   │   │
│   │   ├── mangadex/         # MangaDex provider
│   │   │   ├── __init__.py   # Package exports
│   │   │   ├── client.py     # API client
│   │   │   ├── constants.py  # Constants and URLs
│   │   │   ├── mapper.py     # Data mapping
│   │   │   └── provider.py   # Provider implementation
│   │   │
│   │   ├── mangafire/        # MangaFire provider
│   │   │   ├── __init__.py   # Package exports
│   │   │   ├── client.py     # HTTP client
│   │   │   ├── constants.py  # Constants and URLs
│   │   │   ├── parser.py     # HTML parsing
│   │   │   └── provider.py   # Provider implementation
│   │   │
│   │   ├── myanimelist/      # MyAnimeList provider
│   │   │   ├── __init__.py   # Package exports
│   │   │   ├── client.py     # API client
│   │   │   ├── constants.py  # Constants and URLs
│   │   │   ├── mapper.py     # Data mapping
│   │   │   └── provider.py   # Provider implementation
│   │   │
│   │   ├── base.py           # Base provider class
│   │   ├── manager.py        # Provider manager
│   │   └── setup.py          # Provider initialization
│   │
│   ├── metadata_service/     # Metadata service
│   │   ├── __init__.py       # Package exports
│   │   ├── cache.py          # Cache operations
│   │   ├── facade.py         # Public API
│   │   └── provider_gateway.py # Provider resolution
│   │
│   ├── notifications/        # Notification system
│   │   ├── __init__.py       # Package exports
│   │   ├── channels.py       # Notification channels
│   │   ├── notifications.py  # Core notification logic
│   │   ├── releases.py       # Release notifications
│   │   ├── schema.py         # Table definitions
│   │   ├── settings.py       # Notification settings
│   │   └── subscriptions.py  # Series subscriptions
│   │
│   ├── scrapers/             # Web scrapers
│   │   ├── mangainfo/        # Manga info provider
│   │   │   ├── __init__.py   # Package exports
│   │   │   ├── constants.py  # Constants and static data
│   │   │   ├── mangadex.py   # MangaDex scraper
│   │   │   ├── mangafire.py  # MangaFire scraper
│   │   │   ├── mangapark.py  # MangaPark scraper
│   │   │   ├── provider.py   # Provider implementation
│   │   │   └── utils.py      # Utility functions
│   │
│   ├── calendar.py           # Calendar compatibility shim
│   ├── collection.py         # Collection compatibility shim
│   ├── home_assistant.py     # Home Assistant compatibility shim
│   ├── homarr.py             # Homarr integration
│   ├── metadata_service.py   # Metadata service compatibility shim
│   └── notifications.py      # Notifications compatibility shim
│
├── internals/                # Internal application components
│   ├── db.py                 # Database connection and queries
│   ├── server.py             # Server configuration
│   └── settings.py           # Application settings
│
└── migrations/               # Database migrations
    ├── 0004_add_confirmed_release_flags.py
    └── 0005_add_manga_downloader_tables.py
```

## Package Structure

Each feature package follows a similar structure:

1. **`__init__.py`**: Exports the public API of the package
2. **Core modules**: Implement the feature's functionality
3. **Compatibility shim**: Original filename that re-exports from the package

## Compatibility Shims

To maintain backward compatibility, each refactored module includes a compatibility shim. For example:

```python
# backend/features/notifications.py (compatibility shim)
from backend.features.notifications import (
    setup_notifications_tables,
    create_notification,
    get_notifications,
    # ... other exports
)

__all__ = [
    "setup_notifications_tables",
    "create_notification",
    "get_notifications",
    # ... other exports
]
```

This allows existing code to continue importing from the original module paths without breaking changes.

## Metadata Providers

The metadata providers have been refactored into individual packages:

- **AniList**: GraphQL-based provider for anime/manga metadata
- **Jikan**: REST API client for MyAnimeList
- **MangaDex**: API client for MangaDex manga database
- **MangaFire**: Web scraper for MangaFire website
- **MyAnimeList**: Direct API client for MyAnimeList

Each provider package includes:
- **Client**: Handles API requests
- **Constants**: Stores URLs, patterns, and static data
- **Mapper/Parser**: Transforms raw data into standardized format
- **Provider**: Implements the MetadataProvider interface

## Notification System

The notification system has been modularized into:

- **Schema**: Database table definitions
- **Core Notifications**: Creating and managing notifications
- **Channels**: Email, Discord, Telegram implementations
- **Subscriptions**: Series subscription management
- **Settings**: Notification preferences
- **Releases**: Upcoming release notifications

## Benefits of the New Structure

1. **Improved Maintainability**: Each module has a clear, focused responsibility
2. **Better Organization**: Code is organized by function rather than being in monolithic files
3. **Preserved Compatibility**: All existing imports continue to work through shim files
4. **Reduced Complexity**: Each file is smaller and more focused
5. **Easier Testing**: Smaller modules with clear responsibilities are easier to test
6. **Enhanced Extensibility**: The new structure makes it easier to add new features

## Best Practices for Development

1. **Add new code to the appropriate package**: When adding new functionality, place it in the relevant package
2. **Update the `__init__.py` exports**: Make sure to export any new public functions
3. **Update the compatibility shim**: Add new exports to the compatibility shim
4. **Follow the established patterns**: Maintain consistency with the existing code structure
5. **Write tests for new modules**: Take advantage of the modular structure for better testing
