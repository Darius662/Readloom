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

## Foreign Key Constraints

MangaArr uses foreign key constraints to maintain referential integrity:

1. When a series is deleted:
   - All its volumes are deleted (CASCADE)
   - All its chapters are deleted (CASCADE)
   - All its calendar events are deleted (CASCADE)

2. When a volume is deleted:
   - Its chapters' volume_id is set to NULL (SET NULL)
   - Its calendar events are deleted (CASCADE)

3. When a chapter is deleted:
   - Its calendar events are deleted (CASCADE)

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
