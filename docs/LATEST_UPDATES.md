# Readloom v0.1.7 - Latest Updates

**Date:** October 25, 2025  
**Version:** 0.1.7

## Overview

This document outlines all the major updates and improvements made to Readloom in version 0.1.7, focusing on book details page redesign, UI consistency improvements, and ebook file handling enhancements.

---

## 1. Book Details Page Redesign

### Changes
The book details page has been completely redesigned to match the manga series page layout and provide a more consistent user experience.

### Features
- **Full-Width Layout**: Changed from `books_layout.html` to `base.html` for full-width display
- **Consistent Header**: Added card header with title and action buttons
- **Round Icon Buttons**: Edit, Move, and Delete buttons now use round icon-only style matching manga tabs
- **E-book Management Section**: 
  - Collapsed by default for cleaner interface
  - Quick Actions footer with Move and Scan buttons
  - File management with download and delete capabilities
  - Scan for E-books functionality
- **Modal Dialogs**:
  - Edit Book modal for updating series details
  - Move Book modal for relocating books to different collections
- **Terminology**: Updated labels to use "Book" terminology (Edit Book, Move Book)

### Benefits
✅ Consistent design across book and manga pages  
✅ Cleaner, more organized interface  
✅ Better file management capabilities  
✅ Improved user experience with collapsible sections  

---

## 2. UI Consistency Improvements

### Changes
Both book and manga detail pages now have consistent button styling and positioning.

### Features
- **Button Design**: All action buttons use `rounded-circle` style with proper spacing (`gap-3`)
- **Header Layout**: Buttons positioned in card header for better visual hierarchy
- **Button Order**: Edit (primary), Move (secondary), Delete (danger)
- **Color Coding**: Primary (blue), Secondary (gray), Danger (red)
- **Responsive Design**: Buttons maintain proper alignment on all screen sizes

### Result
✅ Professional, cohesive design  
✅ Improved visual hierarchy  
✅ Better user interaction patterns  

---

## 3. Manga Volume Detection Fix

### Issue
Manga volumes were not being identified automatically after the recent revamp.

### Root Cause
The `manga_volume_cache` table migration wasn't being executed automatically during application startup.

### Solution
- Fixed migration ordering and execution
- Ensured all migrations run automatically on app startup
- Created migration `0008_add_manga_volume_cache.py` to cache volume data

### Result
✅ Volumes are now automatically detected and cached  
✅ Three-tier detection system working:
  1. Static database (POPULAR_MANGA_DATA)
  2. Web scraping (MangaFire, MangaDex, MangaPark)
  3. Estimation based on chapter count

---

## 2. Ebook File Recognition & Permissions

### Issue
CBZ and other ebook files were not being recognized by the scanner due to restrictive file permissions.

### Solution
- Added `fix_file_permissions()` function to automatically fix unreadable files
- Integrated permission fixing into the ebook scanner
- Graceful error handling for permission-denied scenarios

### Features
✅ Automatic permission detection and fixing  
✅ Works for both Docker (root) and local development (regular user)  
✅ Comprehensive logging for debugging  
✅ Continues scanning even if permission fixing fails

### Supported Formats
- PDF
- EPUB
- CBZ (Comic Book Archive)
- CBR (Comic Book Archive RAR)
- MOBI
- AZW / AZW3 (Kindle)

---

## 3. Enhanced Volumes Table UI

### Changes
The volumes display has been completely redesigned to match the old v0.1.2-2 design with enhanced functionality.

### New Features

#### Format Management
- **Format Selector** - Choose between Physical, Digital, Both, or None
- **Digital Format Selector** - Select specific digital format (PDF, EPUB, CBZ, etc.)
- **Automatic Detection** - Formats are automatically detected from uploaded files

#### File Management
- **File Display** - Shows actual filename with download and delete options
- **Download Button** - Download ebook files directly from the table
- **Delete Button** - Remove ebook files with confirmation
- **Upload Button** - Upload files when format is set to Digital or Both

#### Smart Auto-Detection
When a file is uploaded or detected:
1. Format is automatically set to **DIGITAL**
2. Digital Format is automatically detected from file extension
3. Collection item is updated in the background
4. No manual configuration needed!

### UI Layout
```
# | Title | Release Date | Format | Digital Format | File | Actions
1 | Vol 1 | 2019-11-26   | [Digital ▼] | [CBZ ▼] | Vol 1.cbz [↓] [🗑] | [✎] [🗑]
```

---

## 4. Database Schema Updates

### New Migration: 0015_add_ebook_columns_to_collection_items

Added three essential columns to `collection_items` table:

```sql
ALTER TABLE collection_items ADD COLUMN has_file INTEGER DEFAULT 0;
ALTER TABLE collection_items ADD COLUMN ebook_file_id INTEGER;
ALTER TABLE collection_items ADD COLUMN digital_format TEXT;
```

### Purpose
- `has_file` - Tracks if a volume has an associated ebook file
- `ebook_file_id` - Links to the ebook file record
- `digital_format` - Stores the format of the digital file

---

## 5. API Endpoints

### Volume Format Management

#### Update Volume Format
```
PUT /api/collection/volume/{volumeId}/format
Content-Type: application/json

{
  "format": "DIGITAL"  // PHYSICAL, DIGITAL, BOTH, or NONE
}
```

#### Update Volume Digital Format
```
PUT /api/collection/volume/{volumeId}/digital-format
Content-Type: application/json

{
  "digital_format": "CBZ"  // PDF, EPUB, CBZ, CBR, MOBI, AZW, or NONE
}
```

#### Upload Ebook File
```
POST /api/ebooks/upload
Content-Type: multipart/form-data

- file: <binary file data>
- series_id: <integer>
- volume_id: <integer>
```

#### Delete Ebook File
```
DELETE /api/ebooks/{fileId}
```

#### Get Ebook Files for Series
```
GET /api/ebooks/series/{seriesId}
```

---

## 6. File Scanning & Import

### Automatic Ebook Scanning

The ebook scanner now:
1. Scans configured root folders for ebook files
2. Automatically fixes file permissions if needed
3. Extracts volume numbers from filenames
4. Creates volumes if they don't exist
5. Links files to volumes in the database
6. Updates collection items with file information

### Supported Filename Patterns
- `Vol 1.cbz` → Volume 1
- `Volume 2.pdf` → Volume 2
- `v3.epub` → Volume 3
- `1.mobi` → Volume 1
- `Chapter 1.cbz` → Chapter 1 (if no volume found)
- `#5.cbz` → Volume 5

### Scan Endpoint
```
POST /api/ebooks/scan
Content-Type: application/json

{
  "series_id": 2,           // Optional: scan specific series
  "custom_path": "/path"    // Optional: scan custom directory
}
```

---

## 7. Migration System Improvements

### Fixed Issues
- Resolved duplicate migration version numbers (0007, 0010, 0012)
- Fixed migration ordering and execution
- Added proper error handling for already-applied migrations

### Migration Files
All migrations are now properly ordered:
- 0004 - Add confirmed release flags
- 0005 - Add collections and root folders
- 0006 - Fix duplicate default collections
- 0007 - Add authors table
- 0008 - Remove default collection requirement
- 0009 - Add manga volume cache
- 0010 - Fix collection default constraint
- 0011 - Add is_book column
- 0012 - Fix unique default check
- 0013 - Fix collections FK references
- 0014 - Typed default collections
- 0015 - Add ebook columns to collection items

---

## 8. User Experience Improvements

### For End Users
✅ No manual permission fixing needed  
✅ Automatic format detection on file upload  
✅ Intuitive volume management interface  
✅ One-click file download and deletion  
✅ Seamless ebook integration

### For Developers
✅ Comprehensive logging for debugging  
✅ Proper error handling and recovery  
✅ Clean API endpoints  
✅ Well-organized database schema  
✅ Modular code structure

---

## 9. Testing & Validation

### Tested Scenarios
✅ Uploading CBZ files with automatic format detection  
✅ Downloading ebook files from the UI  
✅ Deleting ebook files with confirmation  
✅ Changing format and digital format selectors  
✅ Scanning directories with restrictive permissions  
✅ Creating volumes from scanned files  
✅ Updating collection items with file information

### Known Limitations
- SQLite doesn't support dropping columns, so migrations are append-only
- File permissions may vary depending on the filesystem and OS
- Some file formats may not be recognized if extensions are non-standard

---

## 10. Configuration

### Root Folders
Configure root folders in Settings to enable automatic scanning:
```json
{
  "root_folders": [
    {
      "path": "/mnt/media/eBooks/Manga",
      "name": "Manga Library",
      "content_type": "MANGA"
    },
    {
      "path": "/mnt/media/eBooks/Books",
      "name": "Book Library",
      "content_type": "BOOK"
    }
  ]
}
```

### Supported File Formats
- **Comics**: CBZ, CBR
- **E-books**: PDF, EPUB, MOBI
- **Kindle**: AZW, AZW3

---

## 11. Future Improvements

### Planned Features
- [ ] Batch upload for multiple files
- [ ] Drag-and-drop file upload
- [ ] File preview functionality
- [ ] Advanced search and filtering
- [ ] Export collection to various formats
- [ ] Integration with external ebook readers
- [ ] Automatic metadata extraction from files

---

## 12. Troubleshooting

### Issue: Files not being scanned
**Solution:** Check file permissions and ensure root folder is configured correctly

### Issue: Format not updating
**Solution:** Ensure the API endpoint is accessible and the database columns exist

### Issue: 404 errors on format update
**Solution:** Verify the `/api/collection/volume/{id}/format` endpoint is registered

### Issue: Permission denied on file operations
**Solution:** The app will attempt to fix permissions automatically. Check logs for details.

---

## 13. Summary of Changes

| Component | Change | Impact |
|-----------|--------|--------|
| Database | Added 3 new columns to collection_items | Full ebook file tracking |
| UI | Redesigned volumes table | Better UX and file management |
| Backend | Added permission fixing | Works with restricted files |
| API | Added format update endpoints | Programmatic format control |
| Scanner | Enhanced with auto-detection | Seamless file integration |
| Migrations | Fixed ordering and execution | Reliable database setup |

---

## 14. Version History

### v0.1.6 (Current)
- Fixed manga volume detection
- Enhanced ebook file recognition
- Redesigned volumes UI
- Added automatic format detection
- Fixed database migrations
- Improved file permission handling

### v0.1.5
- Initial hybrid UI implementation
- Collection management system
- Metadata provider integration

### v0.1.2-2 (development-master)
- Original volumes table design
- Basic ebook support
- Collection system foundation

---

## 15. Support & Documentation

For more information, see:
- [EBOOKS.md](EBOOKS.md) - Detailed ebook management guide
- [DATABASE.md](DATABASE.md) - Database schema documentation
- [API.md](API.md) - Complete API reference
- [VOLUME_DETECTION_FIX.md](VOLUME_DETECTION_FIX.md) - Volume detection details
- [SMART_CACHING_SYSTEM.md](SMART_CACHING_SYSTEM.md) - Caching system details

---

**Last Updated:** October 25, 2025  
**Maintained By:** Readloom Development Team
