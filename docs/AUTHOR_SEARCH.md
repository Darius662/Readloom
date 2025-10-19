# Author Search and Details

This document describes the author search and details features in Readloom, including how to search for authors, view author details, and understand the metadata provided.

## Overview

Readloom provides a comprehensive author search and details system that allows you to find information about authors, view their bibliographies, and explore their works. This feature is particularly useful for book collectors and readers who want to discover new authors or learn more about their favorite writers.

## Author Search

### How to Search for Authors

1. Navigate to the Books section of Readloom
2. Click on "Search" in the sidebar or main navigation
3. Enter an author's name in the search box
4. Select "Author" from the search type dropdown
5. Select a provider (OpenLibrary recommended for author information)
6. Click "Search" to find authors matching your query

### Search Results

Author search results are displayed as cards with the following information:

- Author's photo (when available)
- Author's name
- Birth and death dates (when available)
- Work count (number of published works)
- Notable work (a significant publication by the author)
- Provider badge (indicating the source of the information)

### Supported Providers

The following providers support author search:

- **OpenLibrary** (recommended): Comprehensive author information including photos, biographies, and bibliographies
- **Google Books**: Basic author information with some bibliographic data
- **WorldCat**: Academic and scholarly author information

## Author Details

### Viewing Author Details

To view detailed information about an author:

1. Search for an author as described above
2. Click the "Author Details" button on the author card
3. A modal will appear with comprehensive information about the author

### Author Details Content

The author details modal includes:

- **Header Information**:
  - Author's name
  - Author's photo (when available)
  
- **Biographical Information**:
  - Full name/personal name
  - Birth date
  - Death date (if applicable)
  - Alternative names/pseudonyms
  
- **Works Information**:
  - Total work count
  - Notable works (up to 5 significant publications)
  
- **Subject Categories**:
  - Literary genres
  - Subject areas
  - Themes
  
- **Places**:
  - Locations associated with the author
  
- **External Links**:
  - Goodreads profile
  - Wikipedia page
  - Other relevant resources
  
- **Biography**:
  - Detailed biographical text about the author

## Technical Implementation

### API Endpoints

- `/api/metadata/author_search`: Search for authors by name
  - Parameters:
    - `query`: Author name to search for
    - `provider`: Metadata provider to use (OpenLibrary, GoogleBooks, etc.)
  
- `/api/metadata/author/{provider}/{author_id}`: Get detailed author information
  - Parameters:
    - `provider`: Metadata provider (e.g., OpenLibrary)
    - `author_id`: Unique identifier for the author

### Data Sources

Author information is sourced from various providers, with OpenLibrary being the primary source due to its comprehensive author data. The system combines information from:

- OpenLibrary JSON API
- OpenLibrary HTML pages (for additional metadata)
- Author works listings
- External references and links

### Caching

Author data is cached to improve performance and reduce API calls to external providers. The cache includes:

- Basic author information (name, dates, work count)
- Author photos
- Bibliographic information
- Subject categories

## Best Practices

- **Use specific author names**: More specific queries yield better results
- **Try OpenLibrary first**: OpenLibrary generally has the most comprehensive author information
- **Be patient with loading**: Detailed author information may take a moment to load, especially for prolific authors
- **Look for the "Author" header**: In search results, look for cards with the "Author" header to distinguish from book results

## Related Documentation

- [Book Providers](BOOK_PROVIDERS.md): Information about book metadata providers
- [Metadata Providers](METADATA_PROVIDERS.md): General information about metadata providers
- [API Documentation](API.md): Complete API reference
