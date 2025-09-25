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
    'image/svg+xml'
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
            'User-Agent': 'Readloom/1.0.0 Image Proxy',
            'Accept': 'image/*',
            'Referer': 'https://mangadex.org/'  # Some sites check the referer
        }
        
        # Make the request to the external image
        response = requests.get(image_url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Check if the response is an image
        content_type = response.headers.get('Content-Type', '')
        is_image = any(content_type.startswith(ct) for ct in IMAGE_CONTENT_TYPES)
        
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
