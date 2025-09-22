# MangaArr Folder Structure

This document describes how MangaArr manages folder structures for manga and e-book files.

## Overview

MangaArr automatically creates and manages folders for your manga and e-book files. When you add a series to your collection or import it from a metadata provider, MangaArr creates a folder structure in the appropriate root folder based on your collection configuration.

In version 0.0.7, MangaArr introduces a collection-based organization system that allows you to link collections to multiple root folders.

## Root Folder Configuration

In version 0.0.7+, root folders are managed through the Collections page:

```
Collections > Root Folders
```

Each root folder has:
- A path (e.g., `C:\Manga` or `/home/user/manga`)
- A name (e.g., "Main Library")
- A primary content type (e.g., MANGA, COMICS, etc.)

You can create multiple root folders and link them to different collections. This allows you to organize your files in various ways, such as having separate folders for different types of content or different languages.

## Folder Structure

The folder structure is organized by series name within each root folder:

```
/root/folder/1/  (linked to Collection A)
├── Series Name 1/
│   ├── README.txt
│   ├── Volume 1.pdf
│   └── Volume 2.epub
├── Series Name 2/
│   ├── README.txt
│   └── Volume 1.cbz
└── ...

/root/folder/2/  (linked to Collection B)
├── Series Name 3/
│   ├── README.txt
│   └── Volume 1.cbz
└── ...
```

Each series folder contains:
- A README.txt file with series information
- E-book files for each volume (if available)

### Collection-Root Folder Relationship

A collection can be linked to multiple root folders, and a root folder can be linked to multiple collections. When you add a series to a collection, MangaArr will create the series folder in one of the root folders linked to that collection.

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

1. You add a new series manually to a collection
2. You import a series from a metadata provider into a collection
3. You run the `create_missing_folders.py` script

### Folder Selection Logic

When creating a folder for a series, MangaArr follows this logic:

1. If a specific collection is specified, it looks for root folders linked to that collection
2. If no collection is specified or the collection has no root folders, it uses the default collection's root folders
3. If the default collection has no root folders, it uses the first available root folder
4. If no root folders are configured, it uses the default e-book storage directory

## Manual Folder Creation

You can manually create folders for existing series using the following scripts:

- `create_missing_folders.py`: Creates folders for all series in the database
- `create_series_folder.py`: Creates a folder for a specific series

## Troubleshooting

If you encounter issues with folder creation:

1. Check that at least one collection and one root folder are set up
2. Verify that the collection is linked to at least one root folder
3. Check that the root folder exists and is writable
4. Verify that the series exists in the database and is added to a collection
5. Check the logs for any error messages
6. Run the `create_missing_folders.py` script to recreate any missing folders

## Technical Implementation

The folder creation functionality is implemented in:

- `backend/base/helpers.py`: Contains the core functions for folder creation and name sanitization
- `backend/features/collection/collections.py`: Manages collections and root folders
- `backend/features/metadata_service/facade.py`: Handles folder creation during manga import
- `frontend/api_metadata_fixed.py`: API endpoint for importing manga and creating folders
- `frontend/api_collections.py`: API endpoints for managing collections and root folders

The key functions are:

- `create_series_folder_structure`: Creates a folder for a series based on collection configuration
- `get_safe_folder_name`: Sanitizes a string for use as a file or folder name
- `ensure_readme_file`: Creates a README.txt file in a series folder
- `create_collection`: Creates a new collection
- `create_root_folder`: Creates a new root folder
- `add_root_folder_to_collection`: Links a root folder to a collection
