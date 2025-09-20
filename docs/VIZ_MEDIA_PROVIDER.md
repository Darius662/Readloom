# Viz Media Provider

## Overview

The Viz Media provider integrates with Viz Media's website to retrieve official manga release information. This provider is particularly valuable for tracking official release dates of manga published by Viz Media in the North American market.

## Features

### Search Functionality
- Search across Viz Media's extensive catalog of manga titles
- Results include volume information and cover images
- Intelligent volume number extraction from titles
- Automatic cover image retrieval

### Release Calendar
- Access to Viz Media's official release calendar
- Information about upcoming manga releases
- Support for different release formats (paperback, hardcover, digital)
- Release dates for planning your collection

### Cover Images
- High-quality official cover images from Viz Media's CDN
- Image caching to improve performance and reduce API load
- Predictive URL generation for cover images

## Technical Implementation

### Rate Limiting

The provider implements sophisticated rate limiting to avoid overwhelming Viz Media's servers:

```python
# Rate limiting properties
self.last_request_time = 0
self.min_request_interval = 0.5  # Minimum time between requests in seconds
self.request_lock = threading.Lock()  # Lock for thread safety

# In the request method
with self.request_lock:
    current_time = time.time()
    time_since_last_request = current_time - self.last_request_time
    
    if time_since_last_request < self.min_request_interval:
        # Sleep to respect rate limit
        sleep_time = self.min_request_interval - time_since_last_request
        self.logger.info(f"Rate limiting: Sleeping for {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
    
    self.last_request_time = time.time()
```

### Caching System

To minimize repeated requests and improve performance, the provider implements multi-level caching:

1. **Cover Image Caching**: Stores cover URLs to avoid repeated requests
2. **URL-based Cache**: Maps manga URLs to their corresponding cover images
3. **Product ID Cache**: Maps product IDs to cover images for cross-method reuse

### Smart Retries

The provider handles "Too Many Requests" (429) errors gracefully with backoff:

```python
# If we get a 429 (too many requests), retry with backoff
if response.status_code == 429:
    self.logger.warning(f"Received 429 Too Many Requests. Retrying with backoff...")
    time.sleep(2)  # Wait 2 seconds
    response = self.session.get(url, headers=self.headers, params=params, timeout=10)
```

## Usage

### Searching for Manga

```python
# Get the VizMedia provider
viz_provider = metadata_provider_manager.get_provider("VizMedia")

# Search for a manga
results = viz_provider.search("One Piece")

# Display results
for manga in results:
    print(f"Title: {manga['title']}, Volume: {manga['volume']}")
    print(f"Cover: {manga['cover_url']}")
    print("---")
```

### Getting Latest Releases

```python
# Get latest releases
releases = viz_provider.get_latest_releases()

# Display releases
for release in releases:
    print(f"Title: {release['manga_title']}")
    print(f"Format: {release['format']}")
    print(f"Release Date: {release['release_date']}")
    print("---")
```

### Accessing Calendar for Specific Month

```python
# Get releases for a specific month
releases = viz_provider.get_calendar_releases(2025, 9)  # September 2025

# Display calendar releases
for release in releases:
    print(f"Title: {release['manga_title']}")
    print(f"Release Date: {release['release_date']}")
    print("---")
```

## Benefits

- **Official Source**: Direct access to official release information from a major publisher
- **Reliable Release Dates**: Accurate release dates for planning purchases
- **High-Quality Cover Art**: Official cover images for enhanced UI presentation
- **Format Information**: Details about release formats (paperback, hardcover, digital)
- **Extensive Catalog**: Access to Viz Media's complete manga catalog

## Limitations

- **No Chapter Data**: Viz Media doesn't provide chapter-level information
- **Rate Limiting**: API usage is limited to avoid being blocked
- **Limited Metadata**: Less detailed metadata compared to dedicated manga databases
- **Regional Focus**: Primarily focused on North American releases

## Future Improvements

- Enhanced release date parsing for more precise calendar information
- Integration with Viz Media's digital reading platform data (if available)
- Support for author and genre filtering
- More robust error handling and fallback mechanisms
