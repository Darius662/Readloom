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

Deletes a series and all associated volumes, chapters, and calendar events.

**Example Response:**
```json
{
  "message": "Series deleted successfully"
}
```

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

Deletes a volume.

**Example Response:**
```json
{
  "message": "Volume deleted successfully"
}
```

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

Deletes a chapter.

**Example Response:**
```json
{
  "message": "Chapter deleted successfully"
}
```

### Calendar Endpoints

#### Get Calendar Events

```
GET /api/calendar
```

Returns calendar events within a specified date range.

**Query Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `series_id` (optional): Filter events by series ID

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

Refreshes the calendar data.

**Example Response:**
```json
{
  "message": "Calendar refreshed successfully"
}
```

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

**Example Response:**
```json
{
  "success": true,
  "message": "Series added to collection with 50 chapters",
  "series_id": 123
}
```

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
