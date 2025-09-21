# E-book Management in MangARR

This document describes the e-book management functionality in MangARR, including folder structure, file scanning, and collection integration.

## Overview

MangARR supports managing e-book files for your manga/comic collection. It organizes files by content type and series name, automatically detects volume numbers from filenames, and integrates with your collection tracking.

## Folder Structure

E-books are organized in a hierarchical folder structure:

```
data/ebooks/
├── MANGA/
│   ├── Series_Name_1/
│   │   ├── README.txt
│   │   ├── Volume_1.pdf
│   │   └── Volume_2.epub
│   └── Series_Name_2/
│       ├── README.txt
│       └── Volume_1.cbz
├── MANHWA/
│   └── ...
├── MANHUA/
│   └── ...
└── ...
```

Each series folder contains:
- A README.txt file with series information
- E-book files for each volume

## Content Types

MangARR supports the following content types, each with its own directory:

- MANGA: Japanese comics
- MANHWA: Korean comics
- MANHUA: Chinese comics
- COMICS: Western comics
- NOVEL: Light novels or text-based stories
- BOOK: Regular books
- OTHER: Other types of content

## Supported File Formats

MangARR supports the following e-book formats:

- PDF (.pdf)
- EPUB (.epub)
- Comic Book ZIP (.cbz)
- Comic Book RAR (.cbr)
- Mobipocket (.mobi)
- Amazon Kindle (.azw, .azw3)

## File Naming Conventions

MangARR automatically extracts volume numbers from filenames using various patterns:

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

MangARR periodically scans for new e-book files in the background. The scan interval can be configured in the settings.

## Collection Integration

When an e-book file is detected:

1. The system checks if a collection item exists for the volume
2. If it exists, it updates the item with the digital format and file information
3. If it doesn't exist, it creates a new collection item with ownership status "OWNED"
4. The format is set to "DIGITAL" or "BOTH" (if you already own a physical copy)

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

1. Make sure the content type directories exist in the `data/ebooks` folder
2. Check that your series folders are named correctly
3. Verify that your e-book files follow the naming conventions
4. Run the `create_missing_folders.py` script to create any missing folders
5. Restart the application to ensure all changes are picked up

## Scripts

MangARR includes several helper scripts for managing e-book folders:

- `create_content_type_dirs.py`: Creates the content type directories
- `create_missing_folders.py`: Creates folders for all series in the database
- `create_series_folder.py`: Creates a folder for a specific series

## Configuration

E-book functionality can be configured in the settings:

- `ebook_storage`: The path to the e-book storage directory (default: "ebooks")
- `task_interval_minutes`: The interval for automatic scanning (default: 60 minutes)
