# Metadata Providers

This document describes the behavior and implementation details of MangaArr's metadata providers.

## Overview

MangaArr supports multiple metadata providers for fetching manga information, including:
- AniList (primary recommended provider)
- MyAnimeList (via Jikan API)
- MangaDex
- Manga-API

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
   - Use AniList as the primary provider (most comprehensive data)
   - Use MangaDex for additional chapter information
   - Use MyAnimeList for supplementary metadata

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
