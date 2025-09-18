# MangaArr API Documentation

This document describes the API endpoints available in MangaArr for integration with other applications.

## API Overview

MangaArr provides a RESTful API that allows you to:

- Manage series, volumes, and chapters
- Access calendar events
- Configure settings
- Integrate with other applications

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

### Integration Endpoints

#### Home Assistant Integration

```
GET /api/integrations/home-assistant
```

Returns data for Home Assistant integration.

**Example Response:**
```json
{
  "upcoming_releases": [...],
  "stats": {
    "series_count": 5,
    "volume_count": 25,
    "chapter_count": 150
  }
}
```

#### Homarr Integration

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
    "releases_today": 2
  }
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
