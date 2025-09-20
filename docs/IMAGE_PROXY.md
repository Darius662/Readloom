# Image Proxy and Cover Display Solution

## Overview

This document describes the implementation of the image proxy solution for displaying external cover images in MangaARR.

## Problem

External cover images from sources like MangaDex were not displaying properly due to several issues:

1. **CORS Restrictions**: Browsers block loading of images from external domains due to security restrictions
2. **Incorrect URL Construction**: The URL format for MangaDex covers was not being constructed correctly
3. **Missing Fallback Images**: Empty fallback image files resulted in no image being displayed when loading failed

## Solution Components

### 1. Image Proxy Service

We implemented a Flask blueprint in `frontend/image_proxy.py` that provides a proxy endpoint for fetching external images:

```python
@image_proxy_bp.route('/image', methods=['GET'])
def proxy_image():
    """
    Proxy an external image to avoid CORS issues.
    """
    try:
        # Get the image URL from the query parameters
        image_url = request.args.get('url', '')
        
        if not image_url:
            return Response('Image URL is required', status=400)
        
        # URL might be URL-encoded, decode it
        image_url = unquote(image_url)
        
        # Make the request to the external image
        response = requests.get(image_url, headers=headers, stream=True, timeout=10)
        
        # Create a response with the image data and appropriate headers
        proxied_response = Response(
            response.content,
            status=response.status_code
        )
        
        # Add CORS headers
        proxied_response.headers['Access-Control-Allow-Origin'] = '*'
        
        return proxied_response
    
    except Exception as e:
        return Response(f"Error fetching image: {str(e)}", status=500)
```

### 2. Image Utility Function

We created a utility JavaScript function in `frontend/static/js/image-utils.js` to process image URLs:

```javascript
function processImageUrl(url) {
    // If no URL provided, use the fallback
    if (!url) {
        return '{{ url_for("ui.static", filename="img/no-cover.png") }}';
    }
    
    // If URL is already relative, just return it
    if (!url.startsWith('http')) {
        return url;
    }
    
    // Use the proxy for external URLs
    return `/api/proxy/image?url=${encodeURIComponent(url)}`;
}
```

### 3. Fallback Image

Created a proper fallback image at `frontend/static/img/no-cover.png` to display when image loading fails.

## Implementation Details

### Template Updates

We updated all templates that display cover images to use the image proxy:

#### 1. `search.html`
```javascript
// Process cover URL - use proxy for external images
let coverUrl = manga.cover_url || '/static/img/no-cover.png';
if (coverUrl && coverUrl.startsWith('http')) {
    coverUrl = `/api/proxy/image?url=${encodeURIComponent(coverUrl)}`;
}
```

#### 2. `series_list.html`
```html
<img src="${processImageUrl(series.cover_url)}" class="card-img-top" alt="${series.title}">
```

#### 3. `series_detail.html`
```html
<img src="${processImageUrl(series.cover_url)}" class="img-fluid rounded" alt="${series.title}">
```

#### 4. `collection.html`
```javascript
coverImg.src = processImageUrl(item.series_cover_url);
```

#### 5. `dashboard.html`
```javascript
// For upcoming releases section
img.src = processImageUrl(event.series.cover_url);

// For recent series section
img.src = processImageUrl(item.cover_url);
```

### Blueprint Registration

The image proxy blueprint was registered in the main application (`direct_app.py`):

```python
from frontend.image_proxy import image_proxy_bp
app.register_blueprint(image_proxy_bp)
```

## Usage

To use the image proxy in templates:

1. Add an external script tag for the utility:
   ```html
   <script src="/static/js/image-utils.js"></script>
   ```

2. Process image URLs using the utility function:
   ```javascript
   const imageUrl = processImageUrl(originalUrl);
   ```

3. Use the processed URL in img tags:
   ```html
   <img src="${imageUrl}" alt="Cover Image">
   ```

## Important Note on Fallback Images

When using Flask blueprints with static files, it's important to use the correct URL path for static resources. In our implementation, we initially encountered 404 errors when trying to load the fallback image because we were using an incorrect path.

### Initial Issue:
```javascript
// Incorrect path - causes 404 errors
return '/static/img/no-cover.png';
```

### Fixed Implementation:
```javascript
// Correct path using Flask's url_for function
return '{{ url_for("ui.static", filename="img/no-cover.png") }}';
```

The fix ensures that Flask generates the correct URL for the static file based on how the blueprint is registered, which prevents 404 errors and ensures the fallback image is always available.

## Benefits

- **Avoids CORS issues**: Images are fetched through the server, bypassing browser security restrictions
- **Consistent fallback**: Uses a standardized fallback image when loading fails
- **Centralized processing**: One function to handle all image URL processing
- **Improved caching**: Server can add appropriate cache headers to improve performance
- **Blueprint compatibility**: Works correctly with Flask's blueprint system

## Testing

All pages were tested to ensure cover images display correctly:
- Search results
- Series listing
- Series details
- Collection view
