# E-book Management in Readloom

This document describes the e-book management functionality in Readloom, including folder structure, file scanning, and collection integration.

## Overview

Readloom supports managing e-book files for your manga/comic collection. It organizes files by series name, automatically detects volume numbers from filenames, and integrates with your collection tracking.

In version 0.0.7, the e-book scanning functionality has been significantly improved with better detection of files in existing folders and automatic scanning when importing series.

## Folder Structure

E-books are organized directly in root folders that are linked to collections. Each collection can have multiple root folders, and each root folder can be linked to multiple collections:

```
/your/root/folder/
├── Series Name 1/
│   ├── README.txt
│   ├── Volume 1.pdf
│   └── Volume 2.epub
├── Series Name 2/
│   ├── README.txt
│   └── Volume 1.cbz
└── ...
```

Each series folder contains:
- A README.txt file with series information (including series ID, type, and creation date)
- E-book files for each volume

### Custom Paths

As of version 0.0.9, you can set a custom path for each series. This allows you to use your existing folder structure without having to move files to the Readloom-managed folders. To set a custom path:

1. Go to the series detail page
2. Click on "Edit Series"
3. Enter the custom path in the "Custom Path" field
4. Click "Validate" to verify the path exists
5. Click "Save Series"

When a custom path is set, Readloom will:
- Use that path directly for e-book files instead of the default folder
- Not copy files from the custom path to the default folder
- Display the custom path in the series detail page

This is particularly useful if you already have an organized collection of e-books and don't want to duplicate files.

### Folder Naming

Readloom preserves spaces and most special characters in folder names for better readability. Only characters that are invalid in file names are replaced:

- `?` is replaced with `_` (question mark)
- `*` is replaced with `_` (asterisk)
- `/` is replaced with `_` (forward slash)
- `\` is replaced with `_` (backslash)
- `<` is replaced with `_` (less than)
- `>` is replaced with `_` (greater than)
- `:` is replaced with `_` (colon)
- `"` is replaced with `_` (double quote)
- `|` is replaced with `_` (pipe)

This ensures that folder names remain as close as possible to the original series titles while still being valid file system paths.

## Content Types

Readloom tracks the following content types in its database:

- MANGA: Japanese comics
- MANHWA: Korean comics
- MANHUA: Chinese comics
- COMICS: Western comics
- NOVEL: Light novels or text-based stories
- BOOK: Regular books
- OTHER: Other types of content

While content types are stored in the database and used for filtering and organization in the UI, they no longer correspond to separate directories in the file system.

## Supported File Formats

Readloom supports the following e-book formats:

- PDF (.pdf)
- EPUB (.epub)
- Comic Book ZIP (.cbz)
- Comic Book RAR (.cbr)
- Mobipocket (.mobi)
- Amazon Kindle (.azw, .azw3)

## File Naming Conventions

Readloom automatically extracts volume numbers from filenames using various patterns:

- `Volume_1.pdf`, `Volume 1.pdf`
- `Vol_1.epub`, `Vol 1.epub`
- `v1.cbz`, `v.1.cbz`
- Simple numbers like `1.pdf`
- Decimal numbers like `1.5.pdf`
- Various formats like `tome 1`, `chapter 1`, `#1`

## Adding E-book Files

There are two ways to add e-book files to your collection:

### 1. Manual Placement

1. Navigate to the appropriate series folder: `data/ebooks/CONTENT_TYPE/SERIES_NAME/`
2. Copy or move your e-book files into this folder
3. Use the "Scan for E-books" button on the series detail page to detect the files
4. The system will automatically extract volume numbers and update your collection

### 2. Through the UI

1. Go to the series detail page
2. Click on the "Add E-book" button
3. Select the file from your computer
4. The system will copy the file to the appropriate folder and update your collection

## Automatic Scanning

Readloom provides several ways to scan for e-book files:

### Periodic Scanning

Readloom periodically scans for new e-book files in the background. The scan interval can be configured in the settings.

### Manual Scanning

You can manually trigger a scan from:
- The series detail page (scans just that series)
- The E-books page (scans all series)

### Import-time Scanning

When you import a series from a metadata provider, Readloom automatically:
1. Checks if a folder for the series already exists in any of your root folders
2. If found, automatically scans the folder for e-book files
3. Adds any found e-books to your collection

This makes it easy to import series that you already have files for.

## Collection Integration

E-books are now fully integrated with the new collection system in v0.0.7:

### When an e-book file is detected:

1. The system checks if a collection item exists for the volume
2. If it exists, it updates the item with the digital format and file information
3. If it doesn't exist, it creates a new collection item with ownership status "OWNED"
4. The format is set to "DIGITAL" or "BOTH" (if you already own a physical copy)
5. The series is added to the collection associated with the root folder where the file was found

### When importing a series:

1. The series is added to the specified collection (or the default collection)
2. If a folder for the series already exists, it's automatically scanned for e-books
3. Any found e-books are added to your collection
4. The API response includes information about the folder and any e-books found

## Database Schema

E-book files are stored in the `ebook_files` table:

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

The `collection_items` table has been extended with:

```sql
digital_format TEXT CHECK(digital_format IN ('PDF', 'EPUB', 'CBZ', 'CBR', 'MOBI', 'AZW', 'NONE')),
has_file INTEGER DEFAULT 0,
ebook_file_id INTEGER REFERENCES ebook_files(id) ON DELETE SET NULL
```

## API Endpoints

### Scan for E-books

```
POST /api/ebooks/scan
POST /api/ebooks/scan/{series_id}
```

Scans for e-book files in all series folders or a specific series folder.

### Get E-book Files for Series

```
GET /api/ebooks/series/{series_id}
```

Returns all e-book files for a specific series.

### Get E-book Files for Volume

```
GET /api/ebooks/volume/{volume_id}
```

Returns all e-book files for a specific volume.

## Troubleshooting

If you're having issues with the e-book functionality:

### File Detection Issues

1. Check that your e-book files have supported extensions (.pdf, .epub, .cbz, .cbr, .mobi, .azw)
2. Verify that your files follow the naming conventions for volume detection
3. Check the logs for any errors during scanning
4. Try running a manual scan from the series detail page

### Folder Structure Issues

1. Make sure your collections are properly set up with root folders
2. Check that your series folders are named correctly
3. Verify that the folder paths exist and are accessible
4. Run the `fix and test/create_missing_folders.py` script to create any missing folders

### Collection Integration Issues

1. Make sure the series is added to at least one collection
2. Check that the collection is linked to the root folder containing the files
3. Verify that the volume exists in the database

### Debugging

1. Enable debug logging in the settings
2. Check the logs for detailed information about the scanning process
3. Restart the application to ensure all changes are picked up

## Scripts

Readloom includes several helper scripts for managing e-book folders:

- `fix and test/create_content_type_dirs.py`: Creates the content type directories
- `fix and test/create_missing_folders.py`: Creates folders for all series in the database
- `fix and test/create_series_folder.py`: Creates a folder for a specific series

## Configuration

E-book functionality can be configured in the settings:

### General Settings

- `task_interval_minutes`: The interval for automatic scanning (default: 60 minutes)

### Collection and Root Folder Settings

In v0.0.7+, e-book storage is configured through collections and root folders:

1. Create a collection (e.g., "Manga Collection")
2. Create a root folder with a path where your e-books are stored
3. Link the root folder to the collection

You can have multiple root folders for different types of content, all linked to the same collection or to different collections.
