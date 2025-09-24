# Readloom v0.0.7 Upgrade Notes

This document provides important information about upgrading to Readloom v0.0.7, which introduces significant changes to the application's organization system and e-book scanning functionality.

## Major Changes

### Collection-Based Organization System

Readloom now uses a collection-based system to organize your manga/comics. This is a significant change from previous versions:

- **Collections**: Logical groups of series (e.g., "Shonen Manga", "Currently Reading")
- **Root Folders**: Physical locations on your file system where files are stored
- **Relationships**: Collections can be linked to multiple root folders, and series can belong to multiple collections

### Setup Wizard

When you first launch Readloom v0.0.7, you'll be guided through a setup wizard to:
1. Create your first collection
2. Set up your first root folder
3. Link them together

This setup is now **required** before you can use the application.

### Improved E-book Scanning

The e-book scanning functionality has been significantly improved:
- Better detection of CBZ files in existing folders
- Automatic scanning when importing series with existing folders
- Enhanced logging for troubleshooting

## Upgrade Process

### Automatic Migration

When you upgrade to v0.0.7, Readloom will automatically:
1. Create the necessary database tables for collections
2. Create a default collection
3. Migrate your existing root folders from settings to the database
4. Link your existing root folders to the default collection
5. Add your existing series to the default collection

### Manual Steps

After upgrading, you should:
1. Review the default collection and root folders that were created
2. Create additional collections if desired
3. Organize your series into different collections
4. Run a full e-book scan to take advantage of the improved scanning

## New Features

### Collection Management

You can now:
- Create multiple collections
- Link collections to multiple root folders
- Add series to multiple collections
- Set a default collection for new imports

### Root Folder Management

Root folders are now managed through the UI:
- Create and manage root folders through the Collections page
- Link root folders to collections
- See which collections use each root folder

### Automatic E-book Detection

When importing a series:
- If the folder already exists, Readloom will automatically scan it for e-books
- Any found e-books will be added to your collection
- The API response includes information about the folder and found e-books

## Potential Issues

### Setup Required

If you see a message that setup is required, follow the setup wizard to create your first collection and root folder.

### Missing Series

If some series are missing after the upgrade:
1. Go to the Collections page
2. Check if they're in the default collection
3. If not, try adding them manually to a collection

### E-book Scanning Issues

If e-books aren't being detected:
1. Check the logs for any errors
2. Verify that the file extensions are supported (.pdf, .epub, .cbz, .cbr, .mobi, .azw)
3. Try running a manual scan from the series detail page

## Documentation

For more detailed information, refer to the following documentation:
- [Collections](docs/COLLECTIONS.md) - Collection-based organization system
- [E-book Management](docs/EBOOKS.md) - E-book organization and scanning
- [Folder Structure](docs/FOLDER_STRUCTURE.md) - Series folder organization and naming
- [Changelog](docs/CHANGELOG.md) - Version history and changes
- [Implementation Notes](docs/IMPLEMENTATION_NOTES.md) - Technical details about the implementation

## Feedback

If you encounter any issues with the upgrade or have suggestions for improvements, please open an issue on the GitHub repository.
