# Collection Maintenance

This document provides information about maintaining and troubleshooting the collections system in MangaArr.

## Overview

MangaArr's collections system allows you to organize your manga/comics into logical groups. However, in some cases, you might encounter issues such as duplicate collections or problems with the delete functionality. This document explains how to use the maintenance scripts to fix these issues.

## Maintenance Scripts

### fix_collections.py

The `fix_collections.py` script is designed to clean up and fix issues with collections in the database. It performs the following actions:

1. Identifies and removes duplicate collections
2. Ensures there is only one default collection
3. Verifies that all root folders are associated with at least one collection
4. Updates the root_folders setting in the settings table

#### Usage

To run the script:

```bash
python fix_collections.py
```

The script will:
1. Display all collections in the database
2. Automatically determine which collections to keep (Manga, Books, and one Default Collection)
3. Delete any duplicate collections
4. Ensure there is only one default collection
5. Associate any orphaned root folders with the default collection
6. Update the root_folders setting in the settings table

### cleanup_collections.py

The `cleanup_collections.py` script is a simpler version that focuses specifically on removing duplicate Default Collections.

#### Usage

To run the script:

```bash
python cleanup_collections.py
```

## Common Issues and Solutions

### Duplicate Default Collections

**Issue**: Multiple collections named "Default Collection" appear in the Collections Manager.

**Solution**:
1. Run the `fix_collections.py` script to clean up duplicate collections
2. Restart the application

### Delete Button Not Working

**Issue**: Unable to delete collections or remove root folders from collections.

**Solution**:
1. Make sure you're not trying to delete the default collection (which is not allowed)
2. Check the browser console for any JavaScript errors
3. Try refreshing the page and attempting the operation again
4. If problems persist, run the `fix_collections.py` script to clean up the database

### Root Folder Not Showing in Collection

**Issue**: A root folder is not appearing in a collection even though it should be associated with it.

**Solution**:
1. Go to the Collections Manager
2. Select the collection
3. Try removing and re-adding the root folder
4. If that doesn't work, run the `fix_collections.py` script

### Collection Not Showing in Library

**Issue**: A collection is not appearing in the Library tab dropdown.

**Solution**:
1. Check if the collection exists in the Collections Manager
2. Verify that the collection has at least one root folder associated with it
3. Run the `fix_collections.py` script to fix any database inconsistencies

## Best Practices

1. **Regular Maintenance**: Run the `fix_collections.py` script periodically to ensure your collections database remains clean
2. **Backup Before Maintenance**: Always back up your database before running maintenance scripts
3. **Check Logs**: Review the application logs for any errors related to collections
4. **One Default Collection**: Ensure you have only one default collection
5. **Associate Root Folders**: Make sure all root folders are associated with at least one collection

## Advanced Troubleshooting

If you continue to experience issues with collections after running the maintenance scripts, you may need to manually inspect and fix the database. The collections system uses the following tables:

- `collections`: Stores collection information
- `collection_root_folders`: Maps collections to root folders (many-to-many relationship)
- `series_collections`: Maps series to collections (many-to-many relationship)
- `root_folders`: Stores root folder information

You can use SQLite tools to directly query and modify these tables if necessary.
