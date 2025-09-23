# Collections in MangaArr

This document explains the collection system in MangaArr and how it relates to root folders and series.

## Overview

Collections in MangaArr provide a way to organize your manga/comics into logical groups. Each collection can be linked to multiple root folders, and each series can belong to multiple collections. This flexible system allows you to organize your content in various ways.

The Library tab (formerly Collection tab) shows your content organized by the currently selected collection, while the Collections Manager allows you to create and manage multiple collections and their relationships with root folders.

## Key Concepts

### Collections

A collection is a logical grouping of series. For example, you might have collections like:
- "Shonen Manga"
- "Seinen Manga"
- "Western Comics"
- "Completed Series"
- "Currently Reading"

Each collection has:
- A name
- An optional description
- Links to one or more root folders
- Links to series

### Root Folders

A root folder is a physical location on your file system where MangaArr stores and organizes your manga/comic files. Each root folder has:
- A path (e.g., `C:\Manga` or `/home/user/manga`)
- A name (e.g., "Main Manga Library")
- A primary content type (e.g., MANGA, COMICS, etc.)

Root folders can be linked to multiple collections, allowing you to organize your physical storage in different ways.

### Series-Collection Relationship

Series can belong to multiple collections, allowing you to categorize them in different ways. For example, a series might be in both your "Shonen Manga" collection and your "Currently Reading" collection.

## Setup Requirements

MangaArr requires at least one collection and one root folder to be set up before you can use the application. When you first launch MangaArr, you'll be guided through a setup wizard to create these.

## Managing Collections

### Creating a Collection

1. Go to the Collections Manager page
2. Click "Add Collection"
3. Enter a name and optional description
4. Choose whether this should be the default collection
5. Click "Save"

### Adding Root Folders to a Collection

1. Go to the Collections Manager page
2. Select a collection by clicking the select button (checkmark icon)
3. In the Root Folders section of the page, find the root folder you want to add
4. Click the "Add to Selected Collection" button (plus icon)

Alternatively, you can create a new root folder and add it to the selected collection:

1. Click "Add Root Folder"
2. Enter the path, name, and content type
3. Click "Save"
4. When prompted, confirm that you want to add it to the selected collection

### Adding Series to a Collection

Series are automatically added to the collection associated with the root folder they're imported into. You can also manually add series to collections:

1. Go to the Collections Manager page
2. Select a collection
3. In the Series section of the collection details, click "Add Series"
4. Select series from the dropdown
5. Click "Add"

### Removing Root Folders from a Collection

1. Go to the Collections Manager page
2. Select a collection
3. In the Root Folders section of the collection details, find the root folder you want to remove
4. Click the remove button (X icon)
5. Confirm the removal

### Removing Series from a Collection

1. Go to the Collections Manager page
2. Select a collection
3. In the Series section of the collection details, find the series you want to remove
4. Click the remove button (X icon)
5. Confirm the removal

## Default Collection

One collection can be designated as the default collection. This collection is used when:
- Importing series without specifying a collection
- Creating new series without specifying a collection

The default collection is marked with a green "Default" badge in the Collections Manager. You can change which collection is the default by editing a collection and checking the "Set as default collection" option.

## API Endpoints

MangaArr provides API endpoints for managing collections:

### Collections

- `GET /api/collections` - Get all collections
- `GET /api/collections/{id}` - Get a specific collection
- `POST /api/collections` - Create a new collection
- `PUT /api/collections/{id}` - Update a collection
- `DELETE /api/collections/{id}` - Delete a collection

### Root Folders

- `GET /api/root-folders` - Get all root folders
- `GET /api/root-folders/{id}` - Get a specific root folder
- `POST /api/root-folders` - Create a new root folder
- `PUT /api/root-folders/{id}` - Update a root folder
- `DELETE /api/root-folders/{id}` - Delete a root folder

### Collection-Root Folder Relationships

- `GET /api/collections/{id}/root-folders` - Get all root folders for a collection
- `POST /api/collections/{id}/root-folders/{folder_id}` - Add a root folder to a collection
- `DELETE /api/collections/{id}/root-folders/{folder_id}` - Remove a root folder from a collection

### Collection-Series Relationships

- `GET /api/collections/{id}/series` - Get all series in a collection
- `POST /api/collections/{id}/series/{series_id}` - Add a series to a collection
- `DELETE /api/collections/{id}/series/{series_id}` - Remove a series from a collection

## Best Practices

1. **Create meaningful collections**: Group your series in ways that make sense for your library
2. **Use multiple root folders**: Consider using separate root folders for different types of content
3. **Set a default collection**: This simplifies importing new series
4. **Use descriptive names**: Give your collections and root folders clear, descriptive names
5. **Organize by reading status**: Consider creating collections for "Currently Reading", "Plan to Read", etc.

## Troubleshooting

### Collection Not Showing Series

If a series isn't showing up in a collection:
1. Check that the series is properly linked to the collection
2. Verify that the root folder containing the series is linked to the collection
3. Try removing and re-adding the series to the collection

### Root Folder Issues

If you're having issues with root folders:
1. Ensure the path exists and is accessible
2. Check that the folder has proper permissions
3. Verify that the folder is linked to at least one collection

### Setup Wizard Not Completing

If you're having trouble completing the setup wizard:
1. Ensure you've entered valid paths for root folders
2. Check that the application has permission to create directories
3. Try using absolute paths instead of relative paths

### Duplicate Default Collections

If you notice multiple "Default Collection" entries:
1. Run the `fix_collections.py` script to clean up duplicate collections
2. Restart the application

### Delete Button Not Working

If you're unable to delete collections or remove root folders:
1. Make sure you're not trying to delete the default collection (which is not allowed)
2. Check the browser console for any JavaScript errors
3. Try refreshing the page and attempting the operation again
4. If problems persist, run the `fix_collections.py` script to clean up the database
