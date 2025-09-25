# Metadata Providers

This document describes the behavior and implementation details of Readloom's metadata providers.

## Overview

Readloom supports multiple metadata providers for fetching manga and book information, including:

### Manga/Comics Providers:
- AniList (primary recommended provider for manga, enabled by default)
- MyAnimeList (via Jikan API, disabled by default)
- MangaDex (disabled by default)
- MangaFire (disabled by default)
- Manga-API (disabled by default)

### Book Providers:
- Google Books (primary recommended provider for books, enabled by default)
- Open Library (disabled by default)
- ISBNdb (disabled by default, requires API key)
- WorldCat (disabled by default, requires API key)

Only AniList and Google Books are enabled by default to improve initial performance and reduce unnecessary API calls. Other providers can be enabled in the Settings > Integrations > Metadata Providers section.

## Provider Behavior

### AniList

- **Search**: Returns manga titles with rich metadata
- **Details**: Provides comprehensive manga information including description, status, genres
- **Chapters**: 
  - Uses intelligent publication schedule detection for release dates
  - Chapter count is enhanced with multi-source data
  - Popular manga series get accurate chapter counts from static database
  - Release dates follow realistic publication schedules based on manga type
  - Marks past chapters as confirmed historical data
  - Marks future predicted chapters as unconfirmed

### MyAnimeList (Jikan)

- **Search**: Returns manga titles with basic metadata
- **Details**: Provides comprehensive manga information including description, author, status
- **Chapters**: 
  - Limited chapter information due to API limitations
  - Release dates are available for latest chapters
  - Chapter numbers are properly formatted
  - Handles missing chapter numbers by using defaults

### MangaDex

- **Search**: Returns manga titles with detailed metadata
- **Details**: Comprehensive manga information with multiple languages support
- **Chapters**:
  - Full chapter list with release dates
  - May include chapters with null chapter numbers
  - Provides chapter titles in multiple languages
  - Release dates are in ISO format

### MangaFire

- **Search**: Returns manga titles with cover images and basic metadata
- **Details**: Provides manga information including description, status, genres
- **Chapters**:
  - Detailed chapter list with release dates
  - Accurate volume information
  - Chapter numbers are properly formatted
  - Release dates follow actual publication schedules

### Google Books

- **Search**: Returns book titles with rich metadata and accurate information
- **Details**: Provides comprehensive book information including description, authors, publisher
- **Features**:
  - High-quality cover images
  - Accurate publication dates
  - ISBN information
  - Categories and subject information
  - Works without API key, but key recommended for higher rate limits

### Open Library

- **Search**: Returns book titles from a free, open database
- **Details**: Provides book information including description, authors, publication info
- **Features**:
  - No API key required
  - Extensive catalog including older books
  - Cover images for many books
  - Publication information and ISBNs

### ISBNdb

- **Search**: Specialized search by ISBN or book title
- **Details**: Detailed book information with focus on publication data
- **Features**:
  - Comprehensive ISBN database
  - Detailed physical attributes (dimensions, page counts)
  - Publisher information
  - Requires API key

### WorldCat

- **Search**: Global library catalog search
- **Details**: Bibliographic information from libraries worldwide
- **Features**:
  - Over 2 billion items from libraries around the world
  - Academic and scholarly works well represented
  - Library holdings information
  - Multiple language support
  - Requires API key

## Release Date Handling

The calendar system has been enhanced to handle release dates from all providers:

1. **Date Format**: All dates are stored in ISO format (YYYY-MM-DD)
2. **Missing Dates**: Empty dates are allowed and skipped during calendar updates
3. **Historical Dates**: All historical release dates are preserved and marked as confirmed
4. **Future Dates**: Only shows upcoming releases in the next 7 days by default
5. **Confirmation Status**: Tracks whether dates are confirmed or just predicted
6. **Publication Patterns**: Uses intelligent detection of publication schedules:
   - Weekly Shonen Jump titles release on Mondays
   - Monthly seinen magazines release on Thursdays
   - Korean manhwa release on Wednesdays

## Error Handling

1. **Null Chapter Numbers**: Automatically converted to "0" to satisfy database constraints
2. **Invalid Dates**: Skipped during import and calendar updates
3. **Missing Data**: Default values provided for required fields
4. **API Errors**: Cached data used when available, errors logged for debugging

## Cache System

1. **Cache Types**:
   - `manga_details`: Basic manga information
   - `chapters`: Chapter lists and release dates
   - `chapter_images`: Chapter page images

2. **Cache Duration**: Default 7 days, configurable via settings

3. **Cache Invalidation**:
   - Automatic refresh on import
   - Manual refresh via API endpoint
   - Expired items removed during cleanup

## Best Practices

1. **Provider Selection**:
   - For manga/comics:
     - Use AniList as the primary provider (most comprehensive data, enabled by default)
     - Only enable additional providers as needed:
       - MangaDex for additional chapter information
       - MangaFire for accurate volume information
       - MyAnimeList for supplementary metadata
   - For books:
     - Use Google Books as the primary provider (most accurate data, enabled by default)
     - Consider enabling additional providers for specific use cases:
       - Open Library for older or public domain books
       - ISBNdb for detailed publication data (requires API key)
       - WorldCat for academic or library holdings information (requires API key)
   - Keep unused providers disabled to improve performance

2. **Release Date Management**:
   - Always include release dates when available
   - Use ISO format for consistency
   - Preserve historical dates with confirmation status
   - Follow realistic publication schedules for future dates

3. **Error Prevention**:
   - Validate chapter numbers before import
   - Check date formats
   - Handle null values gracefully
   - Use caching to prevent API overload

## Package Structure

Each metadata provider has been refactored into its own package with the following structure:

```
metadata_providers/
├── base.py              # Base provider classes
├── setup.py             # Provider registration and configuration
├── anilist/             # AniList provider (manga)
│   ├── __init__.py
│   └── provider.py
├── mangadex/            # MangaDex provider (manga)
│   ├── __init__.py
│   └── provider.py
├── googlebooks/         # Google Books provider (books)
│   ├── __init__.py
│   └── provider.py
├── openlibrary/         # Open Library provider (books)
│   ├── __init__.py
│   └── provider.py
├── isbndb/              # ISBNdb provider (books)
│   ├── __init__.py
│   └── provider.py
└── worldcat/            # WorldCat provider (books)
    ├── __init__.py
    └── provider.py
```

This modular structure improves maintainability and makes it easier to add new providers.

## Future Improvements

1. **Provider Enhancements**:
   - Add more metadata providers for both manga and books
   - Improve release date accuracy for all content types
   - Enhance chapter information retrieval for manga
   - Add support for audiobook metadata
   - Implement better ISBN lookup and validation

2. **Cache Optimization**:
   - Smart cache invalidation
   - Partial cache updates
   - Cache compression

3. **Data Quality**:
   - Better handling of conflicting data
   - Enhanced validation
   - Improved error reporting
