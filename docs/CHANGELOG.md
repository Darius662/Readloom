# Changelog

All notable changes to MangaArr will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.5] - 2025-09-21

### Added
- Comprehensive e-book management system
  - Organized folder structure by content type and series name
  - Automatic volume number detection from filenames
  - Support for multiple e-book formats (PDF, EPUB, CBZ, CBR, MOBI, AZW)
  - Periodic scanning for new files
  - Manual scan button in the UI
  - Collection integration with digital format tracking
  - Detailed documentation for e-book management
- Enhanced file organization
  - Content type categorization (MANGA, MANHWA, MANHUA, COMICS, NOVEL, BOOK, OTHER)
  - Human-readable folder names based on series titles
  - Automatic folder creation when adding new series
  - README files in each series folder with metadata
- Database schema updates
  - Added `content_type` field to series table
  - Created `ebook_files` table for tracking e-book files
  - Extended `collection_items` table with digital format tracking
  - Added foreign key constraints for e-book files
- Utility scripts for e-book management
  - `create_content_type_dirs.py` - Create content type directories
  - `create_missing_folders.py` - Create folders for all series
  - `create_series_folder.py` - Create folder for a specific series
  - `test_folder_scan.py` - Test e-book scanning functionality
- Periodic task system for background operations
  - Configurable scan interval for e-book files
  - Automatic collection updates when new files are found

## [0.0.4] - 2025-09-20

### Added
- Improved metadata provider support
  - Better handling of null chapter numbers
  - Enhanced release date extraction from providers
  - Fixed caching issues with metadata providers
  - Added image proxy for external images to handle CORS issues
- Foreign key constraints for better data integrity
  - Calendar events now automatically deleted when series are removed
  - Volume events deleted when volumes are removed
  - Chapter events deleted when chapters are removed
- SQLite foreign key support enabled by default
- Improved database schema documentation
- Enhanced calendar functionality
  - Removed date range restrictions to show all release dates
  - Improved handling of historical release dates
  - Fixed chapter release date display in calendar
- Major performance improvements for manga imports
  - Series-specific calendar updates instead of full collection scans
  - Enhanced MangaFire scraper with improved volume detection
  - Added multiple fallback methods for manga search
  - Implemented better error handling for API failures
- Added robust volume detection system
  - Multiple scraping sources for accurate volume data
  - Enhanced pattern matching to find volume information
  - Automatic volume generation when provider data is missing
- Improved distribution of volume release dates
  - Intelligent spacing based on publication schedule
  - More realistic release patterns
- Utility scripts for bulk operations
  - `refresh_all_volumes.py` - Batch update volumes for all manga
  - `update_manga_volumes.py` - Update volumes for specific manga
  - `test_volume_scraper.py` - Test volume scraping functionality
- Added AniList API integration as a new metadata provider
  - Complete manga search functionality
  - Detailed manga information retrieval
  - Chapter list generation with release dates
  - Support for manga recommendations
- Implemented intelligent publication schedule detection
  - Different manga types follow their actual publication patterns
  - Weekly Shonen Jump titles release on Mondays
  - Monthly seinen magazines release on Thursdays
  - Korean manhwa release on Wednesdays
- Multi-source accurate chapter counting system
  - Web scraping for hard-to-find chapter counts
  - Static database of popular manga series with accurate counts
  - Smart chapter count estimation for unknown series
  - Adaptive release date generation based on publication schedules
- Added confirmed release flags for Sonarr/Radarr-like calendar
  - Calendar now only shows upcoming releases within 7 days
  - Past chapters marked as confirmed historical data
  - Future predicted chapters marked as unconfirmed
  - Better display of release patterns

### Changed
- Updated metadata service to handle different provider return formats
- Improved error handling for manga imports
- Modified calendar event cleanup to preserve historical events
- Updated database initialization to include foreign key constraints
- Modified calendar event cleanup to use cascading deletes

### Fixed
- Fixed metadata cache type parameter issue
- Fixed database constraints for chapter numbers
- Improved handling of 'already exists' cases during manga import
- Fixed issue with release dates not appearing in calendar
- Fixed issue with orphaned calendar events after series deletion
- Improved error handling for database constraints
- Fixed MangaDex cover images not displaying properly due to incorrect URL construction
- Fixed missing fallback image for manga covers
- Added image proxy to handle CORS issues with external images
- Updated all templates (search, series list, series details, collection, dashboard) to use image proxy
- Embedded image proxy utility function directly in base template for global availability
- Fixed fallback image paths to work correctly with Flask blueprint system

## [0.0.3] - 2025-09-19

### Added
- Improved documentation structure
- API documentation with endpoint descriptions and examples
- Installation guide with Docker and manual options
- Contributor guidelines and code of conduct
- External manga source integration:
  - MangaFire integration for searching and importing manga
  - MyAnimeList (MAL) integration for metadata and searching
  - Manga-API integration for additional manga sources
  - Search interface for finding manga across multiple sources
  - Import functionality to add manga from external sources to collection
  - Metadata caching system for improved performance
  - Provider configuration UI for customizing API keys and settings

### Changed
- Updated development workflow for better compatibility
- Simplified package requirements for easier installation

### Improved
- Enhanced search capabilities across the application
- Better metadata handling with external providers
- More comprehensive manga details from multiple sources
- Fixed logging to properly write to data/logs folder
- Improved settings persistence between application restarts
- Updated MangaAPI provider to use correct API endpoints
- Added fallback to latest updates when search returns no results

## [0.0.2] - 2025-09-18

### Added
- Enhanced interactive release calendar
  - Filter options for manga/comics by type and series
  - Different view modes (month, week, day)
  - Color coding for different types of releases
  - Improved event details modal
  - Add releases to collection directly from calendar
- Comprehensive manga/comic collection tracking
  - Track ownership status, read status, and purchase details
  - Collection statistics and visualizations
  - Import/export functionality
- Monitoring system for upcoming releases
  - Notification system for upcoming releases
  - Subscription functionality for specific series
  - Multiple notification channels (browser, email, Discord, Telegram)
  - Real-time notification updates
- Home Assistant integration
  - API endpoint for Home Assistant
  - Sensor data for dashboards
  - Setup instructions and configuration examples
- Homarr integration
  - API endpoint for Homarr
  - Status information for dashboards
  - Setup instructions and configuration examples
- Modern, responsive web interface
  - Redesigned base template
  - Collapsible sidebar for desktop and mobile
  - Notification system in navigation bar
  - Modern dashboard with statistics and visualizations
  - Dark/light theme toggle with persistent settings

### Changed
- Complete UI overhaul with responsive design
- Improved database schema for better data organization
- Enhanced API endpoints with better error handling
- Optimized performance for large collections

## [0.0.1] - 2025-09-18

### Added
- Initial project structure and architecture
- Database schema for manga/comic tracking
- Basic API endpoints structure
- Simple web interface with "Coming Soon" page
- Test data generator for development
- Development environment setup script
- Docker configuration for containerization
- Basic documentation framework
- Home Assistant and Homarr integration templates

### Changed
- N/A (Initial release)

### Deprecated
- N/A (Initial release)

### Removed
- N/A (Initial release)

### Fixed
- N/A (Initial release)

### Security
- N/A (Initial release)

## How to Use This Changelog

Each version should:

- List its release date in YYYY-MM-DD format.
- Group changes to describe their impact on the project, as follows:
  - **Added** for new features.
  - **Changed** for changes in existing functionality.
  - **Deprecated** for soon-to-be removed features.
  - **Removed** for now removed features.
  - **Fixed** for any bug fixes.
  - **Security** in case of vulnerabilities.

## Release Process

1. Update the changelog with all relevant changes under the "Unreleased" section.
2. When ready to release, move the "Unreleased" changes to a new version section.
3. Tag the release in Git:
   ```bash
   git tag -a v1.2.3 -m "Release v1.2.3"
   git push origin v1.2.3
   ```
4. Create a new GitHub release with the same version number.
5. Include the changelog entries in the release notes.

## Contact

If you have questions about the changelog or release process, please contact the project maintainers.
