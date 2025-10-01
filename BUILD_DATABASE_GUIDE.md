# Building Your Own Manga Database from MangaFire

## Overview

You can build a comprehensive manga database by scraping MangaFire, which has volume and chapter data for thousands of manga.

## Approach Options

### Option 1: Quick Test (Recommended First)

Test MangaFire's structure to understand the HTML:

```bash
python quick_mangafire_scraper.py
```

Choose option 1 to test the structure. This will:
- Download sample HTML pages
- Show you what elements exist
- Help identify the correct selectors

### Option 2: Full Scrape

Once you understand the structure, run the full scraper:

```bash
python scrape_mangafire_database.py --pages 50 --output manga_database.json
```

Parameters:
- `--pages`: Number of pages to scrape (each page ≈ 24 manga)
- `--output`: Output JSON filename

**Estimated time**: ~2 minutes per page (to be respectful to the server)

### Option 3: Manual Database

If scraping is difficult, manually add popular manga to a JSON file:

```json
{
  "dandadan": {
    "chapters": 211,
    "volumes": 24,
    "title": "Dandadan"
  },
  "one punch man": {
    "chapters": 200,
    "volumes": 29,
    "title": "One Punch-Man"
  }
}
```

## Using the Database

### Method 1: Update constants.py

Convert the JSON to Python dict in `constants.py`:

```python
POPULAR_MANGA_DATA = {
    "dandadan": {"chapters": 211, "volumes": 24},
    "one punch man": {"chapters": 200, "volumes": 29},
    # ... more entries
}
```

### Method 2: Load JSON Dynamically

Update `provider.py` to load from JSON:

```python
import json
from pathlib import Path

# Load database on init
db_file = Path(__file__).parent / 'manga_database.json'
if db_file.exists():
    with open(db_file, 'r', encoding='utf-8') as f:
        POPULAR_MANGA_DATA = json.load(f)
```

## Important Notes

### Be Respectful
- Add delays between requests (1-2 seconds)
- Don't scrape too aggressively
- Consider scraping during off-peak hours
- Cache results to avoid re-scraping

### Legal Considerations
- Scraping may violate terms of service
- Use the data for personal use only
- Don't redistribute scraped data
- Consider using official APIs when available

### Data Quality
- Verify a sample of scraped data
- Some manga may have incomplete data
- Keep the static database as fallback

## Alternative: Use Existing Databases

Instead of scraping, consider using existing databases:

### 1. AniList API
- Official API with good coverage
- Free, no API key needed
- GraphQL interface
- Sometimes missing volume data

### 2. MangaDex API
- Official REST API
- Good coverage
- Free, no API key needed
- We already improved this!

### 3. MyAnimeList (Jikan)
- Unofficial API wrapper
- Good coverage
- Free, no API key needed
- Rate limited

### 4. Community Databases
- Look for existing manga databases on GitHub
- Some projects maintain curated lists
- Can be imported directly

## Recommended Workflow

1. **Start with improved MangaDex API** (already done!)
2. **Add static database for popular manga** (27 entries we have)
3. **Optionally scrape MangaFire** for comprehensive coverage
4. **Use smart caching** to store results

This gives you:
- ✅ Fast lookups (cache)
- ✅ Reliable data (static DB)
- ✅ Comprehensive coverage (MangaDex + scraping)
- ✅ Automatic updates (cache refresh)

## Testing Your Database

After building the database, test it:

```bash
python test_improved_mangadex.py
```

Or import a manga through the UI and check the logs.

## Maintenance

- **Update quarterly** for ongoing manga
- **Add new popular manga** as they release
- **Verify data accuracy** periodically
- **Keep backups** of your database

## Summary

**Quick Start:**
1. Test structure: `python quick_mangafire_scraper.py`
2. Understand HTML selectors
3. Update `scrape_mangafire_database.py` with correct selectors
4. Run full scrape: `python scrape_mangafire_database.py --pages 10`
5. Load JSON in your code or convert to Python dict

**Best Practice:**
- Use MangaDex API (already improved!)
- Keep static database for popular manga
- Optionally scrape for comprehensive coverage
- Let smart caching handle the rest
