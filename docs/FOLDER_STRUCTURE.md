# MangaArr Folder Structure

This document describes how MangaArr manages folder structures for manga and e-book files.

## Overview

MangaArr automatically creates and manages folders for your manga and e-book files. When you add a series to your collection or import it from a metadata provider, MangaArr creates a folder structure in your configured root folder.

## Root Folder Configuration

The root folder is configured in the settings:

```
Settings > Storage > Root Folder
```

By default, this is set to `data/ebooks` relative to the MangaArr installation directory.

## Folder Structure

The folder structure is organized by series name:

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
- A README.txt file with series information
- E-book files for each volume (if available)

## Folder Naming

MangaArr preserves spaces and most special characters in folder names for better readability. Only characters that are invalid in file names are replaced:

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

## README Files

Each series folder contains a README.txt file with the following information:

```
Series: Series Name
ID: 42
Type: MANGA
Created: 2025-09-22 12:34:56

This folder is managed by MangARR. Place your e-book files here.
```

This file helps users identify the purpose of the folder and provides basic metadata about the series.

## Automatic Folder Creation

Folders are automatically created when:

1. You add a new series manually
2. You import a series from a metadata provider
3. You run the `create_missing_folders.py` script

## Manual Folder Creation

You can manually create folders for existing series using the following scripts:

- `create_missing_folders.py`: Creates folders for all series in the database
- `create_series_folder.py`: Creates a folder for a specific series

## Troubleshooting

If you encounter issues with folder creation:

1. Check that the root folder exists and is writable
2. Verify that the series exists in the database
3. Check the logs for any error messages
4. Run the `create_missing_folders.py` script to recreate any missing folders

## Technical Implementation

The folder creation functionality is implemented in:

- `backend/base/helpers.py`: Contains the core functions for folder creation and name sanitization
- `backend/features/metadata_service/facade.py`: Handles folder creation during manga import
- `frontend/api_metadata_fixed.py`: API endpoint for importing manga and creating folders

The key functions are:

- `create_series_folder`: Creates a folder for a series
- `sanitize_filename`: Sanitizes a string for use as a file or folder name
- `ensure_readme_file`: Creates a README.txt file in a series folder
