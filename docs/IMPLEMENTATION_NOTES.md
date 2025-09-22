# Implementation Notes: Collection System and E-book Scanning

This document provides technical details about the implementation of the collection system and e-book scanning improvements in MangaArr v0.0.7.

## Collection System Implementation

### Database Schema

The collection system is implemented with the following database tables:

1. **collections**: Stores collection metadata
   - `id`: Primary key
   - `name`: Collection name
   - `description`: Optional description
   - `is_default`: Flag for the default collection
   - `created_at`, `updated_at`: Timestamps

2. **root_folders**: Stores root folder information
   - `id`: Primary key
   - `path`: Filesystem path
   - `name`: Display name
   - `content_type`: Primary content type (MANGA, COMICS, etc.)
   - `created_at`, `updated_at`: Timestamps

3. **collection_root_folders**: Many-to-many relationship between collections and root folders
   - `id`: Primary key
   - `collection_id`: Foreign key to collections
   - `root_folder_id`: Foreign key to root_folders
   - `created_at`, `updated_at`: Timestamps

4. **series_collections**: Many-to-many relationship between series and collections
   - `id`: Primary key
   - `series_id`: Foreign key to series
   - `collection_id`: Foreign key to collections
   - `created_at`, `updated_at`: Timestamps

### Core Components

1. **Collection Management**
   - `backend/features/collection/collections.py`: Core functions for managing collections
   - `backend/features/collection/collections_schema.py`: Database schema setup
   - `frontend/api_collections.py`: API endpoints for collection management

2. **Setup Wizard**
   - `frontend/templates/setup_wizard.html`: UI for the setup wizard
   - `frontend/ui.py`: Route for the setup wizard
   - `backend/features/setup_check.py`: Check if setup is complete

3. **Middleware**
   - `frontend/middleware.py`: Decorators to enforce setup requirements
     - `setup_required`: Checks both collections and root folders
     - `collections_required`: Checks only collections
     - `root_folders_required`: Checks only root folders

### Migration Path

For existing installations, a migration script (`backend/migrations/0005_add_collections_and_root_folders.py`) handles:
1. Creating the new tables
2. Creating a default collection
3. Migrating existing root folders from settings to the database
4. Linking root folders to the default collection
5. Adding existing series to the default collection

## E-book Scanning Improvements

### Key Changes

1. **Enhanced Logging**
   - Added detailed logging throughout the scanning process
   - Log messages for each step of the scanning process
   - Better error reporting for troubleshooting

2. **Improved File Detection**
   - Better handling of file paths and extensions
   - More robust comparison of file paths
   - Improved volume number extraction from filenames

3. **Automatic Scanning for Existing Folders**
   - When importing a series, check if the folder already exists
   - If folder exists, automatically scan for e-books
   - Return information about found e-books in the API response

4. **Folder Path Handling**
   - Better normalization of file paths
   - Improved handling of spaces and special characters
   - More robust folder existence checks

### Implementation Details

1. **Scan Process**
   - `backend/features/ebook_files.py`: Updated `scan_for_ebooks` function
   - Added more debug logging
   - Improved file detection logic

2. **Import Process**
   - `backend/features/metadata_service/facade.py`: Updated `import_manga_to_collection` function
   - Added folder existence check
   - Added automatic scanning for existing folders

3. **API Enhancements**
   - `frontend/api_metadata_fixed.py`: Updated `api_import_manga` function
   - Added folder path and e-book count to API responses
   - Better handling of existing series

## Setup Requirement Implementation

1. **Startup Check**
   - `backend/features/setup_check.py`: Checks if setup is complete on startup
   - Verifies collections exist
   - Verifies root folders exist and are valid

2. **Middleware**
   - `frontend/middleware.py`: Added decorators to enforce setup requirements
   - Redirects to setup wizard if requirements not met
   - Returns appropriate error responses for API calls

3. **UI Integration**
   - Updated routes to use the new middleware
   - Added setup wizard route
   - Modified dashboard to check setup status

## Testing Notes

1. **Collection System**
   - Test creating, updating, and deleting collections
   - Test linking collections to root folders
   - Test adding series to collections

2. **E-book Scanning**
   - Test scanning with various file types (PDF, EPUB, CBZ, etc.)
   - Test scanning existing folders with different naming patterns
   - Test volume number extraction from different filename formats

3. **Setup Wizard**
   - Test the complete setup flow
   - Test with invalid paths
   - Test with existing collections and root folders

## Known Limitations

1. **Collection System**
   - Default collection cannot be deleted
   - Series must belong to at least one collection

2. **E-book Scanning**
   - Some complex filename patterns may not be correctly parsed
   - Very large folders may take time to scan

3. **Setup Wizard**
   - Limited validation for root folder paths
   - No support for network paths in some environments
