# Book Metadata Providers

This document describes the book metadata providers available in Readloom, including Google Books API, Open Library API, ISBNdb API, and WorldCat API.

## Overview

In addition to manga/comic metadata providers, Readloom now supports several book-specific metadata providers to help you find and import books into your collection. These providers allow you to search for books by title, author, or ISBN, and import them directly into your Readloom collection.

## Available Book Providers

### Google Books API

The Google Books API provides access to millions of books from Google's vast database.

**Features:**
- Search by title, author, or ISBN
- Rich metadata including cover images, descriptions, and publication information
- Genre/category information
- Rating data (when available)
- More accurate and comprehensive data, especially for newer publications

**Configuration:**
- An API key is recommended for higher rate limits but not required
- You can get an API key from the [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- **Enabled by default** - this is the recommended provider for books

### Open Library API

Open Library is a free, open database of books maintained by the Internet Archive.

**Features:**
- Completely free and open data
- No API key required
- Extensive catalog of books
- Cover images for many books
- Publication information and ISBNs

**Configuration:**
- No configuration required - ready to use out of the box

### ISBNdb API

ISBNdb is a comprehensive database of books identified by ISBN.

**Features:**
- Detailed book information including dimensions and page counts
- Accurate publication data
- Publisher information
- ISBN lookup

**Configuration:**
- Requires an API key for access
- You can get an API key by signing up at [ISBNdb.com](https://isbndb.com/pricing)

### WorldCat API

WorldCat is a global catalog of library collections with millions of books from libraries worldwide.

**Features:**
- Extensive catalog with over 2 billion items from libraries around the world
- Academic and scholarly works well represented
- Detailed bibliographic information
- Library holdings information
- Multiple language support

**Configuration:**
- Requires an API key for access
- You can get an API key by signing up at the [OCLC Developer Network](https://www.oclc.org/developer/develop/web-services.en.html)

## Using Book Providers

### Enabling Providers

1. Go to Settings > Integrations
2. Click on "Configure" under Metadata Providers
3. Enable the book providers you want to use
4. Configure any required API keys

### Searching for Books

1. Go to the Search page
2. Enter a book title, author, or ISBN
3. Select a specific provider or search across all enabled providers
4. Browse the results and click "Details" to view more information

### Importing Books

1. From the book details page, click "Add to Collection"
2. The book will be added to your collection
3. If you have e-book files in your root folders that match the book, they will be automatically detected

## Provider Status Indicators

The provider configuration page shows status indicators for each provider:

- **Ready to Use**: The provider is enabled and doesn't need any additional configuration
- **Needs Configuration**: The provider requires additional configuration (like an API key)
- **Disabled**: The provider is currently disabled

## Troubleshooting

### API Key Issues

If you're having trouble with API keys:

1. Double-check that you've entered the key correctly
2. Verify that your API key is active and hasn't expired
3. Check if you've reached your API rate limits

### Search Issues

If you're not getting the results you expect:

1. Try different search terms
2. Try searching with a specific provider
3. For books with ISBNs, try searching by ISBN for more accurate results

### Import Issues

If you're having trouble importing books:

1. Make sure the provider is properly configured
2. Check that you have at least one collection set up
3. Verify that your root folders are properly linked to collections

## Best Practices

- **Use ISBNs when possible**: Searching by ISBN provides the most accurate results
- **Configure Google Books API key**: While optional, this will give you higher rate limits
- **Try multiple providers**: Different providers may have different information for the same book
- **Use Open Library for older books**: It has an extensive catalog of older and public domain books

## Related Documentation

- [Metadata Providers](METADATA_PROVIDERS.md) - General information about metadata providers
- [E-book Management](EBOOKS.md) - How e-book files are managed in Readloom
- [Collections](COLLECTIONS.md) - How to organize your books into collections
