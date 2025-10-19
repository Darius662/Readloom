# Changelog

All notable changes to Readloom will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.6] - 2025-10-19

### Added
- **JavaScript Files for Collections**:
  - Added missing `collection.js` for collection view functionality
  - Added missing `collections.js` for collections list functionality
  - Fixed 404 errors when accessing collection pages
- **Enhanced Author Search**:
  - Added author metadata API endpoint for detailed author information
  - Implemented specialized author cards in search results
  - Added comprehensive author details modal with biography, birth/death dates, and external links
  - Added support for OpenLibrary author photos and metadata

### Fixed
- **Root Folders Detection**:
  - Added API endpoint `/api/rootfolders/check-configured` to check if root folders are configured
  - Implemented JavaScript-based root folders detection in dashboard and series pages
  - Fixed issue where root folders warning was showing even when root folders were configured
  - Added localStorage flag to communicate root folder updates between pages
- **Search Functionality**:
  - Fixed provider/indexer dropdown in search forms
  - Implemented proper filtering of providers based on content type (books vs. manga)
  - Fixed search type selection to properly handle title and author searches
  - Corrected content type selector links in search templates

### Changed
- **Search Functionality**:
  - Removed Book Collections and Authors sections from search
  - Redesigned search page to match original clean layout
  - Kept content type selector while removing sidebar
  - Created unified search template for both Books and Manga
  - Enhanced author search to display proper author information instead of book covers
  - Improved search results presentation with better visual distinction between books and authors
- **Books Tab UI**:
  - Removed Book Collections and Authors sections from the Books tab sidebar
  - Added Search Box and Quick Actions to the sidebar instead
  - Streamlined the Books tab interface for better user experience

## [0.1.5] - 2025-10-18

### Added
- **Content Type System**:
  - Added comprehensive content type system with service factory pattern
  - Implemented `ContentType` enum for better type safety
  - Created `BookService` and `MangaService` classes for content-specific operations
  - Added helper functions to determine content type from metadata

### Changed
- **UI Blueprint Structure**:
  - Reorganized UI routes into content-specific and shared blueprints
  - Created comprehensive UI blueprint (`ui_complete.py`) that includes all routes
  - Updated route handlers to pass necessary context variables to templates

## [0.1.4] - 2025-10-15

### Added
- **Book-specific Features**:
  - Added author-based organization for books
  - Implemented book search by author name
  - Created author detail pages with book listings
  - Added book-specific templates and routes

### Changed
- **Database Schema**:
  - Added `is_book` column to series table
  - Created authors table and book_authors relationship table
  - Updated migration system to handle schema changes
  - Added content type detection from metadata

## [0.1.3] - 2025-10-10

### Added
- **Hybrid UI Implementation**:
  - Added content type tabs to dashboard
  - Implemented dynamic content loading based on selected tab
  - Created separate book and manga home pages
  - Added API endpoints for content-specific operations

### Changed
- **Series API**:
  - Updated series API to support filtering by content type
  - Added content type parameter to search endpoints
  - Modified series list to show appropriate content based on type

## [0.1.2] - 2025-10-04

### Added
- **Collections Manager**:
  - Link Root Folder button and modal in `Collections Manager` collection details
  - Modal lists only unlinked root folders for the selected collection
  - Frontend wiring to `POST /api/collections/{id}/root-folders/{root_folder_id}` and auto-refresh of the table
- **API Documentation**:
  - Documented `GET /api/collections/default` endpoint usage across the app
- **Expanded Content Types in UI**:
  - `frontend/templates/search.html` (Import modal) and `frontend/templates/series_list.html` (Add Series) now support: Manga, Manhwa, Manhua, Comics, Novel, Book, Other.
  - Implemented subtype-to-bucket mapping function to group these under collection buckets: `MANGA` (Manga/Manhwa/Manhua), `COMIC` (Comics), `BOOK` (Book/Novel/Other).
- **Root Folder Selection**:
  - Visible Root Folder selector added to both flows, populated from the auto-selected default collection for the chosen bucket.
  - Users can optionally choose a specific root folder when a collection has multiple.
 - **Series Move API**:
  - Added `POST /api/series/{id}/move` to move a series between collections within the same bucket (DB-only, no file moves yet).
  - Returns a summary of before/after collection memberships and whether a change occurred.
  - **Series Move Feature**:
  - Backend:
    - Added [move_service.py](cci:7://file:///c:/Users/dariu/Documents/GitHub/Readloom/backend/features/move_service.py:0:0-0:0) with full move operation support (DB + filesystem)
    - Dry-run mode to preview moves before executing
    - Bucket compatibility validation (MANGA/COMIC/BOOK)
  - API:
    - Extended `POST /api/series/{id}/move` endpoint with:
      - `target_collection_id` (required)
      - `target_root_folder_id` (optional)
      - `move_files` flag for physical moves
      - `clear_custom_path` option
      - `dry_run` mode
  - UI:
    - Added Move button in series header and Quick Actions
    - Interactive Move dialog with collection/folder selectors
    - Dry-run preview panel showing paths and conflicts
    - Safety checks to prevent destructive overwrites

### Fixed
- **Default Collection Handling**:
  - Ensured only one default collection is treated as active throughout UI flows
  - Consistent Default badge display in Collections Manager
  - Safer delete behavior for default collection and clearer UX around default selection
- **UnboundLocalError in folder path endpoint**:
  - `frontend/api.py`: removed inner import shadowing of `execute_query` and moved `Path` import to top-level to fix "cannot access local variable 'execute_query'" error in `get_series_folder_path()`.

### Changed
- **Docs**:
  - Updated `docs/COLLECTIONS.md` with the new Link Root Folder workflow and troubleshooting
  - Added `docs/LINK_ROOT_FOLDER.md` guide
- **Simplified Collection Selection UX**:
  - Collection selector is now hidden in both Import and Add Series flows and auto-selected to the single default collection per bucket.
  - Import/Add requests now include `content_type` (the selected subtype), resolved `collection_id` (default per bucket), and optional `root_folder_id`.
- **Type Inference on Details Modal**:
  - Light heuristics added in `search.html` to pre-select a sensible content subtype based on title/genres/description.

## [0.1.1-1] - 2025-10-02

### Added
- **Legal Documentation**:
  - Added comprehensive LEGAL.md file with copyright policy and terms of use
  - Added copyright notice section to README.md
  - Added copyright notice card to About page in UI
  - Clarified that Readloom is a management tool, not a content distribution platform
  - Outlined legitimate use cases and user responsibilities
  
### Fixed
- **Docker Volume Mounting**:
  - Fixed docker-compose.yml to mount data folder to `/config` instead of `/data`
  - Database and logs now properly persist in the mounted volume
  - Previously data was written to `/config/data` inside container (not persisted)

## [0.1.1] - 2025-10-01

### Added
- Helper scripts for volume management:
  - `add_manga_to_database.py` - Interactive tool to add manga to static database
  - `refresh_series_volumes.py` - Update existing series with correct volume counts
  - `test_volume_fix.py` - Test volume detection accuracy
  - `test_problematic_titles.py` - Test specific problematic titles
  - `debug_specific_titles.py` - Debug volume detection for any title
- Comprehensive documentation:
  - `VOLUME_FIX_FINAL_SUMMARY.md` - Complete overview of the fix
  - `ADDING_MANGA_TO_DATABASE.md` - Guide for adding manga to static database
  - `VOLUME_FIX_SUMMARY.md` - Initial fix documentation
  - `VOLUME_FIX_UPDATE.md` - Alias support documentation
- **Smart Caching System** - Implemented comprehensive volume detection caching:
  - Database cache table (`manga_volume_cache`) for persistent storage
  - Dynamic static database (auto-populating JSON file)
  - Memory cache for session-based performance
  - Automatic cache refresh (30 days for ongoing, 90 days for completed manga)
  - Migration system integration for automatic table creation
- **Improved MangaDex API Integration**:
  - Better search matching (top 5 results, prefer manga over doujinshi)
  - Uses `lastVolume` and `lastChapter` attributes when available
  - Removes language filter for complete volume data
  - Filters out 'none' volumes for accurate counts
- **Fixed MangaFire Scraper**:
  - Changed from broken `/search?q=` to working `/filter?keyword=` endpoint
  - Updated selector from `.manga-card` to `.unit` (correct class)
  - Added language dropdown parsing for volume counts (e.g., "English (32 Volumes)")
  - Now correctly detects volumes for most manga on MangaFire

### Fixed
- **Critical: Volume Detection System Overhaul**:
  - Fixed scraper not being called during volume creation in `get_manga_details()`
  - Resolved duplicate `"volumes"` key conflict in AniList provider
  - Fixed MangaFire scraper failing due to outdated search endpoint
  - Fixed MangaDex returning incomplete data for some manga
  - Added migration call to `Readloom_direct.py` for automatic table creation
  - Volume counts now accurate for most manga:
    - Blue Exorcist: 32 volumes ✓
    - D.Gray-man: 30 volumes ✓
    - Fire Force: 34 volumes ✓
    - One Piece: 115 volumes ✓
    - One Punch Man: 29 volumes ✓
    - Attack on Titan: 34 volumes ✓
- **Volume Format Update API**:
  - Fixed `digital_format` parameter being passed to functions that don't accept it
  - Removed invalid parameter from `add_to_collection()` call
  - Removed invalid parameter from `update_collection_item()` call
  - Volume format changes (Physical ↔ Digital) now work correctly
- **Migration System**:
  - Fixed migration 0004 to use `migrate()` instead of `run_migration()`
  - Docker containers now start correctly without migration errors

### Changed
- AniList provider now calls scraper in `get_manga_details()` for accurate volume counts
- Renamed duplicate `"volumes"` key to `"volume_count"` (integer) and `"volumes"` (list)
- Updated `get_chapter_list()` to use `volume_count` from manga details
- Expanded static database from 25 to 27 manga entries with aliases
- Enhanced scraper matching logic to support alternative titles
- Updated volume format API to only use valid parameters (`format` only, removed `digital_format`)

## [0.1.0] - 2025-09-27

### Added
- Enhanced Docker support:
  - Added comprehensive Docker Hub publishing documentation
  - Created optimized .dockerignore file for smaller image sizes
  - Added Docker Hub README template for repository description
  - Updated Docker documentation with Docker Hub usage instructions

## [0.0.9] - 2025-08-15

### Added
- Generalized application terminology:
  - Added support for more book-related metadata providers (Google Books, Open Library, ISBNdb, WorldCat)
- Added comprehensive UI documentation:
  - Created new UI_STRUCTURE.md documentation file
  - Updated codebase structure documentation to include frontend
  - Added detailed descriptions of UI components and patterns

### Changed
- Generalized application terminology:
  - Updated UI references from "manga" to "e-book" throughout the application
  - Enabled Google Books by default as the recommended provider for books due to its more accurate metadata
  - Made the application more suitable for all types of e-books, not just manga/comics
- Improved UI organization and navigation:
  - Moved Root Folders management into Collections Manager for unified experience
  - Relocated Integrations into Settings page as a new tab
  - Streamlined sidebar navigation by removing redundant tabs
  - Enhanced Settings page with better tab organization
  - Made E-book Management section collapsible with quick actions
  - Repositioned Edit Series button to top-right corner as icon-only button
- Modified default metadata provider settings:
  - Only AniList provider enabled by default
  - Disabled MyAnimeList, MangaDex, MangaFire, Jikan, and MangaAPI by default
  - Improved initial performance by reducing API calls
- Enhanced Series Detail page:
  - Moved Custom Path import functionality to Edit Series modal
  - Made E-book Management section collapsible to reduce visual clutter
  - Added quick action for scanning e-books without expanding details
  - Improved overall page layout and information hierarchy


### Fixed
- Critical issues in Readloom_direct.py:
  - Added metadata service initialization to ensure database tables are created
  - Added setup check to ensure the application is properly initialized
  - Fixed Flask app creation with correct static folder path configuration
  - Properly registered all required blueprints
  - Fixed missing OS imports
  - Ensured proper static file serving for JavaScript and CSS files
  - Fixed Setup Wizard functionality when running in direct mode
- Docker container issues:
  - Added missing iproute2 package for the ip command
  - Added net-tools package for netstat command
  - Removed deprecated version attribute from docker-compose.yml
  - Added comprehensive Docker documentation

## [0.0.8] - 2025-07-02
### Added
- Folder validation functionality across the application:
  - Added validation to check if folders exist and are writable
  - Added ability to create folders directly from the UI
  - Implemented in Root Folders tab, Collection Manager, and Setup Wizard
  - Reusable JavaScript component for consistent behavior
- New API endpoints for folder validation and creation
- Backend utilities for folder validation with proper error handling
- Implemented custom path feature for series:
  - Added ability to set a custom folder path for each series
  - Files are used directly from custom path without copying
  - Custom path validation with folder creation option
  - Integrated into the Edit Series form
- Implemented robust database migration system:
  - Added framework for tracking and applying migrations
  - Created migration scripts for schema changes
  - Automatic migration application during startup
  - Improved database versioning and upgrade path
- Enhanced folder validation system:
  - Added centralized folder validation utilities
  - Improved error handling for file system operations
  - Added ability to create folders with proper permissions
  - Consistent validation across all parts of the application

### Changed
- Completely redesigned collections management approach:
  - Removed automatic creation of "Default Collection"
  - Now users create their own collections from scratch
  - Any collection can be marked as default by the user
  - Improved setup wizard to guide users through collection creation
- Improved project organization and structure:
  - Moved utility and debug scripts to 'fix and test' folder
  - Cleaned up root directory for better maintainability
  - Updated documentation to reflect new script locations
- Improved API organization and structure:
  - Added dedicated API endpoints for folder operations
  - Better separation of concerns between API modules
  - Enhanced error handling and response formatting
  - More consistent API naming conventions

### Fixed
- Fixed collections management issues:
  - Resolved issue with duplicate Default Collections being created on restart
  - Added database constraint to prevent multiple default collections
  - Added proper migration system to handle database schema updates
  - Improved collection initialization logic
- Fixed API request issues:
  - Added proper Content-Type header to AJAX requests
  - Fixed 415 Unsupported Media Type errors when importing manga
  - Ensured consistent JSON data handling across all API endpoints
- Fixed static file serving configuration:
  - Corrected static folder paths in Flask application
  - Ensured consistent static URL paths across blueprints
  - Fixed 404 errors for JavaScript files


## [0.0.7] - 2025-05-18

### Fixed
- Fixed collections management issues:
  - Improved error handling in collections management
  - Added cleanup script to fix collection database issues
  - Enhanced collection-root folder relationship management
  - Fixed delete functionality for collections and root folders
- UI improvements:
  - Renamed "Collection" tab to "Library" for clarity
  - Added Collections Manager for managing multiple collections
  - Improved UI feedback when performing collection operations
  - Enhanced error handling and debugging in JavaScript functions

## [0.0.6] - 2025-03-25

### Fixed
- Fixed folder structure creation issues:
  - Corrected LOGGER import in the `import_manga_to_collection` function
  - Fixed LOGGER import in the `api_import_manga` function
  - Ensured proper folder name sanitization while preserving spaces
  - Fixed README file creation in series folders
  - Improved error handling during folder creation
- Enhanced folder name sanitization:
  - Only replaces characters that are invalid in file names
  - Preserves spaces and most special characters for better readability
  - Properly handles question marks and other problematic characters
- Fixed metadata provider search issues with special characters

### Added
- Collection-based organization system:
  - Added collections to organize manga/comics into groups
  - Collections can be linked to multiple root folders
  - Series can belong to multiple collections
  - Setup wizard for first-time users to create collections and root folders
  - Required setup check on application startup
- Improved e-book scanning:
  - Automatic scanning of existing folders when importing series
  - Better detection of CBZ files in existing folders
  - Enhanced logging for troubleshooting scanning issues

### Changed
- Application now requires at least one collection and one root folder before use
- Updated API endpoints to enforce setup requirements
- Import process now includes information about existing folders and e-books

## [0.0.5] - 2025-01-30

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

## [0.0.4] - 2024-12-12

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

## [0.0.3] - 2024-10-28

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

## [0.0.2] - 2024-09-15

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

## [0.0.1] - 2024-07-27

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
