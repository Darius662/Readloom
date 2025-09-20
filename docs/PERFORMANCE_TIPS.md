# Performance Tips for MangaArr

This document provides tips and information about performance optimizations in MangaArr, helping you get the best experience even with large manga collections.

## Calendar Performance

### Series-Specific Calendar Updates (v0.0.5+)

Starting with version 0.0.5, MangaArr optimizes calendar updates by only processing the specific manga you're adding or modifying, instead of scanning your entire collection every time.

**Benefits:**
- Much faster manga imports
- Less resource usage
- Better scalability with large collections
- Reduced database load

**How it works:**
- When you add a new manga, only that series' calendar events are processed
- When you update a manga, only its events are refreshed
- Bulk operations still available through utility scripts when needed

**Example:**
- Adding 1 manga to a collection with 100 existing series:
  - Before: All 101 series would be processed for calendar events
  - After: Only the 1 new series is processed, approximately 100x faster

### When to Refresh the Full Calendar

While individual manga operations are optimized, sometimes you may want to refresh the entire calendar:

1. After updating to a new version of MangaArr
2. If you notice missing calendar events
3. When changing global settings that affect the calendar

Use the following methods for a full calendar refresh:

**Option 1: Through the API**
```
POST /api/calendar/refresh
```

**Option 2: Run the bulk update script**
```bash
python "fix and test/refresh_all_volumes.py"
```

## Volume Detection System

MangaArr now uses multiple approaches to ensure accurate volume data:

1. **Multi-source scraping**: Data is collected from multiple sources (MangaFire, MangaDex, etc.)
2. **Static database**: Well-known series have correct volume counts built-in
3. **Fallback estimation**: When external data is unavailable, intelligent estimation is used
4. **Auto-correction**: The `update_manga_volumes.py` script can fix incorrect volume counts

If you notice a manga with missing or incorrect volumes, you can manually set the correct volume count:

```bash
python "fix and test/update_manga_volumes.py" "Manga Title" 15
```

## Database Optimization

For large collections, consider these database optimization tips:

1. **Regular maintenance**: Use the SQLite VACUUM command periodically to optimize the database:
   ```
   VACUUM;
   ```

2. **Index usage**: The application automatically uses indexes for common queries, but avoid manual schema changes

3. **Storage location**: For best performance, store the database on an SSD rather than HDD

## Metadata Caching

MangaArr caches metadata to avoid repeated API calls:

1. The default cache duration is 7 days
2. You can adjust this in Settings → Advanced → `metadata_cache_days`
3. Clear the cache via API when needed: `DELETE /api/metadata/cache`

## Memory Usage Considerations

For systems with limited memory:

1. Set a reasonable calendar range (7-14 days is recommended)
2. Use series-specific updates rather than full refreshes
3. Avoid importing many manga series simultaneously

## Advanced Settings

Fine-tune your performance with these settings:

- `calendar_range_days`: Defines the default view range for the calendar
- `calendar_refresh_hours`: Controls how often the calendar is automatically refreshed
- `task_interval_minutes`: Adjusts background task frequency

Access these settings through:
- API: `GET /api/settings`
- Settings page in the web UI

## Utility Scripts

These scripts help with performance management and testing (located in the `fix and test` directory):

### Volume Management
1. `refresh_all_volumes.py`: Update all manga volumes in a batch operation
2. `update_manga_volumes.py`: Update volumes for a specific manga
3. `fix_manga_volumes.py`: Fix volumes for known manga series

### Testing Tools
4. `test_volume_scraper.py`: Test the volume scraping functionality
5. `test_mangafire.py`: Test MangaFire integration
6. `test_import.py`: Test manga import functionality

### Diagnostic Tools
7. `check_calendar_volumes.py`: Check volume counts in calendar
8. `check_series_volumes.py`: Check volumes for specific series
9. `check_anilist_volume_data.py`: Verify AniList volume data
10. `debug_anilist_chapters.py`: Debug AniList chapter information

### Content Management
11. `add_chapter.py`: Add test chapters to series
12. `add_releases.py`: Add test volume releases
13. `add_series_and_volumes.py`: Create test series with volumes
14. `create_fallback_image.py`: Generate placeholder cover images

Use these when necessary, rather than re-adding manga to your collection.
