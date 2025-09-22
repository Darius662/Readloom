# MangaArr API Documentation

This document describes the API endpoints available in MangaArr for integration with other applications.

## API Overview

MangaArr provides a RESTful API that allows you to:

- Manage series, volumes, and chapters
- Access calendar events
- Track your manga/comic collection
- Manage notifications and subscriptions
- Search and import from external manga sources
- Configure settings
- Integrate with Home Assistant and Homarr

All API endpoints are prefixed with `/api`.

## Module Structure

The API is organized into several modules, each handling different functionality:

```
frontend/
├── api.py                # Main API endpoints
├── api_metadata_fixed.py # Metadata API endpoints
├── api_downloader.py     # Downloader API endpoints
├── image_proxy.py        # Image proxy functionality
└── ui.py                 # UI routes
```

The backend implementation has been refactored into a modular package structure:

```
backend/features/
├── calendar/             # Calendar functionality
├── collection/           # Collection management
├── home_assistant/       # Home Assistant integration
├── metadata_providers/   # Metadata providers
├── metadata_service/     # Metadata service
├── notifications/        # Notification system
└── scrapers/             # Web scrapers
```

Each module exports a consistent API through its `__init__.py` file, with compatibility shims maintaining backward compatibility.

## Authentication

Currently, the API does not require authentication when accessed locally. For remote access, standard network security practices should be implemented.

## API Endpoints

### Series Endpoints

#### Get All Series

```
GET /api/series
```

Returns a list of all series in the library.

**Example Response:**
```json
{
  "series": [
    {
      "id": 1,
      "title": "One Piece",
      "description": "The story follows the adventures of Monkey D. Luffy...",
      "author": "Eiichiro Oda",
      "publisher": "Shueisha",
      "cover_url": "https://example.com/cover.jpg",
      "status": "ONGOING",
      "metadata_source": "MANUAL",
      "metadata_id": null,
      "created_at": "2025-09-18T10:00:00",
      "updated_at": "2025-09-18T10:00:00"
    }
  ]
}
```

#### Get Series Details

```
GET /api/series/{id}
```

Returns details of a specific series, including volumes and chapters.

**Example Response:**
```json
{
  "series": {
    "id": 1,
    "title": "One Piece",
    "description": "The story follows the adventures of Monkey D. Luffy...",
    "author": "Eiichiro Oda",
    "publisher": "Shueisha",
    "cover_url": "https://example.com/cover.jpg",
    "status": "ONGOING",
    "metadata_source": "MANUAL",
    "metadata_id": null,
    "created_at": "2025-09-18T10:00:00",
    "updated_at": "2025-09-18T10:00:00"
  },
  "volumes": [...],
  "chapters": [...],
  "upcoming_events": [...]
}
```

#### Add Series

```
POST /api/series
```

Adds a new series to the library.

**Request Body:**
```json
{
  "title": "One Piece",
  "description": "The story follows the adventures of Monkey D. Luffy...",
  "author": "Eiichiro Oda",
  "publisher": "Shueisha",
  "cover_url": "https://example.com/cover.jpg",
  "status": "ONGOING",
  "metadata_source": "MANUAL",
  "metadata_id": null
}
```

**Example Response:**
```json
{
  "series": {
    "id": 1,
    "title": "One Piece",
    "description": "The story follows the adventures of Monkey D. Luffy...",
    "author": "Eiichiro Oda",
    "publisher": "Shueisha",
    "cover_url": "https://example.com/cover.jpg",
    "status": "ONGOING",
    "metadata_source": "MANUAL",
    "metadata_id": null,
    "created_at": "2025-09-18T10:00:00",
    "updated_at": "2025-09-18T10:00:00"
  }
}
```

#### Update Series

```
PUT /api/series/{id}
```

Updates an existing series.

**Request Body:**
```json
{
  "title": "One Piece (Updated)",
  "status": "HIATUS"
}
```

**Example Response:**
```json
{
  "series": {
    "id": 1,
    "title": "One Piece (Updated)",
    "description": "The story follows the adventures of Monkey D. Luffy...",
    "author": "Eiichiro Oda",
    "publisher": "Shueisha",
    "cover_url": "https://example.com/cover.jpg",
    "status": "HIATUS",
    "metadata_source": "MANUAL",
    "metadata_id": null,
    "created_at": "2025-09-18T10:00:00",
    "updated_at": "2025-09-18T10:05:00"
  }
}
```

#### Delete Series

```
DELETE /api/series/{id}
```

Deletes a series and all associated data through cascading deletes:
- All volumes belonging to the series
- All chapters belonging to the series
- All calendar events for the series, its volumes, and chapters

**Example Response:**
```json
{
  "message": "Series deleted successfully",
  "cascade_deleted": {
    "volumes": 5,
    "chapters": 25,
    "calendar_events": 3
  }
}
```

**Note:** This is a cascading delete operation enforced by database constraints. All related data will be automatically removed to maintain referential integrity.

### Volume Endpoints

#### Add Volume

```
POST /api/series/{series_id}/volumes
```

Adds a new volume to a series.

**Request Body:**
```json
{
  "volume_number": "1",
  "title": "Volume 1",
  "description": "The first volume",
  "cover_url": "https://example.com/volume1.jpg",
  "release_date": "2025-10-01"
}
```

**Example Response:**
```json
{
  "volume": {
    "id": 1,
    "series_id": 1,
    "volume_number": "1",
    "title": "Volume 1",
    "description": "The first volume",
    "cover_url": "https://example.com/volume1.jpg",
    "release_date": "2025-10-01",
    "created_at": "2025-09-18T10:10:00",
    "updated_at": "2025-09-18T10:10:00"
  }
}
```

#### Update Volume

```
PUT /api/volumes/{id}
```

Updates an existing volume.

**Request Body:**
```json
{
  "title": "Volume 1 (Updated)",
  "release_date": "2025-10-15"
}
```

**Example Response:**
```json
{
  "volume": {
    "id": 1,
    "series_id": 1,
    "volume_number": "1",
    "title": "Volume 1 (Updated)",
    "description": "The first volume",
    "cover_url": "https://example.com/volume1.jpg",
    "release_date": "2025-10-15",
    "created_at": "2025-09-18T10:10:00",
    "updated_at": "2025-09-18T10:15:00"
  }
}
```

#### Delete Volume

```
DELETE /api/volumes/{id}
```

Deletes a volume and its associated data:
- Sets volume_id to NULL for any chapters in this volume
- Deletes all calendar events for this volume

**Example Response:**
```json
{
  "message": "Volume deleted successfully",
  "cascade_deleted": {
    "calendar_events": 1
  },
  "chapters_updated": 5
}
```

**Note:** Chapter records are preserved but their volume_id is set to NULL. Calendar events are deleted through cascading constraints.

### Chapter Endpoints

#### Add Chapter

```
POST /api/series/{series_id}/chapters
```

Adds a new chapter to a series.

**Request Body:**
```json
{
  "chapter_number": "1",
  "title": "Chapter 1",
  "volume_id": 1,
  "description": "The first chapter",
  "release_date": "2025-10-01",
  "status": "ANNOUNCED",
  "read_status": "UNREAD"
}
```

**Example Response:**
```json
{
  "chapter": {
    "id": 1,
    "series_id": 1,
    "volume_id": 1,
    "chapter_number": "1",
    "title": "Chapter 1",
    "description": "The first chapter",
    "release_date": "2025-10-01",
    "status": "ANNOUNCED",
    "read_status": "UNREAD",
    "created_at": "2025-09-18T10:20:00",
    "updated_at": "2025-09-18T10:20:00"
  }
}
```

#### Update Chapter

```
PUT /api/chapters/{id}
```

Updates an existing chapter.

**Request Body:**
```json
{
  "title": "Chapter 1 (Updated)",
  "status": "RELEASED",
  "read_status": "READ"
}
```

**Example Response:**
```json
{
  "chapter": {
    "id": 1,
    "series_id": 1,
    "volume_id": 1,
    "chapter_number": "1",
    "title": "Chapter 1 (Updated)",
    "description": "The first chapter",
    "release_date": "2025-10-01",
    "status": "RELEASED",
    "read_status": "READ",
    "created_at": "2025-09-18T10:20:00",
    "updated_at": "2025-09-18T10:25:00"
  }
}
```

#### Delete Chapter

```
DELETE /api/chapters/{id}
```

Deletes a chapter and its associated data:
- Deletes all calendar events for this chapter

**Example Response:**
```json
{
  "message": "Chapter deleted successfully",
  "cascade_deleted": {
    "calendar_events": 1
  }
}
```

**Note:** Calendar events are deleted through cascading constraints.

### Folder Management Endpoints

#### Create Series Folder

```
POST /api/folders/create/{series_id}
```

Creates a folder for a specific series in the configured root folder.

**Parameters:**

- `series_id` (path) - The ID of the series

**Response:**

```json
{
  "success": true,
  "folder_path": "C:\\Users\\username\\Documents\\Mangas\\One Piece",
  "readme_created": true
}
```

#### Create All Missing Folders

```
POST /api/folders/create-all
```

Creates folders for all series that don't have folders yet.

**Response:**

```json
{
  "success": true,
  "folders_created": 5,
  "errors": 0
}
```

### Collection Endpoints

#### Get All Collections

```
GET /api/collections
```

Returns a list of all collections.

**Response:**

```json
{
  "success": true,
  "collections": [
    {
      "id": 1,
      "name": "My Collection",
      "description": "My first manga collection",
      "is_default": 1,
      "created_at": "2025-09-22T10:00:00",
      "updated_at": "2025-09-22T10:00:00",
      "root_folder_count": 2,
      "series_count": 5
    }
  ]
}
```

#### Get Collection Details

```
GET /api/collections/{collection_id}
```

Returns details of a specific collection.

**Parameters:**

- `collection_id` (path) - The ID of the collection

**Response:**

```json
{
  "success": true,
  "collection": {
    "id": 1,
    "name": "My Collection",
    "description": "My first manga collection",
    "is_default": 1,
    "created_at": "2025-09-22T10:00:00",
    "updated_at": "2025-09-22T10:00:00",
    "root_folder_count": 2,
    "series_count": 5
  }
}
```

#### Create Collection

```
POST /api/collections
```

Creates a new collection.

**Request Body:**

```json
{
  "name": "New Collection",
  "description": "My new manga collection",
  "is_default": false
}
```

**Response:**

```json
{
  "success": true,
  "message": "Collection 'New Collection' created successfully",
  "collection": {
    "id": 2,
    "name": "New Collection",
    "description": "My new manga collection",
    "is_default": 0,
    "created_at": "2025-09-22T10:00:00",
    "updated_at": "2025-09-22T10:00:00",
    "root_folder_count": 0,
    "series_count": 0
  }
}
```

#### Update Collection

```
PUT /api/collections/{collection_id}
```

Updates an existing collection.

**Parameters:**

- `collection_id` (path) - The ID of the collection

**Request Body:**

```json
{
  "name": "Updated Collection",
  "description": "Updated description",
  "is_default": true
}
```

**Response:**

```json
{
  "success": true,
  "message": "Collection updated successfully",
  "collection": {
    "id": 2,
    "name": "Updated Collection",
    "description": "Updated description",
    "is_default": 1,
    "created_at": "2025-09-22T10:00:00",
    "updated_at": "2025-09-22T10:01:00",
    "root_folder_count": 0,
    "series_count": 0
  }
}
```

#### Delete Collection

```
DELETE /api/collections/{collection_id}
```

Deletes a collection.

**Parameters:**

- `collection_id` (path) - The ID of the collection

**Response:**

```json
{
  "success": true,
  "message": "Collection deleted successfully"
}
```

#### Get Default Collection

```
GET /api/collections/default
```

Returns the default collection.

**Response:**

```json
{
  "success": true,
  "collection": {
    "id": 1,
    "name": "My Collection",
    "description": "My first manga collection",
    "is_default": 1,
    "created_at": "2025-09-22T10:00:00",
    "updated_at": "2025-09-22T10:00:00"
  }
}
```

### Root Folder Endpoints

#### Get All Root Folders

```
GET /api/root-folders
```

Returns a list of all root folders.

**Response:**

```json
{
  "success": true,
  "root_folders": [
    {
      "id": 1,
      "path": "C:\\Manga",
      "name": "Main Library",
      "content_type": "MANGA",
      "created_at": "2025-09-22T10:00:00",
      "updated_at": "2025-09-22T10:00:00",
      "collection_count": 1,
      "exists": true
    }
  ]
}
```

#### Create Root Folder

```
POST /api/root-folders
```

Creates a new root folder.

**Request Body:**

```json
{
  "path": "D:\\Comics",
  "name": "Comics Library",
  "content_type": "COMICS"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Root folder 'Comics Library' created successfully",
  "root_folder": {
    "id": 2,
    "path": "D:\\Comics",
    "name": "Comics Library",
    "content_type": "COMICS",
    "created_at": "2025-09-22T10:00:00",
    "updated_at": "2025-09-22T10:00:00",
    "collection_count": 0,
    "exists": true
  }
}
```

#### Update Root Folder

```
PUT /api/root-folders/{root_folder_id}
```

Updates an existing root folder.

**Parameters:**

- `root_folder_id` (path) - The ID of the root folder

**Request Body:**

```json
{
  "name": "Updated Comics Library",
  "content_type": "COMICS"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Root folder updated successfully",
  "root_folder": {
    "id": 2,
    "path": "D:\\Comics",
    "name": "Updated Comics Library",
    "content_type": "COMICS",
    "created_at": "2025-09-22T10:00:00",
    "updated_at": "2025-09-22T10:01:00",
    "collection_count": 0,
    "exists": true
  }
}
```

#### Delete Root Folder

```
DELETE /api/root-folders/{root_folder_id}
```

Deletes a root folder.

**Parameters:**

- `root_folder_id` (path) - The ID of the root folder

**Response:**

```json
{
  "success": true,
  "message": "Root folder deleted successfully"
}
```

#### Get Collection Root Folders

```
GET /api/collections/{collection_id}/root-folders
```

Returns all root folders for a collection.

**Parameters:**

- `collection_id` (path) - The ID of the collection

**Response:**

```json
{
  "success": true,
  "root_folders": [
    {
      "id": 1,
      "path": "C:\\Manga",
      "name": "Main Library",
      "content_type": "MANGA",
      "created_at": "2025-09-22T10:00:00",
      "updated_at": "2025-09-22T10:00:00",
      "exists": true
    }
  ]
}
```

#### Add Root Folder to Collection

```
POST /api/collections/{collection_id}/root-folders/{root_folder_id}
```

Adds a root folder to a collection.

**Parameters:**

- `collection_id` (path) - The ID of the collection
- `root_folder_id` (path) - The ID of the root folder

**Response:**

```json
{
  "success": true,
  "message": "Root folder added to collection successfully"
}
```

#### Remove Root Folder from Collection

```
DELETE /api/collections/{collection_id}/root-folders/{root_folder_id}
```

Removes a root folder from a collection.

**Parameters:**

- `collection_id` (path) - The ID of the collection
- `root_folder_id` (path) - The ID of the root folder

**Response:**

```json
{
  "success": true,
  "message": "Root folder removed from collection successfully"
}
```

#### Get Collection Series

```
GET /api/collections/{collection_id}/series
```

Returns all series in a collection.

**Parameters:**

- `collection_id` (path) - The ID of the collection

**Response:**

```json
{
  "success": true,
  "series": [
    {
      "id": 1,
      "title": "One Piece",
      "description": "The story follows the adventures of Monkey D. Luffy...",
      "author": "Eiichiro Oda",
      "publisher": "Shueisha",
      "cover_url": "https://example.com/cover.jpg",
      "status": "ONGOING",
      "content_type": "MANGA",
      "metadata_source": "MANUAL",
      "metadata_id": null,
      "created_at": "2025-09-18T10:00:00",
      "updated_at": "2025-09-18T10:00:00"
    }
  ]
}
```

#### Add Series to Collection

```
POST /api/collections/{collection_id}/series/{series_id}
```

Adds a series to a collection.

**Parameters:**

- `collection_id` (path) - The ID of the collection
- `series_id` (path) - The ID of the series

**Response:**

```json
{
  "success": true,
  "message": "Series added to collection successfully"
}
```

#### Remove Series from Collection

```
DELETE /api/collections/{collection_id}/series/{series_id}
```

Removes a series from a collection.

**Parameters:**

- `collection_id` (path) - The ID of the collection
- `series_id` (path) - The ID of the series

**Response:**

```json
{
  "success": true,
  "message": "Series removed from collection successfully"
}
```

### E-book Endpoints

#### Scan for E-books

```
POST /api/ebooks/scan
```

Scans all series folders for e-book files.

**Response:**

```json
{
  "stats": {
    "scanned": 10,
    "added": 2,
    "skipped": 7,
    "errors": 1,
    "series_processed": 3
  }
}
```

#### Scan Series for E-books

```
POST /api/ebooks/scan/{series_id}
```

Scans a specific series folder for e-book files.

**Parameters:**

- `series_id` (path) - The ID of the series to scan

**Response:**

```json
{
  "stats": {
    "scanned": 3,
    "added": 1,
    "skipped": 2,
    "errors": 0,
    "series_processed": 1
  }
}
```

#### Get E-book Files for Series

```
GET /api/ebooks/series/{series_id}
```

Returns all e-book files for a specific series.

**Parameters:**

- `series_id` (path) - The ID of the series

**Response:**

```json
{
  "files": [
    {
      "id": 1,
      "series_id": 123,
      "volume_id": 456,
      "file_path": "data/ebooks/MANGA/Series_Name/Volume_1.pdf",
      "file_name": "1632145678_Volume_1.pdf",
      "file_size": 12345678,
      "file_type": "PDF",
      "original_name": "Volume_1.pdf",
      "added_date": "2025-09-21T22:15:30",
      "created_at": "2025-09-21T22:15:30",
      "updated_at": "2025-09-21T22:15:30"
    }
  ]
}
```

#### Get E-book Files for Volume

```
GET /api/ebooks/volume/{volume_id}
```

Returns all e-book files for a specific volume.

**Parameters:**

- `volume_id` (path) - The ID of the volume

**Response:**

```json
{
  "files": [
    {
      "id": 1,
      "series_id": 123,
      "volume_id": 456,
      "file_path": "data/ebooks/MANGA/Series_Name/Volume_1.pdf",
      "file_name": "1632145678_Volume_1.pdf",
      "file_size": 12345678,
      "file_type": "PDF",
      "original_name": "Volume_1.pdf",
      "added_date": "2025-09-21T22:15:30",
      "created_at": "2025-09-21T22:15:30",
      "updated_at": "2025-09-21T22:15:30"
    }
  ]
}
```

#### Download E-book File

```
GET /api/ebooks/download/{file_id}
```

Downloads an e-book file.

**Parameters:**

- `file_id` (path) - The ID of the e-book file

**Response:**

The file content with appropriate Content-Type header.

### Calendar Endpoints

#### Get Calendar Events

```
GET /api/calendar
```

Returns calendar events within a specified date range. The calendar shows all release dates for manga in your collection, with no date range restrictions.

**Query Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `series_id` (optional): Filter events by series ID

**Note:** While the calendar API accepts date range parameters for pagination and display purposes, it stores and can show all release dates without any date restrictions. Historical release dates and future releases are all preserved.

**Example Response:**
```json
{
  "events": [
    {
      "id": 1,
      "title": "Chapter 1 - One Piece",
      "description": "Release of chapter 1: Chapter 1",
      "date": "2025-10-01",
      "type": "CHAPTER_RELEASE",
      "series": {
        "id": 1,
        "title": "One Piece",
        "cover_url": "https://example.com/cover.jpg"
      },
      "chapter": {
        "id": 1,
        "number": "1",
        "title": "Chapter 1"
      }
    }
  ]
}
```

#### Refresh Calendar

```
POST /api/calendar/refresh
```

Refreshes the calendar data. You can optionally specify a series ID to only update that specific series.

**Query Parameters:**
- `series_id` (optional): Only update calendar events for this specific series

**Example Request (Full Refresh):**
```
POST /api/calendar/refresh
```

**Example Request (Series-Specific Refresh):**
```
POST /api/calendar/refresh?series_id=42
```

**Example Response:**
```json
{
  "message": "Calendar refreshed successfully"
}
```

**Note:** Using the series-specific refresh is much more efficient when adding new manga or updating a single series, as it doesn't scan the entire collection.

### Settings Endpoints

#### Get Settings

```
GET /api/settings
```

Returns all application settings.

**Example Response:**
```json
{
  "host": "0.0.0.0",
  "port": 7227,
  "url_base": "",
  "log_level": "INFO",
  "log_rotation": 5,
  "log_size": 10,
  "metadata_cache_days": 7,
  "calendar_range_days": 14,
  "calendar_refresh_hours": 12,
  "task_interval_minutes": 60
}
```

**Note:** While `calendar_range_days` sets a default display range for the calendar UI, the calendar system stores and can display events from any date range. This setting primarily affects the initial view in the UI.
```

#### Update Settings

```
PUT /api/settings
```

Updates application settings.

**Request Body:**
```json
{
  "calendar_range_days": 30,
  "calendar_refresh_hours": 6
}
```

**Example Response:**
```json
{
  "host": "0.0.0.0",
  "port": 7227,
  "url_base": "",
  "log_level": "INFO",
  "log_rotation": 5,
  "log_size": 10,
  "metadata_cache_days": 7,
  "calendar_range_days": 30,
  "calendar_refresh_hours": 6,
  "task_interval_minutes": 60
}
```

### Collection Tracking Endpoints

#### Get Collection Items

```
GET /api/collection
```

Returns collection items with optional filters.

**Query Parameters:**
- `series_id` (optional): Filter by series ID
- `item_type` (optional): Filter by item type (SERIES, VOLUME, CHAPTER)
- `ownership_status` (optional): Filter by ownership status (OWNED, WANTED, ORDERED)
- `read_status` (optional): Filter by read status (READ, READING, UNREAD)
- `format` (optional): Filter by format (PHYSICAL, DIGITAL)

**Example Response:**
```json
{
  "items": [
    {
      "id": 1,
      "series_id": 1,
      "series_title": "One Piece",
      "item_type": "VOLUME",
      "volume_id": 1,
      "volume_number": "1",
      "chapter_id": null,
      "chapter_number": null,
      "ownership_status": "OWNED",
      "read_status": "READ",
      "format": "PHYSICAL",
      "condition": "GOOD",
      "purchase_date": "2025-09-01",
      "purchase_price": 9.99,
      "purchase_location": "Local Bookstore",
      "notes": "First edition",
      "custom_tags": ["favorite", "signed"],
      "created_at": "2025-09-18T10:30:00",
      "updated_at": "2025-09-18T10:30:00"
    }
  ]
}
```

#### Get Collection Statistics

```
GET /api/collection/stats
```

Returns statistics about the collection.

**Example Response:**
```json
{
  "total_items": 50,
  "owned_volumes": 45,
  "read_volumes": 30,
  "total_value": 449.55,
  "formats": {
    "PHYSICAL": 40,
    "DIGITAL": 10
  },
  "conditions": {
    "MINT": 10,
    "GOOD": 30,
    "FAIR": 5
  },
  "series_breakdown": [
    {
      "series_id": 1,
      "series_title": "One Piece",
      "owned_count": 20,
      "total_count": 25,
      "completion_percentage": 80
    }
  ]
}
```

#### Add to Collection

```
POST /api/collection
```

Adds an item to the collection.

**Request Body:**
```json
{
  "series_id": 1,
  "item_type": "VOLUME",
  "volume_id": 1,
  "ownership_status": "OWNED",
  "read_status": "READ",
  "format": "PHYSICAL",
  "condition": "GOOD",
  "purchase_date": "2025-09-01",
  "purchase_price": 9.99,
  "purchase_location": "Local Bookstore",
  "notes": "First edition",
  "custom_tags": ["favorite", "signed"]
}
```

**Example Response:**
```json
{
  "id": 1
}
```

#### Update Collection Item

```
PUT /api/collection/{item_id}
```

Updates a collection item.

**Request Body:**
```json
{
  "ownership_status": "OWNED",
  "read_status": "READING",
  "condition": "FAIR"
}
```

**Example Response:**
```json
{
  "message": "Collection item updated successfully"
}
```

#### Remove from Collection

```
DELETE /api/collection/{item_id}
```

Removes an item from the collection.

**Example Response:**
```json
{
  "message": "Collection item removed successfully"
}
```

#### Import Collection

```
POST /api/collection/import
```

Imports collection data from JSON.

**Request Body:**
```json
{
  "items": [
    {
      "series_id": 1,
      "item_type": "VOLUME",
      "volume_id": 1,
      "ownership_status": "OWNED",
      "read_status": "READ",
      "format": "PHYSICAL"
    }
  ]
}
```

**Example Response:**
```json
{
  "imported_count": 1,
  "failed_count": 0
}
```

#### Export Collection

```
GET /api/collection/export
```

Exports collection data as JSON.

**Example Response:**
```json
{
  "items": [...]
}
```

### Notification Endpoints

#### Get Notifications

```
GET /api/notifications
```

Returns notifications.

**Query Parameters:**
- `limit` (optional): Maximum number of notifications to return (default: 50)
- `unread_only` (optional): Whether to only return unread notifications (default: false)

**Example Response:**
```json
{
  "notifications": [
    {
      "id": 1,
      "title": "New Volume Release",
      "message": "Volume 100 of One Piece will be released tomorrow!",
      "type": "INFO",
      "read": false,
      "created_at": "2025-09-18T12:00:00"
    }
  ]
}
```

#### Mark Notification as Read

```
PUT /api/notifications/{notification_id}/read
```

Marks a notification as read.

**Example Response:**
```json
{
  "message": "Notification marked as read"
}
```

#### Mark All Notifications as Read

```
PUT /api/notifications/read
```

Marks all notifications as read.

**Example Response:**
```json
{
  "message": "All notifications marked as read"
}
```

#### Delete Notification

```
DELETE /api/notifications/{notification_id}
```

Deletes a notification.

**Example Response:**
```json
{
  "message": "Notification deleted"
}
```

#### Delete All Notifications

```
DELETE /api/notifications
```

Deletes all notifications.

**Example Response:**
```json
{
  "message": "All notifications deleted"
}
```

#### Get Notification Settings

```
GET /api/notifications/settings
```

Returns notification settings.

**Example Response:**
```json
{
  "email_enabled": 0,
  "email_address": null,
  "browser_enabled": 1,
  "discord_enabled": 0,
  "discord_webhook": null,
  "telegram_enabled": 0,
  "telegram_bot_token": null,
  "telegram_chat_id": null,
  "notify_new_volumes": 1,
  "notify_new_chapters": 1,
  "notify_releases_days_before": 1
}
```

#### Update Notification Settings

```
PUT /api/notifications/settings
```

Updates notification settings.

**Request Body:**
```json
{
  "email_enabled": true,
  "email_address": "user@example.com",
  "notify_releases_days_before": 2
}
```

**Example Response:**
```json
{
  "message": "Notification settings updated"
}
```

#### Send Test Notification

```
POST /api/notifications/test
```

Sends a test notification.

**Request Body:**
```json
{
  "title": "Test Notification",
  "message": "This is a test notification",
  "type": "INFO"
}
```

**Example Response:**
```json
{
  "message": "Test notification sent"
}
```

### Subscription Endpoints

#### Get Subscriptions

```
GET /api/subscriptions
```

Returns all subscriptions.

**Example Response:**
```json
{
  "subscriptions": [
    {
      "id": 1,
      "series_id": 1,
      "series_title": "One Piece",
      "series_author": "Eiichiro Oda",
      "series_cover_url": "https://example.com/cover.jpg",
      "notify_new_volumes": 1,
      "notify_new_chapters": 1,
      "created_at": "2025-09-18T12:30:00"
    }
  ]
}
```

#### Check Subscription Status

```
GET /api/subscriptions/{series_id}
```

Checks if a series is subscribed to.

**Example Response:**
```json
{
  "subscribed": true
}
```

#### Subscribe to Series

```
POST /api/subscriptions
```

Subscribes to a series.

**Request Body:**
```json
{
  "series_id": 1,
  "notify_new_volumes": true,
  "notify_new_chapters": true
}
```

**Example Response:**
```json
{
  "id": 1
}
```

#### Unsubscribe from Series

```
DELETE /api/subscriptions/{series_id}
```

Unsubscribes from a series.

**Example Response:**
```json
{
  "message": "Unsubscribed from series"
}
```

#### Check Upcoming Releases

```
POST /api/monitor/check-releases
```

Checks for upcoming releases and sends notifications.

**Example Response:**
```json
{
  "releases": [...]
}
```

### Integration Endpoints

#### Home Assistant Integration Data

```
GET /api/integrations/home-assistant
```

Returns data for Home Assistant integration.

**Example Response:**
```json
{
  "stats": {
    "series_count": 5,
    "volume_count": 25,
    "chapter_count": 150,
    "owned_volumes": 20,
    "read_volumes": 15,
    "collection_value": 199.95
  },
  "upcoming_releases": [...],
  "releases_by_date": {...},
  "releases_today": 2,
  "releases_this_week": 5,
  "last_updated": "2025-09-18T13:00:00"
}
```

#### Home Assistant Setup Instructions

```
GET /api/integrations/home-assistant/setup
```

Returns setup instructions for Home Assistant integration.

**Example Response:**
```json
{
  "title": "MangaArr Home Assistant Integration",
  "description": "Follow these steps to integrate MangaArr with your Home Assistant instance.",
  "base_url": "http://localhost:7227",
  "api_endpoint": "http://localhost:7227/api/integrations/home-assistant",
  "steps": [...],
  "notes": [...]
}
```

#### Homarr Integration Data

```
GET /api/integrations/homarr
```

Returns data for Homarr integration.

**Example Response:**
```json
{
  "app": "MangaArr",
  "version": "1.0.0",
  "status": "ok",
  "info": {
    "series_count": 5,
    "volume_count": 25,
    "chapter_count": 150,
    "owned_volumes": 20,
    "releases_today": 2
  }
}
```

#### Homarr Setup Instructions

```
GET /api/integrations/homarr/setup
```

Returns setup instructions for Homarr integration.

**Example Response:**
```json
{
  "title": "MangaArr Homarr Integration",
  "description": "Follow these steps to integrate MangaArr with your Homarr dashboard.",
  "base_url": "http://localhost:7227",
  "api_endpoint": "http://localhost:7227/api/integrations/homarr",
  "steps": [...],
  "notes": [...]
}
```

### Metadata API Endpoints

All metadata API endpoints are prefixed with `/api/metadata`.

#### Search Manga

```
GET /api/metadata/search
```

Search for manga across all enabled providers or a specific provider.

**Query Parameters:**
- `query` (required): The search query
- `provider` (optional): The provider name
- `page` (optional): The page number (default: 1)

**Example Response:**
```json
{
  "query": "One Piece",
  "page": 1,
  "results": {
    "MangaFire": [
      {
        "id": "one-piece",
        "title": "One Piece",
        "cover_url": "https://example.com/cover.jpg",
        "author": "Eiichiro Oda",
        "status": "ONGOING",
        "latest_chapter": "Chapter 1050",
        "url": "https://mangafire.to/manga/one-piece",
        "source": "MangaFire"
      }
    ],
    "MyAnimeList": [...]
  },
  "timestamp": "2025-09-19T10:30:00"
}
```

#### Get Manga Details

```
GET /api/metadata/manga/{provider}/{manga_id}
```

Get details for a manga from a specific provider.

**Example Response:**
```json
{
  "id": "one-piece",
  "title": "One Piece",
  "alternative_titles": ["ワンピース", "Wan Pīsu"],
  "cover_url": "https://example.com/cover.jpg",
  "author": "Eiichiro Oda",
  "status": "ONGOING",
  "description": "The story follows the adventures of Monkey D. Luffy...",
  "genres": ["Action", "Adventure", "Comedy", "Fantasy"],
  "rating": "4.9",
  "url": "https://mangafire.to/manga/one-piece",
  "source": "MangaFire"
}
```

#### Import Manga to Collection

```
POST /api/metadata/manga/{provider}/{manga_id}/import
```

Imports a manga from a provider to your collection. This endpoint:
1. Adds the manga to your database
2. Creates a folder structure for the manga in your configured root folder
3. Generates a README.txt file with series information
4. Updates the calendar with release dates

**Example Request:**
```
POST /api/metadata/manga/AniList/21/import
```

**Example Response:**
```json
{
  "success": true,
  "message": "Manga imported successfully",
  "series_id": 42,
  "folder_created": "C:\\Users\\username\\Documents\\Mangas\\One Piece"
}
```

**Note:** The folder name preserves spaces and most special characters from the original title, only replacing characters that are invalid in file names.

#### Get Chapter List

```
GET /api/metadata/manga/{provider}/{manga_id}/chapters
```

Get the chapter list for a manga from a specific provider.

**Example Response:**
```json
{
  "chapters": [
    {
      "id": "chapter-1050",
      "title": "Chapter 1050",
      "number": "1050",
      "date": "2025-09-15",
      "url": "https://mangafire.to/manga/one-piece/chapter-1050",
      "manga_id": "one-piece"
    }
  ]
}
```

#### Get Chapter Images

```
GET /api/metadata/manga/{provider}/{manga_id}/chapter/{chapter_id}
```

Get the images for a chapter from a specific provider.

**Example Response:**
```json
{
  "images": [
    "https://example.com/images/chapter-1050/1.jpg",
    "https://example.com/images/chapter-1050/2.jpg"
  ]
}
```

#### Get Latest Releases

```
GET /api/metadata/latest
```

Get the latest manga releases from all enabled providers or a specific provider.

**Query Parameters:**
- `provider` (optional): The provider name
- `page` (optional): The page number (default: 1)

**Example Response:**
```json
{
  "page": 1,
  "results": {
    "MangaFire": [
      {
        "manga_id": "one-piece",
        "manga_title": "One Piece",
        "cover_url": "https://example.com/cover.jpg",
        "chapter": "Chapter 1050",
        "chapter_id": "chapter-1050",
        "date": "2025-09-15",
        "url": "https://mangafire.to/manga/one-piece/chapter-1050",
        "source": "MangaFire"
      }
    ],
    "MyAnimeList": [...]
  },
  "timestamp": "2025-09-19T10:30:00"
}
```

#### Get Metadata Providers

```
GET /api/metadata/providers
```

Get all metadata providers and their settings.

**Example Response:**
```json
{
  "providers": {
    "MangaFire": {
      "enabled": true,
      "settings": {}
    },
    "MyAnimeList": {
      "enabled": true,
      "settings": {
        "client_id": "your_client_id"
      }
    },
    "MangaAPI": {
      "enabled": true,
      "settings": {
        "api_url": "https://manga-api.fly.dev"
      }
    }
  },
  "timestamp": "2025-09-19T10:30:00"
}
```

#### Update Metadata Provider

```
PUT /api/metadata/providers/{name}
```

Update a metadata provider's settings.

**Request Body:**
```json
{
  "enabled": true,
  "settings": {
    "client_id": "your_new_client_id"
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "message": "Provider MyAnimeList updated successfully"
}
```

#### Clear Metadata Cache

```
DELETE /api/metadata/cache
```

Clear the metadata cache.

**Query Parameters:**
- `provider` (optional): The provider name
- `type` (optional): The cache type

**Example Response:**
```json
{
  "success": true,
  "message": "Cache cleared successfully"
}
```

#### Import Manga to Collection

```
POST /api/metadata/import/{provider}/{manga_id}
```

Import a manga from an external source to the collection.

**Example Success Response:**
```json
{
  "success": true,
  "message": "Series added to collection with 50 chapters",
  "series_id": 123
}
```

**Example Already Exists Response:**
```json
{
  "success": false,
  "already_exists": true,
  "message": "Series already exists in the collection",
  "series_id": 123
}
```

**Note:** When a series already exists in the collection, the API returns a 200 status code with `already_exists: true` instead of treating it as an error. This allows clients to handle this case gracefully and potentially show a link to the existing series.

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a JSON object with an error message:

```json
{
  "error": "Error message"
}
```

## API Usage Examples

### Python Example

```python
import requests

# Get all series
response = requests.get('http://localhost:7227/api/series')
series = response.json()['series']

# Add a new series
new_series = {
    "title": "My New Series",
    "author": "Author Name",
    "status": "ONGOING"
}
response = requests.post('http://localhost:7227/api/series', json=new_series)
created_series = response.json()['series']
```

### JavaScript Example

```javascript
// Get all series
fetch('http://localhost:7227/api/series')
  .then(response => response.json())
  .then(data => {
    const series = data.series;
    console.log(series);
  });

// Add a new series
const newSeries = {
  title: "My New Series",
  author: "Author Name",
  status: "ONGOING"
};

fetch('http://localhost:7227/api/series', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(newSeries)
})
  .then(response => response.json())
  .then(data => {
    const createdSeries = data.series;
    console.log(createdSeries);
  });
```

## Rate Limiting

Currently, there are no rate limits implemented for the API. However, it's recommended to limit requests to avoid performance issues.

## API Changes

API changes will be documented in the [CHANGELOG.md](CHANGELOG.md) file. Breaking changes will be accompanied by a major version bump.
