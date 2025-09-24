# AniList Provider

This document describes the AniList provider implementation in Readloom, including its features, limitations, and best practices.

## Overview

The AniList provider leverages AniList's GraphQL API to fetch comprehensive manga metadata. It is enhanced with additional systems to compensate for limitations in AniList's API, particularly related to chapter counts and release dates.

## Features

### Manga Information

- **Title**: Original, romanized, and English titles
- **Description**: Full synopsis with HTML handling
- **Cover Images**: High-quality cover art images
- **Metadata**: Genres, status, start/end dates, ratings
- **Authors**: Author and artist information
- **Related Manga**: Connected series information
- **Recommendations**: Similar manga suggestions

### Chapter and Volume Management

- **Multi-Source Chapter Counting**: Uses multiple data sources to get accurate chapter counts
  - Static database for popular manga (One Piece, Naruto, etc.)
  - Web scraping for less common series
  - MangaDex API integration for additional verification
  - Smart estimation for unknown series

- **Enhanced Volume Detection** (v0.0.5+):
  - Advanced web scraping from multiple sources (MangaFire, MangaPark, MangaDex)
  - Pattern-based detection in chapter titles and descriptions
  - Static database for known series' volume counts
  - Fallback estimation based on chapter count
  - Automatic volume generation when external data is unavailable

- **Intelligent Release Date Generation**:
  - Different manga types follow their actual publication schedules
  - Weekly Shonen Jump titles release on Mondays
  - Monthly seinen magazines release on Thursdays
  - Korean manhwa release on Wednesdays
  - Default releases are bi-weekly on Mondays

- **Confirmation Status Tracking**:
  - Past chapters marked as confirmed historical data
  - Future predicted chapters marked as unconfirmed
  - Sonarr/Radarr-like calendar shows only upcoming releases in the next 7 days

## Technical Implementation

### GraphQL API

The AniList provider uses GraphQL queries to fetch data efficiently:

```graphql
query ($search: String) {
  Page(perPage: 10) {
    media(type: MANGA, search: $search, sort: POPULARITY_DESC) {
      id
      title {
        romaji
        english
        native
      }
      # Additional fields...
    }
  }
}
```

### Publication Schedule Detection

The provider analyzes manga metadata to determine likely publication schedules:

```python
def _determine_publication_schedule(self, manga_details):
    # Get relevant metadata
    title = manga_details.get("title", "").lower()
    genres = manga_details.get("genres", [])
    status = manga_details.get("status", "")
    
    # Check for Weekly Shonen Jump series
    if "one piece" in title or "my hero academia" in title:
        return (0, timedelta(days=7))  # Monday, Weekly
    
    # Check for monthly seinen magazines
    if "berserk" in title or "seinen" in genres:
        return (3, timedelta(days=30))  # Thursday, Monthly
    
    # Additional rules...
```

### Chapter Count Enhancement

For popular manga, accurate chapter counts are provided from a curated database:

```python
popular_manga_data = {
    "one piece": {"chapters": 1112, "volumes": 108},
    "naruto": {"chapters": 700, "volumes": 72},
    "berserk": {"chapters": 375, "volumes": 41},
    # Additional series...
}
```

## Limitations

- AniList API doesn't provide detailed chapter information
- Chapter titles are generic ("Chapter X") rather than actual titles
- Volume information is limited and often estimated
- Web scraping may be affected by website changes
- Release date predictions are based on patterns, not official announcements

## Best Practices

1. **Use with Other Providers**:
   - AniList for general metadata and release schedules
   - MangaDex for detailed chapter information when available
   - MangaFire for accurate volume counts

2. **Calendar Configuration**:
   - Keep the 7-day upcoming release window for clean calendar display
   - Filter series to focus on actively followed manga
   - Use series-specific calendar updates for better performance

3. **Release Date Expectations**:
   - Understand that future dates are predictions, not official dates
   - Past chapter dates are more reliable as historical records

4. **Volume Management**:
   - Use `fix and test/update_manga_volumes.py` to correct inaccurate volume counts
   - For bulk operations, use `fix and test/refresh_all_volumes.py`
   - Check scraper logs if volume detection isn't working properly

## Troubleshooting

1. **Missing Chapter Counts**:
   - Check if the manga is in the static database
   - Verify if web scraping is enabled
   - Consider adding the manga to the static database

2. **Missing or Incorrect Volumes**:
   - Run `fix and test/update_manga_volumes.py "Manga Title" <correct_volume_count>`
   - Check if the manga title is recognized by the scrapers
   - Try alternative spellings if the manga isn't found
   - Use `fix and test/test_volume_scraper.py` to diagnose issues

3. **Incorrect Release Dates**:
   - Check the publication schedule detection
   - Verify the manga type and publisher
   - Update the schedule detection rules if necessary

4. **Calendar Issues**:
   - Ensure calendar_range_days is set appropriately
   - Check if confirmation mode is enabled/disabled as desired
   - For performance issues, refer to the PERFORMANCE_TIPS.md document
