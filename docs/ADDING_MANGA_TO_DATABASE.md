# Adding Manga to the Static Database

## Why Add Manga to the Database?

The volume detection system uses multiple methods to find accurate volume counts:

1. **Static Database** (fastest, most reliable) - Hardcoded data for popular manga
2. **Web Scraping** (slower, may fail) - Scrapes MangaFire, MangaDex, MangaPark
3. **Estimation** (least accurate) - Estimates based on chapter count (chapters ÷ 9)

When web scraping fails or returns incorrect data, the static database ensures accurate results.

## When to Add Manga

Add manga to the static database when:

- ✅ The volume count is incorrect after import
- ✅ Web scraping fails for a specific title
- ✅ You want guaranteed accurate data for your favorite manga
- ✅ The manga is popular and will be imported by many users

## How to Add Manga

### Method 1: Using the Helper Script (Easiest)

1. Run the helper script:
   ```bash
   python add_manga_to_database.py
   ```

2. Follow the prompts:
   ```
   Enter manga title (lowercase, e.g., 'dandadan'): dandadan
   Enter total chapters: 211
   Enter total volumes: 24
   Enter alternative titles/aliases (optional):
     Alias 1 (or press Enter to skip): 
   ```

3. The script will generate the entry for you:
   ```python
   "dandadan": {"chapters": 211, "volumes": 24}
   ```

4. Copy the entry and add it to the file (see Method 2 for details)

### Method 2: Manual Edit

1. **Find accurate data** for your manga:
   - Check official sources (publisher websites, Wikipedia, MyAnimeList)
   - Use reliable manga databases
   - Count volumes on official manga sites

2. **Open the constants file**:
   ```
   backend/features/scrapers/mangainfo/constants.py
   ```

3. **Find the POPULAR_MANGA_DATA dictionary** (around line 23)

4. **Add your entry**:
   ```python
   POPULAR_MANGA_DATA = {
       "one piece": {"chapters": 1112, "volumes": 108},
       "naruto": {"chapters": 700, "volumes": 72},
       # ... other entries ...
       "your manga": {"chapters": 123, "volumes": 45},  # <-- Add here
   }
   ```

5. **Save the file**

6. **Restart your application** or refresh the series

### Entry Format

#### Basic Entry
```python
"manga title": {"chapters": 123, "volumes": 45}
```

#### Entry with Aliases
```python
"manga title": {"chapters": 123, "volumes": 45, "aliases": ["alternative title", "japanese title"]}
```

## Important Rules

### Title Format
- ✅ Use **lowercase** for the main title
- ✅ Use the **most common English title**
- ✅ Keep it **simple** (avoid subtitles if possible)

Examples:
- ✅ `"attack on titan"` (good)
- ❌ `"Attack on Titan"` (wrong - not lowercase)
- ❌ `"attack on titan: final season"` (wrong - too specific)

### Aliases
- Use aliases for:
  - **Japanese titles**: `"shingeki no kyojin"` for `"attack on titan"`
  - **Alternative spellings**: `"haikyuu"` for `"haikyu"`
  - **Shortened versions**: `"spy family"` for `"spy x family"`
  - **Full titles with subtitles**: `"shangri-la frontier kusoge hunter"` for `"shangri-la frontier"`

### Data Accuracy
- Use **current, accurate data** (not outdated)
- For **ongoing manga**, update the entry when new volumes are released
- Include **all published volumes**, not just translated ones

## Examples

### Example 1: Simple Entry
```python
"dandadan": {"chapters": 211, "volumes": 24}
```

### Example 2: Entry with Japanese Alias
```python
"attack on titan": {"chapters": 139, "volumes": 34, "aliases": ["shingeki no kyojin"]}
```

### Example 3: Entry with Multiple Aliases
```python
"my hero academia": {"chapters": 430, "volumes": 40, "aliases": ["boku no hero academia", "mha"]}
```

### Example 4: Entry with Subtitle Alias
```python
"shangri-la frontier": {"chapters": 100, "volumes": 17, "aliases": ["shangri-la frontier kusoge hunter"]}
```

## After Adding

### For New Imports
- New imports will automatically use the updated database
- No additional steps needed

### For Existing Series
Use the refresh script to update existing series:

```bash
# Refresh a specific series
python refresh_series_volumes.py --name "Dandadan"

# Refresh all series
python refresh_series_volumes.py --all
```

## Finding Accurate Data

### Recommended Sources

1. **Official Publisher Sites**
   - Most accurate and up-to-date
   - Check the manga's official website

2. **MyAnimeList (MAL)**
   - Usually accurate for volume counts
   - https://myanimelist.net

3. **AniList**
   - Good for ongoing series
   - https://anilist.co

4. **Wikipedia**
   - Reliable for completed series
   - Often has detailed publication information

5. **MangaDex**
   - Good for chapter and volume information
   - https://mangadex.org

### What to Check
- ✅ **Total published volumes** (not chapters)
- ✅ **Current status** (ongoing vs completed)
- ✅ **Latest volume number**
- ❌ Don't count: special editions, artbooks, guidebooks (unless they're numbered volumes)

## Common Manga to Add

Here are some popular manga you might want to add:

```python
# Ongoing Popular Manga (update these periodically)
"jujutsu kaisen": {"chapters": 257, "volumes": 26},
"my hero academia": {"chapters": 430, "volumes": 40},
"one piece": {"chapters": 1112, "volumes": 108},
"black clover": {"chapters": 368, "volumes": 36},

# Completed Manga
"demon slayer": {"chapters": 205, "volumes": 23, "aliases": ["kimetsu no yaiba"]},
"death note": {"chapters": 108, "volumes": 12},
"fullmetal alchemist": {"chapters": 116, "volumes": 27},
"attack on titan": {"chapters": 139, "volumes": 34, "aliases": ["shingeki no kyojin"]},
```

## Troubleshooting

### "The volume count is still wrong after adding"

1. **Check the title matches**: The title in the database must match what AniList returns
   - Run: `python debug_specific_titles.py` to see what title AniList uses
   - Add that exact title (lowercase) or use an alias

2. **Restart the application**: Changes to the constants file require a restart

3. **Clear the cache**: The scraper caches results
   - Restart the application to clear the cache
   - Or wait a few minutes for the cache to expire

4. **Refresh the series**: Use the refresh script for existing series

### "I don't know the accurate volume count"

1. Check the recommended sources above
2. Look for the latest volume number on official sites
3. If unsure, it's better to leave it out than add incorrect data
4. The web scraping will still attempt to find the data

### "The web scraping works for me, why use the static database?"

- Web scraping can fail due to:
  - Network issues
  - Site structure changes
  - Rate limiting
  - Blocked requests
- The static database is:
  - Faster (no network requests)
  - More reliable (always works)
  - More accurate (manually verified)

## Contributing

If you add manga to your local database, consider contributing back:

1. Fork the repository
2. Add the manga to `constants.py`
3. Test it works correctly
4. Submit a pull request

This helps other users who import the same manga!

## Maintenance

### Updating Existing Entries

For ongoing manga, update the entries periodically:

1. Check for new volumes (monthly or quarterly)
2. Update the chapter and volume counts
3. Restart the application
4. Refresh affected series

### Keeping Track

Consider keeping a list of manga you've added:
- Note the date you added them
- Check for updates periodically
- Update when new volumes are released

## Summary

**Quick Steps:**
1. Run `python add_manga_to_database.py`
2. Enter the manga information
3. Copy the generated entry
4. Add it to `backend/features/scrapers/mangainfo/constants.py`
5. Save and restart
6. Refresh existing series if needed

**Key Points:**
- ✅ Use lowercase titles
- ✅ Add aliases for Japanese titles
- ✅ Use accurate, current data
- ✅ Restart after changes
- ✅ Refresh existing series
