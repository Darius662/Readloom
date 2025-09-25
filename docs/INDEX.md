# Readloom Documentation Index

This document provides an overview of all available documentation for Readloom.

## Getting Started

- [Installation Guide](INSTALLATION.md) - Detailed setup instructions
- [Upgrade Notes](../UPGRADE_NOTES.md) - Important information for upgrading to v0.0.7
- [Changelog](CHANGELOG.md) - Version history and changes

## Core Features

- [Collections](COLLECTIONS.md) - Collection-based organization system (v0.0.7+)
- [Collection Maintenance](COLLECTION_MAINTENANCE.md) - Troubleshooting and fixing collection issues
- [E-book Management](EBOOKS.md) - E-book organization and scanning
- [Folder Structure](FOLDER_STRUCTURE.md) - Series folder organization and naming
- [API Documentation](API.md) - Complete API reference

## Technical Documentation

- [Database Schema](DATABASE.md) - Database structure information
- [Codebase Structure](CODEBASE_STRUCTURE.md) - Overview of the modular architecture
- [UI Structure](UI_STRUCTURE.md) - Overview of the user interface organization
- [Direct Execution Mode](DIRECT_EXECUTION.md) - Running Readloom in direct execution mode
- [Implementation Notes](IMPLEMENTATION_NOTES.md) - Technical details about implementations
- [Performance Tips](PERFORMANCE_TIPS.md) - Optimize for large collections

## Integrations

- [AniList Provider](ANILIST_PROVIDER.md) - AniList integration details
- [Metadata Providers](METADATA_PROVIDERS.md) - Details on metadata provider implementation
- [Image Proxy](IMAGE_PROXY.md) - Image proxy functionality

## Development

- [Contributing Guide](CONTRIBUTING.md) - Guidelines for contributing to Readloom
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community guidelines
- [Refactoring Guide](REFACTORING_GUIDE.md) - Guidelines for code refactoring

## Version-Specific Features

### v0.0.9 (Latest)

- **UI Improvements**: 
  - Root Folders management integrated into Collections Manager
  - Integrations moved to Settings page for better organization
  - Collapsible E-book Management section with quick actions
  - Streamlined Series Detail page with improved layout
  - Icon-only Edit button in top-right corner
  - Custom Path import functionality moved to Edit Series modal
- **Metadata Provider Optimization**:
  - Only AniList enabled by default for better performance
  - Other providers can be enabled as needed
- **Critical Fixes**:
  - Fixed Readloom_direct.py to properly initialize services
  - Corrected static file serving in direct execution mode
  - Fixed Setup Wizard functionality in direct mode
  - Added proper blueprint registration

### v0.0.8

- **Folder Validation**: Validate and create folders directly from the UI
- **Custom Paths**: Set custom paths for series with validation
- **Improved Error Handling**: Better feedback for file system operations

### v0.0.7

- **Collection System**: Organize manga/comics into collections linked to root folders
- **Collections Manager**: Create and manage multiple collections and their relationships
- **Library Tab**: Renamed from "Collection" tab for clarity
- **Collection Maintenance Tools**: Scripts to fix collection database issues
- **Setup Wizard**: Guide for first-time users to create collections and root folders
- **Improved E-book Scanning**: Better detection of files in existing folders
- **Automatic Import Scanning**: Scan existing folders when importing series

### v0.0.6

- **Enhanced Folder Naming**: Preserves spaces and most special characters
- **Improved README Files**: Better series information in README files
- **Fixed Folder Creation**: More robust folder creation logic

### v0.0.5

- **E-book Management System**: Organize and track digital manga/comics
- **Advanced Volume Detection**: Better volume number extraction from filenames
- **Multiple E-book Format Support**: PDF, EPUB, CBZ, CBR, MOBI, AZW

## Troubleshooting

If you encounter issues:

1. Check the relevant documentation section for your specific feature
2. Look for troubleshooting sections within each document
3. Check the logs for error messages
4. Refer to the [Implementation Notes](IMPLEMENTATION_NOTES.md) for technical details
5. If all else fails, open an issue on the GitHub repository
