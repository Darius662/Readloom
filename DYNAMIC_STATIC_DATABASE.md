# Dynamic Static Database - Auto-Populating System

## Overview

The "static" database is now **dynamic** - it automatically grows as you import manga! No pre-filling needed.

## How It Works

### First Import (New Manga)
```
User imports "Obscure Manga"
  ↓
1. Check database cache → Not found
2. Check dynamic static DB → Not found
3. Scrape web (MangaDex, MangaFire, etc.)
4. MangaDex returns: 45 chapters, 5 volumes
5. Save to database cache ✓
6. Save to dynamic static DB ✓  ← NEW!
7. Save to JSON file ✓           ← NEW!
8. Create 5 volumes
```

### Second Import (Same Manga)
```
User imports "Obscure Manga" again
  ↓
1. Check database cache → Found! (5 volumes)
2. Use cached data
3. Create 5 volumes
Time: <100ms (instant!)
```

### Third Import (After Restart)
```
App restarts, database cache cleared
User imports "Obscure Manga"
  ↓
1. Load dynamic static DB from JSON → Found! (5 volumes)
2. Check dynamic static DB → Found! ✓
3. Use static DB data
4. Save to database cache
5. Create 5 volumes
Time: <100ms (instant!)
```

## File Structure

### JSON File Location
```
backend/features/scrapers/mangainfo/manga_static_db.json
```

### JSON Format
```json
{
  "obscure manga": {
    "chapters": 45,
    "volumes": 5,
    "title": "Obscure Manga"
  },
  "another manga": {
    "chapters": 123,
    "volumes": 12,
    "title": "Another Manga"
  }
}
```

## The Complete System

```
┌─────────────────────────────────────────────────────────────┐
│                    Import Manga Request                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: Database Cache (Session, Fast)                      │
│ • In-memory cache for current session                       │
│ • Cleared on restart                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Tier 2: Database Cache (Persistent, Fast)                   │
│ • manga_volume_cache table                                  │
│ • Persists across restarts                                  │
│ • Auto-refreshes when stale                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Tier 3: Dynamic Static DB (Persistent, Fast) ← NEW!         │
│ • Loaded from manga_static_db.json on startup               │
│ • Includes 27 hardcoded popular manga                       │
│ • Auto-populated when you import manga                      │
│ • Persists across restarts                                  │
│ • Can be shared/exported                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Tier 4: Web Scraping (Comprehensive)                        │
│ • MangaDex API (improved)                                   │
│ • MangaFire scraping                                         │
│ • MangaPark scraping                                         │
│ • Saves to dynamic static DB after success ✓                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Tier 5: Estimation (Last Resort)                            │
│ • chapters ÷ 9 = volumes                                    │
│ • NOT saved to static DB (unreliable)                       │
└─────────────────────────────────────────────────────────────┘
```

## Benefits

### For You
✅ **Zero maintenance** - Database grows automatically
✅ **Fast imports** - Second import is instant
✅ **Persists across restarts** - JSON file survives restarts
✅ **Works for ALL manga** - Not limited to popular titles
✅ **Shareable** - Can export/import the JSON file

### How It Grows
- Import 10 manga → 10 entries in JSON
- Import 100 manga → 100 entries in JSON
- Import 1000 manga → 1000 entries in JSON
- **Your personal manga database!**

## What Gets Saved

### Saved to Dynamic Static DB:
✅ Data from MangaDex API
✅ Data from MangaFire scraping
✅ Data from MangaPark scraping

### NOT Saved:
❌ Estimation data (unreliable)
❌ Fallback data (too conservative)

## Viewing the Database

### Check JSON File
```bash
cat backend/features/scrapers/mangainfo/manga_static_db.json
```

Or open in any text editor.

### Check Statistics
```python
import json
with open('backend/features/scrapers/mangainfo/manga_static_db.json', 'r') as f:
    db = json.load(f)
    print(f"Total manga: {len(db)}")
```

## Exporting/Sharing

### Export Your Database
```bash
# Copy the JSON file
cp backend/features/scrapers/mangainfo/manga_static_db.json my_manga_database.json
```

### Import Someone Else's Database
```bash
# Replace with their database
cp their_manga_database.json backend/features/scrapers/mangainfo/manga_static_db.json
```

### Merge Databases
```python
import json

# Load yours
with open('manga_static_db.json', 'r') as f:
    my_db = json.load(f)

# Load theirs
with open('their_database.json', 'r') as f:
    their_db = json.load(f)

# Merge (yours takes precedence)
merged = {**their_db, **my_db}

# Save merged
with open('manga_static_db.json', 'w') as f:
    json.dump(merged, f, indent=2)
```

## Maintenance

### Backup
```bash
# Backup your database
cp backend/features/scrapers/mangainfo/manga_static_db.json manga_db_backup.json
```

### Clear
```bash
# Start fresh (keeps hardcoded popular manga)
rm backend/features/scrapers/mangainfo/manga_static_db.json
```

### Edit Manually
Open `manga_static_db.json` in any text editor and add/edit entries:
```json
{
  "your manga": {
    "chapters": 123,
    "volumes": 45,
    "title": "Your Manga"
  }
}
```

## Performance

| Scenario | First Import | Second Import | After Restart |
|----------|--------------|---------------|---------------|
| **Popular manga** | <100ms (static) | <100ms (cache) | <100ms (static) |
| **New manga** | 2-5s (scrape) | <100ms (cache) | <100ms (static) |
| **All manga** | Varies | <100ms (cache) | <100ms (static) |

## Example Growth

### Day 1
```json
{
  "dandadan": {"chapters": 211, "volumes": 24, "title": "Dandadan"}
}
```

### Week 1
```json
{
  "dandadan": {"chapters": 211, "volumes": 24, "title": "Dandadan"},
  "obscure manga 1": {"chapters": 45, "volumes": 5, "title": "Obscure Manga 1"},
  "obscure manga 2": {"chapters": 67, "volumes": 7, "title": "Obscure Manga 2"},
  "obscure manga 3": {"chapters": 89, "volumes": 9, "title": "Obscure Manga 3"}
}
```

### Month 1
```json
{
  // 50+ manga entries...
}
```

### Year 1
```json
{
  // 500+ manga entries...
  // Your complete personal manga database!
}
```

## Troubleshooting

### "JSON file not found"
- Normal on first run
- Will be created automatically when you import first manga

### "JSON file corrupted"
- Delete the file
- Restart app
- Will recreate on next import

### "Wrong data in JSON"
- Edit the JSON file manually
- Or delete the entry and re-import

## Summary

The dynamic static database:

✅ **Starts with 27 popular manga** (hardcoded)
✅ **Grows automatically** as you import
✅ **Persists across restarts** (JSON file)
✅ **Fast lookups** (loaded into memory)
✅ **Shareable** (export/import JSON)
✅ **Zero maintenance** (auto-populated)
✅ **Works for ALL manga** (not just popular)

**Your personal manga database that builds itself!** 🎉
