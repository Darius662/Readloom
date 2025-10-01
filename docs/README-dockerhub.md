# Readloom - E-book Collection Manager

Readloom is a comprehensive e-book collection manager that helps you organize, track, and manage your digital book collection.

## Features

- **E-book Management**: Organize and track digital books and comics
- **Collection System**: Organize e-books into collections linked to root folders
- **Metadata Providers**: 
  - Google Books (enabled by default)
  - Open Library
  - ISBNdb
  - WorldCat
  - AniList (for manga/comics)
- **Calendar**: Track upcoming releases
- **Library Management**: Track ownership, read status, and more
- **Docker Ready**: Easy deployment with Docker

## Quick Start

```bash
docker run -d \
  --name readloom \
  -p 7227:7227 \
  -v /path/to/data:/config \
  -v /path/to/ebooks:/ebooks \
  yourusername/readloom:latest
```

Readloom will be available at http://localhost:7227

## Environment Variables

- `TZ`: Set your timezone (default: UTC)
- `PYTHONUNBUFFERED`: Ensures Python output is not buffered (set to 1)

## Volumes

- `/config`: Stores configuration, database, and logs
- `/ebooks`: Mount your e-book collection here (optional)

## Docker Compose

```yaml
services:
  readloom:
    image: yourusername/readloom:latest
    container_name: readloom
    restart: unless-stopped
    ports:
      - "7227:7227"
    volumes:
      - ./data:/config
      - /path/to/ebooks:/ebooks
    environment:
      - TZ=UTC
```

## Documentation

For more information, visit the [GitHub repository](https://github.com/yourusername/Readloom).
