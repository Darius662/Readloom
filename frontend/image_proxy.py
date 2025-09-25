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
    'image/x-icon',
    'image/vnd.microsoft.icon',
    'image/bmp',
    'image/tiff'
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
            'Accept': 'image/*,*/*;q=0.8',  # Accept any content that might be an image
            'Referer': 'https://www.google.com/'  # Generic referer that most sites accept
        }
        
        # Make the request to the external image
        response = requests.get(image_url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Check if the response is an image
        content_type = response.headers.get('Content-Type', '')
        
        # More permissive check for image content types
        is_image = any(content_type.startswith(ct) for ct in IMAGE_CONTENT_TYPES)
        
        # If content type doesn't match but URL ends with image extension, consider it an image
        if not is_image:
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico', '.bmp', '.tiff']
            if any(image_url.lower().endswith(ext) for ext in image_extensions):
                is_image = True
                # If no content type was provided, guess based on extension
                if not content_type:
                    ext = image_url.lower().split('.')[-1]
                    if ext in ['jpg', 'jpeg']:
                        content_type = 'image/jpeg'
                    elif ext == 'png':
                        content_type = 'image/png'
                    elif ext == 'gif':
                        content_type = 'image/gif'
                    elif ext == 'webp':
                        content_type = 'image/webp'
                    elif ext == 'svg':
                        content_type = 'image/svg+xml'
                    elif ext in ['ico', 'icon']:
                        content_type = 'image/x-icon'
                    elif ext == 'bmp':
                        content_type = 'image/bmp'
                    elif ext in ['tiff', 'tif']:
                        content_type = 'image/tiff'
                    else:
                        content_type = 'image/jpeg'  # Default to JPEG
        
        # Special case for WorldCat and other providers that might return HTML with embedded images
        if not is_image and ('text/html' in content_type or 'application/xhtml+xml' in content_type):
            # Log the issue but don't block the request
            logging.warning(f"Proxy received HTML content from {image_url}, but will try to process it anyway")
            is_image = True  # Let it pass through
            
        if not is_image:
            logging.warning(f"Proxy requested non-image content: {content_type} from {image_url}")
            return Response('Not an image', status=400)
        
        # Create a response with the image data and appropriate headers
        proxied_response = Response(
            response.content,
            status=response.status_code
        )
        
        # Copy relevant headers
        for header in ['Content-Type', 'Content-Length', 'Cache-Control', 'Expires']:
            if header in response.headers:
                proxied_response.headers[header] = response.headers[header]
        
        # Add CORS headers
        proxied_response.headers['Access-Control-Allow-Origin'] = '*'
        
        # Add cache headers to improve performance
        if 'Cache-Control' not in proxied_response.headers:
            proxied_response.headers['Cache-Control'] = 'public, max-age=86400'  # Cache for 24 hours
        
        return proxied_response
    
    except requests.RequestException as e:
        logging.error(f"Error proxying image: {e}")
        return Response(f"Error fetching image: {str(e)}", status=500)
    
    except Exception as e:
        logging.error(f"Unexpected error in image proxy: {e}")
        return Response("Internal server error", status=500)
