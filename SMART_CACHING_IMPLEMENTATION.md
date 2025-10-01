# Smart Caching Implementation

## Overview

The volume detection system has been upgraded from a **static hardcoded database** to a **smart database caching system**. This provides the best of both worlds: fast performance and automatic updates.

## What Changed

### Before (Static Database)
- Volume counts hardcoded in `constants.py`
- Required manual updates for new manga
- Limited to 27 manga entries
- Always accurate but not scalable

### After (Smart Caching)
- Volume counts stored in database cache
- Automatically scraped and cached on first import
- Works for **any manga**, not just popular ones
- Cache automatically refreshes when stale
- No manual maintenance required

## How It Works

### Three-Tier System

1. **Memory Cache** (fastest)
   - Stores results for the current session
   - Avoids repeated database queries
   - Cleared when application restarts

2. **Database Cache** (fast, persistent)
   - Stores scraped results in `manga_volume_cache` table
   - Persists across restarts
   - Automatically refreshes when stale

3. **Web Scraping** (slowest, most accurate)
   - MangaFire, MangaDex, MangaPark
   - Only runs when cache is empty or stale
   - Results automatically cached

### Cache Freshness

The system automatically determines when cache is stale:

- **Ongoing manga**: Cache for 30 days
- **Completed manga**: Cache for 90 days

When cache is stale, it's automatically refreshed on next access.

### Database Schema

```sql
CREATE TABLE manga_volume_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manga_title TEXT NOT NULL,
    manga_title_normalized TEXT NOT NULL,
    anilist_id TEXT,
    mal_id TEXT,
    chapter_count INTEGER NOT NULL DEFAULT 0,
    volume_count INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL,
    status TEXT,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    refresh_count INTEGER DEFAULT 0,
    UNIQUE(manga_title_normalized)
);
```

## Benefits

### For Users

✅ **No manual maintenance** - Cache builds automatically
✅ **Works for all manga** - Not limited to popular titles
✅ **Always up-to-date** - Stale cache automatically refreshes
✅ **Fast imports** - Cached data loads instantly
✅ **Transparent** - Can see cache source and age

### For Developers

✅ **No hardcoded data** - Everything is dynamic
✅ **Scalable** - Handles unlimited manga
✅ **Maintainable** - No manual database updates
✅ **Flexible** - Easy to adjust cache duration
✅ **Debuggable** - Full logging and cache inspection

## Usage

### Normal Import (Automatic Caching)

```python
# First import - scrapes and caches
details = anilist.get_manga_details(manga_id)
# Result: Scraped from web, cached in database

# Second import (same manga) - uses cache
details = anilist.get_manga_details(manga_id)
# Result: Loaded from cache (instant)

# After 30+ days - automatically refreshes
details = anilist.get_manga_details(manga_id)
# Result: Cache stale, re-scrapes and updates cache
```

### Force Refresh

```python
# Bypass cache and scrape fresh data
chapters, volumes = provider.get_chapter_count(
    manga_title="Dandadan",
    anilist_id="132029",
    status="ONGOING",
    force_refresh=True  # <-- Force refresh
)
```

### Check Cache

```python
from backend.internals.db import execute_query

# Get all cached manga
cached = execute_query(
    "SELECT manga_title, volume_count, source, refreshed_at FROM manga_volume_cache"
)

for entry in cached:
    print(f"{entry['manga_title']}: {entry['volume_count']} volumes")
```

## Migration

### Automatic Migration

The system includes a database migration (`0008_add_manga_volume_cache.py`) that:
- Creates the `manga_volume_cache` table
- Creates indexes for performance
- Runs automatically on application start

### No Data Loss

- Existing series are not affected
- Cache builds gradually as manga are imported
- Old static database data is not migrated (not needed)

## Files Modified

### 1. New Migration
- `backend/migrations/0008_add_manga_volume_cache.py`
  - Creates cache table and indexes

### 2. Updated Provider
- `backend/features/scrapers/mangainfo/provider.py`
  - Removed static database dependency
  - Added database caching logic
  - Added cache freshness checks
  - Added automatic refresh
  - Added force_refresh option

### 3. Updated AniList Provider
- `backend/features/metadata_providers/anilist/provider.py`
  - Passes `anilist_id` and `status` to scraper
  - Better cache matching
  - Improved logging

## Testing

### Test Script

Run the test script to verify the system works:

```bash
python test_smart_caching.py
```

This will:
1. Run migrations to create the cache table
2. Import several manga
3. Verify they're cached in the database
4. Show cache statistics

### Manual Testing

1. **Import a new manga** - Should scrape and cache
2. **Import the same manga again** - Should use cache (instant)
3. **Check the cache table** - Should see the entry
4. **Wait 30+ days** - Cache should refresh automatically

## Cache Management

### View Cache

```sql
SELECT * FROM manga_volume_cache ORDER BY refreshed_at DESC;
```

### Clear Cache

```sql
DELETE FROM manga_volume_cache;
```

### Clear Specific Entry

```sql
DELETE FROM manga_volume_cache WHERE manga_title_normalized = 'dandadan';
```

### Update Cache Manually

```sql
UPDATE manga_volume_cache 
SET volume_count = 24, chapter_count = 211 
WHERE manga_title_normalized = 'dandadan';
```

## Performance

### First Import (No Cache)
- Time: 2-5 seconds (web scraping)
- Database: 1 write (cache entry)

### Subsequent Imports (Cached)
- Time: <100ms (database read)
- Database: 1 read (cache lookup)

### Cache Refresh (Stale)
- Time: 2-5 seconds (web scraping)
- Database: 1 update (cache refresh)

## Configuration

### Cache Duration

Edit `provider.py` to adjust cache duration:

```python
def _is_cache_fresh(self, cache_entry: Dict) -> bool:
    status = cache_entry.get('status', '').upper()
    if status == 'COMPLETED' or status == 'FINISHED':
        return age_days < 90  # <-- Adjust this
    else:
        return age_days < 30  # <-- Adjust this
```

### Scraping Sources

The system tries multiple sources in parallel:
1. MangaFire
2. MangaDex API
3. MangaPark
4. Estimation (fallback)

The source with the highest chapter count is used.

## Troubleshooting

### "Cache not working"

Check if migration ran:
```sql
SELECT * FROM migrations WHERE migration_file = '0008_add_manga_volume_cache.py';
```

If not found, run migrations manually:
```bash
python -c "from backend.internals.migrations import run_migrations; run_migrations()"
```

### "Wrong volume count cached"

Force refresh to re-scrape:
```python
provider.get_chapter_count(manga_title, force_refresh=True)
```

Or delete the cache entry:
```sql
DELETE FROM manga_volume_cache WHERE manga_title_normalized = 'title';
```

### "Cache never refreshes"

Check the `refreshed_at` timestamp:
```sql
SELECT manga_title, refreshed_at, 
       julianday('now') - julianday(refreshed_at) as age_days
FROM manga_volume_cache;
```

## Future Enhancements

### Possible Improvements

1. **Background refresh job**
   - Automatically refresh stale cache in background
   - No delay on user imports

2. **Manual refresh UI**
   - Button to refresh specific manga
   - Bulk refresh option

3. **Cache statistics**
   - Show cache hit rate
   - Show most cached manga
   - Show cache age distribution

4. **Smart refresh**
   - Refresh ongoing manga more frequently
   - Skip refresh for completed manga

5. **Cache sharing**
   - Export/import cache between instances
   - Community-shared cache database

## Comparison with Static Database

| Feature | Static Database | Smart Caching |
|---------|----------------|---------------|
| **Maintenance** | Manual updates required | Automatic |
| **Coverage** | 27 manga | Unlimited |
| **Accuracy** | Always accurate | Accurate + auto-refresh |
| **Speed** | Instant | Instant (after first import) |
| **Scalability** | Limited | Unlimited |
| **Updates** | Manual code changes | Automatic scraping |
| **Storage** | Code file | Database |
| **Flexibility** | Fixed | Dynamic |

## Summary

The smart caching system provides:

✅ **Zero maintenance** - No manual updates needed
✅ **Universal coverage** - Works for any manga
✅ **Automatic updates** - Stale cache refreshes automatically
✅ **Fast performance** - Cached results load instantly
✅ **Transparent operation** - Full logging and inspection
✅ **Flexible configuration** - Easy to adjust cache duration
✅ **Backward compatible** - No breaking changes

The static database has been completely replaced with a dynamic, self-maintaining caching system that scales to handle any number of manga without manual intervention.
