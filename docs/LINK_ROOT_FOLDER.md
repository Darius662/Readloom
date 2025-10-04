# Linking Root Folders to Collections

## Overview

The Link Root Folder feature allows you to associate existing root folders with collections through a dedicated modal interface.

## How to Use

1. Navigate to Collections Manager
2. Click the eye icon to view a collection's details
3. In the Root Folders section, click "Link Root Folder"
4. Select an available root folder from the dropdown
5. Click "Link" to confirm

## Key Points

- Only shows root folders not already linked to this collection
- Requires a collection to be selected first
- Uses existing API endpoints (no new endpoints needed)

## Troubleshooting

- **No folders in dropdown**:
  - Create root folders first
  - Check if folders are already linked to this collection
- **Modal won't open**:
  - Verify you've selected a collection
  - Check browser console for errors
  - Hard refresh (Ctrl+F5)
- **Link fails**:
  - Verify API connectivity
  - Check server logs for errors
