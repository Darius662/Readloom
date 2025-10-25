# Readloom Known Issues

This document lists known issues in Readloom that need to be addressed.

## Current Issues

### 1. Authors Tab - Temporarily Disabled (RESOLVED - WORKAROUND)

**Status:** Disabled - Placeholder page shown  
**Severity:** Medium (Feature unavailable)  
**Date Reported:** October 25, 2025  
**Date Resolved:** October 26, 2025  
**Version:** v0.1.8

**Description:**
The Authors tab (`/authors`) was causing the browser to freeze indefinitely when accessed. The page would show a loading spinner but never complete loading, and the entire browser tab would become unresponsive.

**Root Cause Analysis:**
After extensive debugging, we discovered that the freeze was caused by a **complex interaction between the base template's notification loading system and the authors page JavaScript initialization**. The exact mechanism involves:

1. The base template's `$(document).ready()` handler was calling `loadNotifications()` synchronously
2. This fetch request was blocking the JavaScript event loop
3. The authors page's `DOMContentLoaded` event would fire, but subsequent `setTimeout` calls would never execute
4. The `loadAuthors()` function would never be called, leaving the page in a frozen state
5. The browser's event loop was completely blocked, making the tab unresponsive

**Key Findings:**
- ✅ The backend API was responding correctly (verified with test endpoints)
- ✅ The health check endpoint worked fine
- ✅ The notifications API was responding (200 OK)
- ❌ The browser's JavaScript event loop was blocked
- ❌ The `setTimeout` callbacks were never firing
- ❌ The page became completely unresponsive

**Attempted Fixes (v0.1.7-0.1.8):**
1. Removed `@setup_required` decorator from API routes
2. Replaced BookService with direct database queries
3. Added 5-second timeout to fetch requests
4. Disabled periodic task manager during development
5. Added comprehensive console logging to track execution
6. Delayed notifications loading with `setTimeout`
7. Simplified JavaScript initialization with try-catch blocks
8. Attempted to use `Promise.race()` with timeout

**None of these fixes resolved the underlying issue.**

**Current Solution (v0.1.8):**
The Authors tab has been replaced with a simple "Coming Soon" placeholder page that:
- Loads instantly without any JavaScript
- Informs users the feature is under development
- Provides a link to the Books Search page as an alternative
- Does not freeze the browser

**Files Modified:**
- `/frontend/templates/authors/authors.html` - Replaced with simple placeholder
- `/frontend/static/js/authors.js` - No longer used (can be removed)
- `/frontend/api_authors.py` - API still available but not used
- `/run_dev.py` - Periodic task manager disabled
- `/frontend/templates/base.html` - Notifications loading delayed

**Future Implementation:**
To properly implement the Authors tab in the future, consider:
1. Using a separate worker thread or async task queue for heavy operations
2. Implementing pagination from the start to avoid loading large datasets
3. Using a modern frontend framework (React, Vue) instead of jQuery
4. Separating concerns between base template and page-specific scripts
5. Implementing proper request cancellation and timeouts

---

## Fixed Issues

### ✅ Authors Page Blank (FIXED - v0.1.7)

**Status:** Fixed  
**Date Fixed:** October 25, 2025

**Issue:**
The authors page was showing a blank page instead of loading authors.

**Root Cause:**
The `get_all_authors()` and `get_author_details()` methods in BookService were trying to select columns that don't exist in the database schema (e.g., `metadata_source`, `metadata_id`).

**Solution:**
Updated BookService to dynamically build column lists based on what actually exists in the database schema. This prevents SQL errors when columns are missing.

**Files Fixed:**
- `/backend/features/book_service.py` - Updated get_all_authors() and get_author_details()

---

## Recommendations

### For Developers
1. Always check database schema before writing queries
2. Use dynamic column selection when possible
3. Add comprehensive error handling to JavaScript
4. Test API endpoints with curl before debugging frontend
5. Enable browser developer tools to catch JavaScript errors

### For Users
1. Avoid clicking the Authors tab (it's hidden now)
2. Report any new issues with detailed error messages
3. Check the browser console (F12) for error messages

---

## Testing Checklist

Before re-enabling the Authors tab:
- [ ] Test `/api/authors` endpoint with curl
- [ ] Check browser console for JavaScript errors
- [ ] Verify BookService methods work correctly
- [ ] Test with sample author data in database
- [ ] Test pagination and sorting
- [ ] Test error handling with network failures
- [ ] Test with different browsers
- [ ] Verify performance with large author lists

---

## Related Documentation

- [LATEST_UPDATES_v0.1.6.md](LATEST_UPDATES_v0.1.6.md) - Latest changes
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [API.md](API.md) - API documentation

---

**Last Updated:** October 26, 2025  
**Maintained By:** Readloom Development Team

---

## Summary

The Authors tab issue has been resolved by replacing the problematic dynamic page with a simple static placeholder. This allows the application to remain fully functional while the Authors feature is redesigned and reimplemented with a more robust architecture in a future version.
