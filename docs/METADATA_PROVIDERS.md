# Metadata Providers

This document describes the behavior and implementation details of MangaArr's metadata providers.

## Overview

MangaArr supports multiple metadata providers for fetching manga information, including:
- MyAnimeList (via Jikan API)
- MangaDex
- Viz Media
- Manga-API (deprecated)

## Provider Behavior

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

### Viz Media

- **Search**: Returns official manga titles published by Viz Media
- **Details**: Basic manga information and cover images from official sources
- **Calendar**:
  - Access to official Viz Media release calendar
  - Accurate release dates for upcoming volumes
  - Includes physical (paperback, hardcover) and digital formats
- **Rate Limiting**:
  - Implements automatic rate limiting to prevent API blocks
  - Uses caching system to minimize requests

## Release Date Handling

The calendar system has been enhanced to handle release dates from all providers:

1. **Date Format**: All dates are stored in ISO format (YYYY-MM-DD)
2. **Missing Dates**: Empty dates are allowed and skipped during calendar updates
3. **Historical Dates**: All historical release dates are preserved
4. **Future Dates**: Upcoming release dates are tracked without restrictions

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
   - Use MyAnimeList for reliable metadata
   - Use MangaDex for comprehensive chapter information
   - Use Viz Media for official release dates and calendar information
   - Avoid deprecated providers (Manga-API)

2. **Release Date Management**:
   - Always include release dates when available
   - Use ISO format for consistency
   - Preserve historical dates
   - Allow future dates without restrictions

3. **Error Prevention**:
   - Validate chapter numbers before import
   - Check date formats
   - Handle null values gracefully
   - Use caching to prevent API overload

## Future Improvements

1. **Provider Enhancements**:
   - Add more metadata providers
   - Improve release date accuracy
   - Enhance chapter information retrieval

2. **Cache Optimization**:
   - Smart cache invalidation
   - Partial cache updates
   - Cache compression

3. **Data Quality**:
   - Better handling of conflicting data
   - Enhanced validation
   - Improved error reporting
