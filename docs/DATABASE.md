# Readloom Database Schema

This document describes the database schema used by Readloom, including tables, relationships, and constraints.

## Overview

Readloom uses SQLite as its database engine. The database includes foreign key constraints to maintain data integrity and prevent orphaned records.

## Tables

### collections

Collections for organizing manga/comics.

```sql
CREATE TABLE collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    is_default INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### root_folders

Root folders for storing manga/comic files.

```sql
CREATE TABLE root_folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    name TEXT NOT NULL,
    content_type TEXT DEFAULT 'MANGA',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(path)
)
```

### collection_root_folders

Many-to-many relationship between collections and root folders.

```sql
CREATE TABLE collection_root_folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL,
    root_folder_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(collection_id, root_folder_id),
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
)
```

### series_collections

Many-to-many relationship between series and collections.

```sql
CREATE TABLE series_collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(series_id, collection_id),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
)
```

### authors

Authors of books. This table stores information about authors that can be searched and displayed in the UI. The enhanced author search feature uses external providers (primarily OpenLibrary) to fetch additional author information like biographies, photos, and bibliographies.

```sql
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    external_id TEXT,         -- ID from external provider (e.g., OpenLibrary author ID)
    provider TEXT,            -- External provider name (e.g., 'OpenLibrary')
    photo_url TEXT,           -- URL to author photo
    birth_date TEXT,          -- Author's birth date
    death_date TEXT,          -- Author's death date (if applicable)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### series_authors

Many-to-many relationship between series and authors. This table supports the author search feature by linking books to their authors, allowing users to find all books by a specific author.

```sql
CREATE TABLE series_authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    is_primary INTEGER DEFAULT 0,  -- Flag to indicate primary author
    role TEXT,                     -- Author role (e.g., 'author', 'illustrator', 'translator')
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(series_id, author_id),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
)
```

### series

Series information for manga/comics and books.

```sql
CREATE TABLE series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    author TEXT,  -- Legacy field, now using authors table for books
    publisher TEXT,
    cover_url TEXT,
    status TEXT,
    is_book INTEGER DEFAULT 0,  -- Flag to identify books vs manga/comics
    content_type TEXT DEFAULT 'MANGA',
    metadata_source TEXT,
    metadata_id TEXT,
    custom_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

The `custom_path` column was added in version 0.0.9 to allow users to specify a custom folder path for a series, enabling the use of existing folder structures without copying files.

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

Readloom uses foreign key constraints to maintain referential integrity:

1. When a collection is deleted:
   - All its links to root folders are deleted (CASCADE)
   - All its links to series are deleted (CASCADE)

2. When a series is deleted:
   - All its volumes are deleted (CASCADE)
   - All its chapters are deleted (CASCADE)
   - All its calendar events are deleted (CASCADE)
   - All its e-book files are deleted (CASCADE)
   - All its collection items are deleted (CASCADE)
   - All its links to collections are deleted (CASCADE)

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

### Upgrading to v0.0.7

When upgrading to v0.0.7, a migration script will:
1. Create the new collection tables
2. Create a default collection
3. Migrate existing root folders from settings to the database
4. Link root folders to the default collection
5. Add existing series to the default collection

### Upgrading from before v0.0.5

When upgrading from a version before 0.0.5:
1. Back up your database
2. Delete the existing database file
3. Restart Readloom to create a new database with proper constraints
4. Re-import your series using the metadata providers

## External Author Metadata

In addition to the local database tables, Readloom v0.2.0+ supports fetching rich author metadata from external providers:

### OpenLibrary Author API

The primary source for author information is the OpenLibrary API, which provides:

- Author biographies
- Birth and death dates
- Author photos
- Bibliography (list of works)
- External links and references
- Subject areas and genres

This data is fetched on demand and displayed in the UI but is not stored in the local database. The `external_id` field in the `authors` table can be used to link local author records to their corresponding entries in external providers.

### Author Search API

The author search API endpoint (`/api/metadata/author_search`) allows searching for authors across enabled providers. Results include:

- Author name
- Birth and death dates
- Work count
- Notable works
- Author photo URL

### Author Details API

The author details API endpoint (`/api/metadata/author/{provider}/{author_id}`) provides comprehensive information about an author from a specific provider.

## Best Practices

1. Always use foreign key constraints when adding new tables
2. Use CASCADE or SET NULL for foreign key actions based on the relationship
3. Include created_at and updated_at timestamps in all tables
4. Use TEXT for dates to maintain ISO format compatibility
5. Use the `external_id` field to link local author records to external providers
