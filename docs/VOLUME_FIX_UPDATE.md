# Volume Detection Fix - Update

## Additional Fix for Japanese/Alternative Titles

### Problem
After the initial fix, some titles were still showing incorrect volume counts:
- **Shangri-La Frontier**: Showed 4 volumes instead of 17
- **Attack on Titan / Shingeki no Kyojin**: Showed 7 volumes instead of 34

### Root Cause
The static database matching logic was too simple. It only checked if the title contained the search key, but didn't handle:
1. **Japanese titles**: "Shingeki no Kyojin" didn't match "attack on titan"
2. **Long titles with subtitles**: "Shangri-La Frontier: Kusoge Hunter, Kami ge ni Idoman to su" didn't match well

### The Fix

#### 1. Added Aliases to Static Database

Updated `backend/features/scrapers/mangainfo/constants.py` to support alternative titles:

```python
POPULAR_MANGA_DATA = {
    "attack on titan": {
        "chapters": 139, 
        "volumes": 34, 
        "aliases": ["shingeki no kyojin"]
    },
    "demon slayer": {
        "chapters": 205, 
        "volumes": 23, 
        "aliases": ["kimetsu no yaiba"]
    },
    "my hero academia": {
        "chapters": 430, 
        "volumes": 40, 
        "aliases": ["boku no hero academia"]
    },
    "shangri-la frontier": {
        "chapters": 100, 
        "volumes": 17, 
        "aliases": ["shangri-la frontier kusoge hunter"]
    },
    # ... and more
}
```

#### 2. Enhanced Matching Logic

Updated `backend/features/scrapers/mangainfo/provider.py` to check aliases:

```python
# Look for matching popular manga in our static database
for known_title, data in POPULAR_MANGA_DATA.items():
    # Check main title
    if known_title in manga_title_lower or manga_title_lower in known_title:
        result = (data['chapters'], data['volumes'])
        LOGGER.info(f"Using static data for {manga_title}: {result[0]} chapters, {result[1]} volumes (matched: {known_title})")
        self.cache[manga_title] = result
        return result
    
    # Check aliases if they exist
    if 'aliases' in data:
        for alias in data['aliases']:
            alias_lower = alias.lower()
            if alias_lower in manga_title_lower or manga_title_lower in alias_lower:
                result = (data['chapters'], data['volumes'])
                LOGGER.info(f"Using static data for {manga_title}: {result[0]} chapters, {result[1]} volumes (matched alias: {alias})")
                self.cache[manga_title] = result
                return result
```

### Test Results

All problematic titles now work correctly:

| Title | Search Term | Expected | Actual | Status |
|-------|-------------|----------|--------|--------|
| Shangri-La Frontier | "Shangri-La Frontier" | 17 | 17 | ✓ |
| Attack on Titan | "Attack on Titan" | 34 | 34 | ✓ |
| Attack on Titan | "Shingeki no Kyojin" | 34 | 34 | ✓ |

### Files Modified

1. **`backend/features/scrapers/mangainfo/constants.py`**
   - Added `aliases` field to manga entries
   - Added "Shangri-La Frontier" to the database
   - Added aliases for popular manga with Japanese titles

2. **`backend/features/scrapers/mangainfo/provider.py`**
   - Enhanced matching logic to check aliases
   - Added logging to show which title/alias matched

### Adding More Titles

To add more manga to the static database:

1. Open `backend/features/scrapers/mangainfo/constants.py`
2. Add an entry in `POPULAR_MANGA_DATA`:

```python
"your manga title": {
    "chapters": 123,
    "volumes": 45,
    "aliases": ["alternative title", "japanese title"]  # Optional
}
```

3. Use lowercase for both the main title and aliases
4. The matching is flexible - it checks if the search term contains the title or vice versa

### Common Aliases to Add

Here are some common patterns for aliases:
- **Japanese titles**: "shingeki no kyojin" for "attack on titan"
- **Romanization variants**: "haikyuu" for "haikyu"
- **Shortened titles**: "spy family" for "spy x family"
- **Full titles**: "shangri-la frontier kusoge hunter" for "shangri-la frontier"
- **Alternative spellings**: "dr. stone" for "dr stone"

### Verification

To verify a title works correctly:

```bash
python test_problematic_titles.py
```

Or test a specific title:

```python
from backend.features.scrapers.mangainfo.provider import MangaInfoProvider

provider = MangaInfoProvider()
chapters, volumes = provider.get_chapter_count("Your Manga Title")
print(f"Chapters: {chapters}, Volumes: {volumes}")
```

### Impact

✅ **Japanese titles now work**: Titles like "Shingeki no Kyojin" correctly match "Attack on Titan"
✅ **Long titles with subtitles work**: Titles with extra text are matched correctly
✅ **Flexible matching**: The system checks both the main title and all aliases
✅ **Easy to extend**: Adding new titles and aliases is simple

### For Existing Series

If you have series that were imported before this fix and still show incorrect volumes:

```bash
# Refresh a specific series
python refresh_series_volumes.py --name "Shangri-La Frontier"

# Or refresh all series
python refresh_series_volumes.py --all
```
