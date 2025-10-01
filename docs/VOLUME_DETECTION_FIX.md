# Volume Detection Bug Fix

> **Note**: This document describes the initial fix. For the complete, updated solution including alias support and expanded database, see [VOLUME_FIX_FINAL_SUMMARY.md](../VOLUME_FIX_FINAL_SUMMARY.md) in the root directory.

## Problem Description

The application was showing incorrect volume counts for many manga series when importing from AniList. For example:
- **One Punch Man**: Showed only 4 volumes instead of 29
- **Shangri-La Frontier**: Showed only 4 volumes instead of 17
- **Attack on Titan / Shingeki no Kyojin**: Showed only 7 volumes instead of 34
- **Dandadan**: Showed only 11 volumes instead of 24
- **Berserk**: Worked correctly (41 volumes)

## Root Cause Analysis

The bug was caused by **three related issues** in the import process:

### Issue 1: Duplicate Dictionary Key in AniList Provider

**File**: `backend/features/metadata_providers/anilist/provider.py`

In the `get_manga_details()` method (lines 328-347), there was a duplicate key `"volumes"` in the returned dictionary:

```python
return {
    # ... other fields ...
    "volumes": item.get("volumes", 0),      # Line 338 - Volume COUNT from API
    # ... other fields ...
    "volumes": volumes_list,                 # Line 346 - Volume LIST (overwrites count!)
}
```

**Impact**: The second `"volumes"` key overwrote the first one. This meant:
- If AniList API returned a low volume count (or 0), a small `volumes_list` was created
- The accurate volume count from MangaFire scraper was never used during import

### Issue 2: Volume Creation Timing

**File**: `backend/features/metadata_service/facade.py`

In the `import_manga_to_collection()` function (lines 372-444), volumes were created BEFORE the MangaFire scraper was consulted:

1. The function called `get_chapter_list()` which triggers the scraper
2. The scraper gets accurate volume counts (e.g., 29 for One Punch Man)
3. BUT this data was only used for chapter generation, NOT for creating volume records
4. Volume creation used either:
   - The `volumes_list` from manga_details (which was based on low AniList API data)
   - A default of 4 volumes

**Impact**: Even though the scraper found the correct volume count, it wasn't used to create the actual volume records in the database.

### Issue 3: Missing Aliases and Incomplete Static Database

**File**: `backend/features/scrapers/mangainfo/constants.py` and `provider.py`

The static database and matching logic had limitations:

1. **No alias support**: Japanese titles like "Shingeki no Kyojin" didn't match "Attack on Titan"
2. **Incomplete database**: Popular manga like "Dandadan" and "Shangri-La Frontier" were missing
3. **Simple matching**: Only checked if one string contained the other

**Impact**: Many manga fell back to web scraping or estimation, which often failed or returned incorrect data.

## The Fix

### Fix 1: Rename Duplicate Key

Changed the duplicate `"volumes"` key to separate keys:

```python
return {
    # ... other fields ...
    "volume_count": volume_count,    # Volume COUNT (integer)
    # ... other fields ...
    "volumes_list": volumes_list,    # Volume LIST (array of volume objects)
}
```

### Fix 2: Use Scraper Data Before Creating Volumes

Added code to fetch accurate volume count from the scraper BEFORE creating volumes:

```python
# Try to get accurate volume count from scrapers (MangaFire, etc.)
if provider == "AniList":
    try:
        from backend.features.metadata_providers.setup import get_provider
        anilist_provider = get_provider("AniList")
        if anilist_provider and hasattr(anilist_provider, 'info_provider'):
            manga_title = manga_details.get("title", "")
            if manga_title:
                LOGGER.info(f"Getting accurate volume count from scrapers for: {manga_title}")
                accurate_chapters, accurate_volumes = anilist_provider.info_provider.get_chapter_count(manga_title)
                if accurate_volumes > 0:
                    volume_count = accurate_volumes
                    LOGGER.info(f"Using scraped volume count: {volume_count} volumes")
    except Exception as e:
        LOGGER.warning(f"Could not get accurate volume count from scrapers: {e}")
```

Also updated the check to use `volumes_list` instead of `volumes`:

```python
if "volumes_list" in manga_details and isinstance(manga_details["volumes_list"], list):
    # Create volumes from provider data
```

### Fix 3: Add Alias Support and Expand Database

Added alias support to the static database:

```python
POPULAR_MANGA_DATA = {
    "attack on titan": {
        "chapters": 139, 
        "volumes": 34, 
        "aliases": ["shingeki no kyojin"]
    },
    "dandadan": {"chapters": 211, "volumes": 24},
    "shangri-la frontier": {
        "chapters": 100, 
        "volumes": 17, 
        "aliases": ["shangri-la frontier kusoge hunter"]
    },
    # ... more entries
}
```

Enhanced matching logic to check aliases:

```python
# Check main title
if known_title in manga_title_lower or manga_title_lower in known_title:
    return result

# Check aliases if they exist
if 'aliases' in data:
    for alias in data['aliases']:
        if alias_lower in manga_title_lower or manga_title_lower in alias_lower:
            return result
```

## How the Scraper Works

The MangaFire scraper (`backend/features/scrapers/mangainfo/mangafire.py`) uses multiple strategies:

1. **Static Database**: Checks a hardcoded list of popular manga with known volume counts
2. **MangaFire Scraping**: Scrapes mangafire.to for volume information
3. **MangaDex API**: Queries MangaDex for volume data
4. **MangaPark Scraping**: Scrapes mangapark.net as fallback
5. **Estimation**: Estimates based on chapter count (chapters ÷ 9)

For "One Punch Man", the static database has the correct value:
```python
"one punch man": {"chapters": 200, "volumes": 29}
```

## Testing

To verify the fix works:

1. **Test the scraper directly**:
   ```bash
   python "fix and test/test_one_punch_man_volumes.py"
   ```

2. **Import a new series** from AniList and check volume count

3. **For existing series**, you can refresh volumes using:
   ```bash
   python "fix and test/refresh_all_volumes.py"
   ```

## Expected Results

After the fix:
- **One Punch Man**: Should show 29 volumes ✓
- **Berserk**: Should continue to show 41 volumes ✓
- **Attack on Titan / Shingeki no Kyojin**: Should show 34 volumes ✓
- **Shangri-La Frontier**: Should show 17 volumes ✓
- **Dandadan**: Should show 24 volumes ✓
- **Other popular manga**: Should show accurate volume counts from the scraper or static database

## Files Modified

1. `backend/features/metadata_providers/anilist/provider.py`
   - Fixed duplicate "volumes" key (renamed to "volume_count" and "volumes")
   - Added scraper call in `get_manga_details()` method
   - Updated `get_chapter_list()` to use "volume_count"

2. `backend/features/scrapers/mangainfo/constants.py`
   - Added aliases for popular manga with Japanese titles
   - Expanded database from 25 to 27 entries
   - Added Dandadan, Shangri-La Frontier, and other missing manga

3. `backend/features/scrapers/mangainfo/provider.py`
   - Enhanced matching logic to check aliases
   - Improved logging to show which title/alias matched

## Additional Notes

- The fix only applies to **new imports**. Existing series in the database will still have the old volume counts.
- To fix existing series, use `refresh_series_volumes.py` in the root directory.
- The scraper has a cache, so repeated requests for the same manga will be faster.
- If the scraper fails, the system falls back to estimation based on chapter count.

## Adding More Manga

To add manga to the static database:

1. Use the helper script: `python add_manga_to_database.py`
2. Or manually edit `backend/features/scrapers/mangainfo/constants.py`
3. See [ADDING_MANGA_TO_DATABASE.md](../ADDING_MANGA_TO_DATABASE.md) for detailed instructions

## Complete Documentation

For the complete, updated solution including all fixes and tools:
- [VOLUME_FIX_FINAL_SUMMARY.md](../VOLUME_FIX_FINAL_SUMMARY.md) - Complete overview
- [ADDING_MANGA_TO_DATABASE.md](../ADDING_MANGA_TO_DATABASE.md) - Guide for adding manga
- [VOLUME_FIX_UPDATE.md](../VOLUME_FIX_UPDATE.md) - Alias support details
