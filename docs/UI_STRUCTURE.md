# Readloom UI Structure

This document provides an overview of the Readloom user interface structure and navigation.

## Navigation Structure

Readloom's UI is organized with a sidebar navigation that provides access to all major features:

- **Dashboard**: Overview of your library and recent activity
- **Calendar**: View upcoming releases in a calendar format
- **Series**: Browse all e-book series in your library
- **Library**: View your collection of e-books
- **Collections Manager**: Manage collections and root folders
- **Search**: Search for new e-books to add to your library
- **Notifications**: View system notifications
- **Settings**: Configure application settings and integrations
- **About**: Information about Readloom

## Key Pages

### Collections Manager

The Collections Manager provides a unified interface for managing both collections and root folders:

- **Collections**: Create, edit, and delete collections
- **Root Folders**: Add, edit, and delete root folders
- **Linking**: Connect collections to root folders

This page replaces the separate Root Folders management page from previous versions.

### Settings

The Settings page is organized into tabs:

- **General**: Basic application settings (host, port, URL base)
- **Calendar**: Calendar-specific settings
- **Logging**: Configure logging behavior
- **Integrations**: Configure external integrations:
  - Home Assistant integration
  - Homarr dashboard integration
  - Metadata providers configuration

The Integrations tab consolidates what was previously a separate page, providing a more organized settings experience.

### Search Page

The Search page provides a unified interface for finding books, manga, and authors:

- **Content Type Selector**: Toggle between Books and Manga content types
- **Search Form**:
  - Search query input field
  - Search type dropdown (Title or Author)
  - Provider/Indexer dropdown (filtered based on content type)
  - Search button
- **Search Results**:
  - Grid layout with cards for each result
  - Different card styles for books and authors
  - Book cards show cover image, title, and author
  - Author cards show author photo, name, and notable works
  - Details button to view more information
- **Author Details**:
  - Modal with comprehensive author information
  - Author photo and biographical information
  - Birth and death dates
  - Bibliography (list of works)
  - External links and references
  - Subject areas the author writes about

### Series Detail

The Series Detail page provides comprehensive information about an e-book series:

- **Header Section**: 
  - Series title, author, publisher information
  - Description and metadata (status, content type)
  - Edit button positioned in the top-right corner as an icon-only button

- **E-book Management**: 
  - Collapsible section to reduce visual clutter
  - Quick action in footer for scanning e-books without expanding details
  - Detailed information available when expanded (folder location, supported formats)
  - Custom path functionality moved to Edit Series modal for better organization

- **Volumes and Chapters**: 
  - Tabular display of volumes and chapters
  - File management and status tracking
  - Upload functionality for e-book files

### Setup Wizard

For new users, the Setup Wizard guides through the initial configuration:

1. Creating a collection
2. Adding a root folder
3. Linking the collection and root folder

## UI Components

### Sidebar Navigation

The sidebar provides the main navigation structure and can be collapsed to provide more screen space for content.

### Cards

Content is organized into cards with consistent styling:

- Card headers for section titles
- Card bodies for content
- Card footers for actions

#### Collapsible Cards

Some cards feature collapsible content to reduce visual clutter:

- Toggle button in the header with chevron icon that changes direction
- Initially collapsed state for non-essential information
- Quick actions in the footer for common tasks without expanding
- Auto-expansion when important information needs to be shown

### Tables

Data is presented in responsive tables with:

- Sortable columns (where applicable)
- Action buttons for item management
- Status indicators

### Modals

Modal dialogs are used for:

- Adding new items
- Editing existing items
- Confirmation dialogs
- Detailed information views

### Action Buttons

Action buttons follow these conventions:

- Primary actions use solid buttons with appropriate colors
- Secondary actions use outline buttons
- Icon-only buttons for common actions to reduce visual clutter
- Button placement follows standard patterns:
  - Edit buttons in top-right corner as icon-only buttons
  - Form submission buttons at bottom right of forms/modals
  - Quick actions in card footers

## Best Practices for UI Extensions

When extending the Readloom UI:

1. **Follow existing patterns**: Use the established card and table structures
2. **Use consistent styling**: Apply Bootstrap classes consistently
3. **Responsive design**: Ensure all new UI elements work on mobile devices
4. **Accessibility**: Include proper ARIA attributes and keyboard navigation
5. **Error handling**: Provide clear error messages and validation feedback

## UI Customization

Readloom's UI can be customized through:

- Dark/light mode toggle
- URL base configuration for reverse proxy setups
- Custom CSS (advanced users can modify the static CSS files)

## JavaScript Components

The UI is powered by several JavaScript components:

- **main.js**: Core UI functionality and shared utilities
- **folder-validation.js**: Validates and creates folders with consistent behavior across the application
- **collections_manager.js**: Manages collections and root folders in a unified interface
- **calendar.js**: Calendar view functionality and event handling
- **ebook-manager.js**: E-book file management, scanning, and format handling

These components handle:
- API interactions and data fetching
- DOM manipulation and dynamic content generation
- User interaction handling
- Form validation and submission
- Collapsible UI elements and state management
- Toast notifications for user feedback
