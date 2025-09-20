# MangaArr

MangaArr is a manga, manwa, and comics collection manager with a focus on release tracking and calendar functionality. It follows the design principles of the *arr suite of applications but with a specialized focus on manga and comics.

![MangaArr Dashboard](frontend/static/img/screenshot.png)

## Features

- **Enhanced Release Calendar**: Interactive calendar showing manga/comic releases
  - Sonarr/Radarr-like calendar showing only upcoming confirmed releases
  - Complete historical and future release date tracking
  - Filter options for manga/comics by type and series
  - Different view modes (month, week, list)
  - Color coding for different types of releases
  - Add releases to collection directly from calendar
  - Automatic calendar updates when importing manga
- **Comprehensive Collection Tracking**: Track your manga/comic collection
  - Track ownership status, read status, and purchase details
  - Collection statistics and visualizations
  - Import/export functionality
- **External Source Integration**: Connect to popular manga sources
  - AniList integration with intelligent release date prediction
  - MyAnimeList (MAL) integration for metadata and searching
  - MangaDex integration for searching and importing manga
  - Multi-source accurate chapter counting system
  - Search interface for finding manga across multiple sources
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

The easiest way to run MangaArr is using Docker:

```bash
# Clone the repository
git clone https://github.com/yourusername/MangaArr.git
cd MangaArr

# Start with Docker Compose
docker-compose up -d
```

MangaArr will be available at http://localhost:7227

### Manual Installation

#### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

#### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MangaArr.git
   cd MangaArr
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run MangaArr:
   ```bash
   python MangaArr.py
   ```

MangaArr will be available at http://localhost:7227

## Configuration

MangaArr stores its configuration in a SQLite database. You can modify settings through the web interface at http://localhost:7227/settings.

### Calendar Settings

- `calendar_range_days`: Default number of days to show in the calendar view (default: 7)
  - Note: This only affects the initial calendar view. The calendar system stores and can display events from any date range.
  - Only upcoming releases in the next 7 days will be displayed by default.
- `calendar_refresh_hours`: How often to automatically refresh the calendar (default: 12)
  - The calendar is also automatically updated when importing new manga or modifying release dates.
- `calendar_confirmation_mode`: Controls which releases show in the calendar (default: true)
  - When enabled, only confirmed releases appear in the calendar (Sonarr/Radarr-like behavior).
  - When disabled, all predicted releases appear in the calendar.

### Command Line Arguments

- `-d, --DatabaseFolder`: The folder to store the database in
- `-l, --LogFolder`: The folder to store logs in
- `-f, --LogFile`: The log file name
- `-o, --Host`: The host to bind to (default: 0.0.0.0)
- `-p, --Port`: The port to bind to (default: 7227)
- `-u, --UrlBase`: The URL base (e.g., /mangarr)

## Integrations

### Home Assistant

MangaArr can integrate with Home Assistant to display your manga/comic collection and upcoming releases on your dashboard.

See the [Integrations](http://localhost:7227/integrations) page in the MangaArr web interface for setup instructions.

### Homarr

MangaArr can integrate with Homarr to display your manga/comic collection status on your dashboard.

See the [Integrations](http://localhost:7227/integrations) page in the MangaArr web interface for setup instructions.

## Development

### Project Structure

- `MangaArr.py`: Main application entry point
- `backend/`: Backend code
  - `base/`: Base definitions and helpers
  - `features/`: Feature implementations
  - `internals/`: Internal components (database, server, settings)
- `frontend/`: Frontend code
  - `api.py`: API endpoints
  - `ui.py`: UI routes
  - `templates/`: HTML templates
  - `static/`: Static files (CSS, JS, images)

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MangaArr is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
