# Readloom

Readloom is a manga, manwa, and comics collection manager with a focus on release tracking and calendar functionality. It follows the design principles of the *arr suite of applications but with a specialized focus on manga and comics.

![Readloom Dashboard](frontend/static/img/screenshot.png)

## Features

- **Enhanced Release Calendar**: Interactive calendar showing manga/comic releases
  - Sonarr/Radarr-like calendar showing only upcoming confirmed releases
  - Complete historical and future release date tracking
  - Filter options for manga/comics by type and series
  - Different view modes (month, week, list)
  - Color coding for different types of releases
  - Add releases to collection directly from calendar
  - Efficient series-specific calendar updates (v0.0.5+)
  - Performance-optimized for large collections
- **E-book Management System** (v0.0.5+): Organize and track your digital manga/comics
  - Organized folder structure by series name with human-readable folder names (v0.0.6+)
  - Automatic volume number detection from filenames
  - Support for multiple e-book formats (PDF, EPUB, CBZ, CBR, MOBI, AZW)
  - Periodic scanning for new files
  - Manual scan button in the UI
  - Collection integration with digital format tracking
  - Automatic README files with series information
- **Comprehensive Collection System** (v0.0.7+): Organize and track your manga/comic collection
  - Flexible collection-based organization system
  - Link collections to multiple root folders
  - Add series to multiple collections
  - Track ownership status, read status, and purchase details
  - Track both physical and digital formats
  - Collection statistics and visualizations
  - Import/export functionality
- **External Source Integration**: Connect to popular manga and book sources
  - AniList integration with intelligent release date prediction
  - MyAnimeList (MAL) integration for metadata and searching
  - MangaDex integration for searching and importing manga
  - OpenLibrary integration for books and comprehensive author information
  - Google Books integration for detailed book metadata
  - Multi-source accurate chapter counting system
  - Advanced volume detection with multiple scrapers (v0.0.5+)
  - MangaFire integration for accurate volume data
  - Search interface for finding manga, books, and authors across multiple sources
  - **Enhanced author search and details** (v0.2.0+):
    - Author profiles with photos, biographies, and bibliographies
    - Comprehensive subject categorization for authors
    - Notable works listing with direct links
    - External resource links (Goodreads, Wikipedia, etc.)
    - Author-specific metadata from OpenLibrary
- **Author Collection Management** (v0.1.7+):
    - Add authors to collections with proper folder structure
    - Create author folders with subfolders for notable works
    - Generate README.md files with author information
    - Add more books to existing author folders
    - Consistent folder organization for authors and their books
- **Monitoring System**: Stay updated on upcoming releases
  - Notification system for upcoming releases
  - Subscription functionality for specific series
  - Multiple notification channels (browser, email, Discord, Telegram)
- **Integration Capabilities**: 
  - Home Assistant integration with sensor data and dashboard widgets
  - Homarr integration for status information and quick access
- **Modern UI**: Responsive web interface
  - Collapsible sidebar for desktop and mobile
  - Notification system in navigation bar
  - Modern dashboard with statistics and visualizations
  - Dark/light theme toggle with persistent settings

## Installation

### Docker (Recommended)

The easiest way to run Readloom is using Docker:

```bash
# Clone the repository
git clone https://github.com/yourusername/Readloom.git
cd Readloom

# Start with Docker Compose
docker compose up -d
```

Readloom will be available at http://localhost:7227

#### Docker Compose Configuration

The default `docker-compose.yml` file includes the following configuration:

```yaml
services:
  readloom:
    build: .
    container_name: readloom
    restart: unless-stopped
    ports:
      - "7227:7227"
    volumes:
      - ./data:/config
    environment:
      - TZ=UTC
      - PYTHONUNBUFFERED=1
    command:
      - "-o"
      - "0.0.0.0"
      - "-p"
      - "7227"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### Docker Volumes

The Docker container uses the following volume:

- `./data:/config`: Stores all Readloom data, including the database, logs, and e-books

#### Docker Environment Variables

- `TZ`: Set your timezone (default: UTC)
- `PYTHONUNBUFFERED`: Ensures Python output is unbuffered for better logging

#### Docker Healthcheck

The Docker container includes a healthcheck that verifies the application is running properly. The healthcheck uses curl to check if the application is responding on port 7227.

#### Container Behavior

The Docker container is designed to keep running even if the Readloom application exits. This allows you to inspect logs and troubleshoot any issues that might cause the application to exit unexpectedly.

If you need to restart the application without restarting the container, you can use:

```bash
docker exec -it readloom python Readloom.py -d /config/data -l /config/logs -o 0.0.0.0 -p 7227
```

To view logs:

```bash
docker logs readloom
```

To access the container shell:

```bash
docker exec -it readloom /bin/bash
```

#### Troubleshooting

If you can't access Readloom at http://localhost:7227 or http://127.0.0.1:7227, try the following:

1. **Check if the container is running**:
   ```bash
   docker ps | grep readloom
   ```

2. **Check container logs**:
   ```bash
   docker logs readloom
   ```

3. **Run the debug script**:
   ```bash
   docker exec -it readloom /usr/local/bin/docker-debug.sh
   ```

4. **Check if the port is correctly mapped**:
   ```bash
   docker port readloom
   ```

5. **Try accessing with your Docker host IP**:
   If you're using Docker Desktop, try using the Docker host IP instead of localhost.
   
6. **Restart the application inside the container**:
   ```bash
   docker exec -it readloom python Readloom.py -d /config/data -l /config/logs -o 0.0.0.0 -p 7227
   ```

7. **Check firewall settings**:
   Make sure your firewall allows connections to port 7227.

### Manual Installation

#### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

#### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Readloom.git
   cd Readloom
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run Readloom:
   ```bash
   python Readloom.py
   ```

Readloom will be available at http://localhost:7227

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions
- [API Documentation](docs/API.md) - Complete API reference
- [Collections](docs/COLLECTIONS.md) - Collection-based organization system
- [Author Collection Management](docs/AUTHOR_COLLECTION_MANAGEMENT.md) - Author folder structure and book organization
- [E-book Management](docs/EBOOKS.md) - E-book organization and scanning
- [Folder Structure](docs/FOLDER_STRUCTURE.md) - Series folder organization and naming
- [Performance Tips](docs/PERFORMANCE_TIPS.md) - Optimize for large collections
- [AniList Provider](docs/ANILIST_PROVIDER.md) - AniList integration details
- [Database Schema](docs/DATABASE.md) - Database structure information
- [Changelog](docs/CHANGELOG.md) - Version history and changes
- [Codebase Structure](docs/CODEBASE_STRUCTURE.md) - Overview of the modular architecture
- [Refactoring Guide](docs/REFACTORING_GUIDE.md) - Guidelines for code refactoring
- [Metadata Providers](docs/METADATA_PROVIDERS.md) - Details on metadata provider implementation

### Volume Detection Fix

If you're experiencing incorrect volume counts for manga series:

- [Volume Fix Summary](VOLUME_FIX_FINAL_SUMMARY.md) - Complete overview of the volume detection fix
- [Adding Manga to Database](ADDING_MANGA_TO_DATABASE.md) - Guide for adding manga with accurate volume counts
- Use `python refresh_series_volumes.py --all` to update existing series

## Configuration

Readloom stores its configuration in a SQLite database. You can modify settings through the web interface at http://localhost:7227/settings.

### Calendar Settings

- `calendar_range_days`: Default number of days to show in the calendar view (default: 7)
  - Note: This only affects the initial calendar view. The calendar system stores and can display events from any date range.
  - Only upcoming releases in the next 7 days will be displayed by default.
- `calendar_refresh_hours`: How often to automatically refresh the calendar (default: 12)
  - The calendar is also automatically updated when importing new manga or modifying release dates.
- `calendar_confirmation_mode`: Controls which releases show in the calendar (default: true)
  - When enabled, only confirmed releases appear in the calendar (Sonarr/Radarr-like behavior).
  - When disabled, all predicted releases appear in the calendar.

### E-book Settings

- `ebook_storage`: Path to the e-book storage directory (default: "ebooks")
  - This can be a relative path within the data directory or an absolute path
  - E-books are organized by content type and series name within this directory
- `task_interval_minutes`: How often to scan for new e-book files (default: 60)
  - The system will automatically scan for new files at this interval
  - You can also manually trigger a scan from the series detail page

### Command Line Arguments

- `-d, --DatabaseFolder`: The folder to store the database in
- `-l, --LogFolder`: The folder to store logs in
- `-f, --LogFile`: The log file name
- `-o, --Host`: The host to bind to (default: 0.0.0.0)
- `-p, --Port`: The port to bind to (default: 7227)
- `-u, --UrlBase`: The URL base (e.g., /readloom)

## Integrations

### Home Assistant

Readloom can integrate with Home Assistant to display your manga/comic collection and upcoming releases on your dashboard.

See the [Integrations](http://localhost:7227/integrations) page in the Readloom web interface for setup instructions.

### Homarr

Readloom can integrate with Homarr to display your manga/comic collection status on your dashboard.

See the [Integrations](http://localhost:7227/integrations) page in the Readloom web interface for setup instructions.

## Development

### Project Structure

- `Readloom.py`: Main application entry point
- `backend/`: Backend code
  - `base/`: Base definitions and helpers
  - `features/`: Feature implementations
    - `calendar/`: Calendar management package
    - `collection/`: Collection tracking package
    - `home_assistant/`: Home Assistant integration package
    - `metadata_providers/`: Metadata provider packages
      - `anilist/`: AniList provider implementation
      - `jikan/`: Jikan (MyAnimeList) provider implementation
      - `mangadex/`: MangaDex provider implementation
      - `mangafire/`: MangaFire provider implementation
      - `myanimelist/`: MyAnimeList direct provider implementation
    - `metadata_service/`: Metadata service package
    - `notifications/`: Notification system package
    - `scrapers/`: Web scraping services
      - `mangainfo/`: Multi-source manga information provider
  - `internals/`: Internal components (database, server, settings)
- `frontend/`: Frontend code
  - `api.py`: API endpoints
  - `api_metadata_fixed.py`: Metadata provider endpoints
  - `api_downloader.py`: Downloader API endpoints
  - `image_proxy.py`: Image proxy functionality
  - `ui.py`: UI routes
  - `templates/`: HTML templates
  - `static/`: Static files (CSS, JS, images)
- **Utility Scripts** (in `fix and test` directory):
  - Volume Management:
    - `refresh_all_volumes.py`: Batch update all manga volumes
    - `update_manga_volumes.py`: Fix volumes for specific manga
    - `fix_manga_volumes.py`: Fix volumes for known manga series
  - Testing and Diagnostics:
    - `test_volume_scraper.py`: Test volume detection
    - `check_series_volumes.py`: Check volumes for specific manga
    - `debug_anilist_chapters.py`: Debug AniList chapter information
  - Content Management:
    - `add_chapter.py`: Add test chapters
    - `add_series_and_volumes.py`: Create test series with volumes

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Copyright Notice

Readloom is a library management tool designed to help you organize and track digital media files you own or have legal rights to access.

**Important:**
- Readloom does not provide, host, or distribute any copyrighted content
- Users are solely responsible for ensuring they have legal rights to any files they manage with Readloom
- Readloom is intended for personal, non-commercial use
- We do not condone or support piracy in any form

Please respect copyright laws and support content creators by purchasing legal copies of manga, comics, and books.

For more details, see [LEGAL.md](LEGAL.md).

## License

Readloom is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
