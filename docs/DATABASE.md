# MangaArr Database Schema

This document describes the database schema used by MangaArr, including tables, relationships, and constraints.

## Overview

MangaArr uses SQLite as its database engine. The database includes foreign key constraints to maintain data integrity and prevent orphaned records.

## Tables

### series

Main table for manga/comic series.

```sql
CREATE TABLE series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    author TEXT,
    publisher TEXT,
    cover_url TEXT,
    status TEXT,
    content_type TEXT DEFAULT 'MANGA',
    metadata_source TEXT,
    metadata_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### volumes

Volumes belonging to series.

```sql
CREATE TABLE volumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    volume_number TEXT NOT NULL,
    title TEXT,
    description TEXT,
    cover_url TEXT,
    release_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE
)
```

### chapters

Chapters belonging to series and optionally to volumes.

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    volume_id INTEGER,
    chapter_number TEXT NOT NULL,
    title TEXT,
    description TEXT,
    release_date TEXT,
    status TEXT,
    read_status TEXT DEFAULT 'UNREAD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE,
    FOREIGN KEY (volume_id) REFERENCES volumes (id) ON DELETE SET NULL
)
```

### calendar_events

Events for the release calendar.

```sql
CREATE TABLE calendar_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER REFERENCES series(id) ON DELETE CASCADE,
    volume_id INTEGER REFERENCES volumes(id) ON DELETE CASCADE,
    chapter_id INTEGER REFERENCES chapters(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    event_date TEXT NOT NULL,
    event_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### ebook_files

E-book files associated with volumes.

```sql
CREATE TABLE ebook_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    volume_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER,
    file_type TEXT,
    original_name TEXT,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE,
    FOREIGN KEY (volume_id) REFERENCES volumes (id) ON DELETE CASCADE
)
```

### collection_items

Items in the user's collection.

```sql
CREATE TABLE collection_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    volume_id INTEGER NULL,
    chapter_id INTEGER NULL,
    item_type TEXT NOT NULL CHECK(item_type IN ('SERIES', 'VOLUME', 'CHAPTER')),
    ownership_status TEXT NOT NULL CHECK(ownership_status IN ('OWNED', 'WANTED', 'ORDERED', 'LOANED', 'NONE')),
    read_status TEXT NOT NULL CHECK(read_status IN ('READ', 'READING', 'UNREAD', 'NONE')),
    format TEXT CHECK(format IN ('PHYSICAL', 'DIGITAL', 'BOTH', 'NONE')),
    digital_format TEXT CHECK(digital_format IN ('PDF', 'EPUB', 'CBZ', 'CBR', 'MOBI', 'AZW', 'NONE')),
    has_file INTEGER DEFAULT 0,
    ebook_file_id INTEGER,
    condition TEXT CHECK(condition IN ('NEW', 'LIKE_NEW', 'VERY_GOOD', 'GOOD', 'FAIR', 'POOR', 'NONE')),
    purchase_date TEXT,
    purchase_price REAL,
    purchase_location TEXT,
    notes TEXT,
    custom_tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (volume_id) REFERENCES volumes(id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE,
    FOREIGN KEY (ebook_file_id) REFERENCES ebook_files(id) ON DELETE SET NULL
)
```

## Foreign Key Constraints

MangaArr uses foreign key constraints to maintain referential integrity:

1. When a series is deleted:
   - All its volumes are deleted (CASCADE)
   - All its chapters are deleted (CASCADE)
   - All its calendar events are deleted (CASCADE)
   - All its e-book files are deleted (CASCADE)
   - All its collection items are deleted (CASCADE)

2. When a volume is deleted:
   - Its chapters' volume_id is set to NULL (SET NULL)
   - Its calendar events are deleted (CASCADE)
   - Its e-book files are deleted (CASCADE)
   - Its collection items are deleted (CASCADE)

3. When a chapter is deleted:
   - Its calendar events are deleted (CASCADE)
   - Its collection items are deleted (CASCADE)
   
4. When an e-book file is deleted:
   - Collection items' ebook_file_id is set to NULL (SET NULL)

## SQLite Configuration

The database is configured with:
```sql
PRAGMA foreign_keys = ON;
```

This ensures that foreign key constraints are enforced.

## Data Types

- `INTEGER`: Used for IDs and numeric values
- `TEXT`: Used for strings, dates, and URLs
- `TIMESTAMP`: Used for created_at and updated_at fields

## Dates

All dates are stored in ISO format (YYYY-MM-DD) as TEXT.

## Migrations

When upgrading from a version before 0.0.5:
1. Back up your database
2. Delete the existing database file
3. Restart MangaArr to create a new database with proper constraints
4. Re-import your series using the metadata providers

## Best Practices

1. Always use foreign key constraints when adding new tables
2. Use CASCADE or SET NULL for foreign key actions based on the relationship
3. Include created_at and updated_at timestamps in all tables
4. Use TEXT for dates to maintain ISO format compatibility
