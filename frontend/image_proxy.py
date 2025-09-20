#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Image proxy to handle external images and avoid CORS issues.
"""

from flask import Blueprint, request, Response
import requests
from urllib.parse import unquote
import logging

# Create a Blueprint for the image proxy
image_proxy_bp = Blueprint('image_proxy', __name__, url_prefix='/api/proxy')

# Common image content types
IMAGE_CONTENT_TYPES = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/svg+xml',
    'image/jpg',  # Some servers use this non-standard MIME type
    'application/octet-stream',  # Some CDNs use this for binary images
    'binary/octet-stream'  # Another variant used by some CDNs
]

@image_proxy_bp.route('/image', methods=['GET'])
def proxy_image():
    """
    Proxy an external image to avoid CORS issues.
    
    Query Parameters:
        url: The URL of the image to proxy.
        
    Returns:
        The image content with appropriate headers.
    """
    try:
        # Get the image URL from the query parameters
        image_url = request.args.get('url', '')
        
        if not image_url:
            return Response('Image URL is required', status=400)
        
        # URL might be URL-encoded, decode it
        image_url = unquote(image_url)
        
        # Set up headers for the request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/*,*/*;q=0.8',  # Accept more content types
        }
        
        # Use a dynamic referer based on the domain
        if 'mangadex.org' in image_url or 'uploads.mangadex.org' in image_url:
            headers['Referer'] = 'https://mangadex.org/'
        elif 'viz.com' in image_url or 'cloudfront.net' in image_url:
            headers['Referer'] = 'https://www.viz.com/'
        elif 'myanimelist.net' in image_url:
            headers['Referer'] = 'https://myanimelist.net/'
        
        # Make the request to the external image
        response = requests.get(image_url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Check if the response is an image
        content_type = response.headers.get('Content-Type', '')
        
        # More lenient check for image content
        is_image = any(content_type.startswith(ct) for ct in IMAGE_CONTENT_TYPES)
        
        # Special case for cloudfront.net and other CDNs that might return octet-stream
        if not is_image and ('cloudfront.net' in image_url or 'viz.com' in image_url):
            # If URL ends with common image extensions, consider it an image
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
            if any(image_url.lower().endswith(ext) for ext in image_extensions):
                is_image = True
                logging.info(f"Accepting response as image based on file extension: {image_url}")
        
        if not is_image:
            # Log the issue but still try to return the content if URL looks like an image
            logging.warning(f"Proxy requested possibly non-image content: {content_type} from {image_url}")
            
            # Last resort check - if URL looks like an image, try to return it anyway
            if '.jpg' in image_url or '.jpeg' in image_url or '.png' in image_url:
                logging.info(f"Attempting to return content as image despite content type: {image_url}")
                is_image = True
            else:
                return Response('Not an image', status=400)
        
        # Create a response with the image data and appropriate headers
        proxied_response = Response(
            response.content,
            status=response.status_code
        )
        
        # Copy relevant headers
        for header in ['Content-Type', 'Content-Length', 'Cache-Control', 'Expires', 'ETag', 'Last-Modified']:
            if header in response.headers:
                proxied_response.headers[header] = response.headers[header]
        
        # Add CORS headers
        proxied_response.headers['Access-Control-Allow-Origin'] = '*'
        
        # Add cache headers to improve performance
        if 'Cache-Control' not in proxied_response.headers:
            # Use longer cache time for Viz Media and cloudfront images since they change less frequently
            if 'cloudfront.net' in image_url or 'viz.com' in image_url:
                proxied_response.headers['Cache-Control'] = 'public, max-age=2592000'  # Cache for 30 days
            else:
                proxied_response.headers['Cache-Control'] = 'public, max-age=86400'  # Cache for 24 hours
        
        # Add a Vary header to ensure proper caching
        proxied_response.headers['Vary'] = 'Accept-Encoding'
        
        return proxied_response
    
    except requests.RequestException as e:
        logging.error(f"Error proxying image: {e}")
        return Response(f"Error fetching image: {str(e)}", status=500)
    
    except Exception as e:
        logging.error(f"Unexpected error in image proxy: {e}")
        return Response("Internal server error", status=500)
