#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API endpoints for author search.
"""

import logging
import requests
from flask import Blueprint, jsonify, request
from backend.features.metadata_providers.openlibrary.provider import OpenLibraryProvider
from backend.base.decorators import setup_required

# Set up logger
LOGGER = logging.getLogger(__name__)

# Create API blueprint
author_search_api_bp = Blueprint('api_author_search', __name__, url_prefix='/api/metadata/author_search')


@author_search_api_bp.route('', methods=['GET'])
@setup_required
def search_authors():
    """Search for authors.
    
    Returns:
        Response: The search results.
    """
    try:
        query = request.args.get('query', '')
        provider = request.args.get('provider', 'OpenLibrary')
        
        if not query:
            return jsonify({
                "error": "Query parameter is required"
            }), 400
        
        # Currently only supporting OpenLibrary
        if provider.lower() != 'openlibrary':
            return jsonify({
                "error": f"Provider {provider} not supported for author search"
            }), 400
        
        # Initialize OpenLibrary provider
        openlibrary_provider = OpenLibraryProvider(enabled=True)
        
        # Search for authors using OpenLibrary's author search API
        search_url = f"{openlibrary_provider.base_url}/search/authors.json"
        params = {"q": query}
        
        response = requests.get(search_url, params=params, headers=openlibrary_provider.headers)
        
        if not response.ok:
            return jsonify({
                "error": f"Failed to search authors: {response.status_code}"
            }), response.status_code
        
        search_data = response.json()
        
        # Process search results
        results = []
        if "docs" in search_data and search_data["docs"]:
            for author in search_data["docs"]:
                # Extract author key (ID)
                author_key = author.get("key", "")
                if author_key.startswith("/authors/"):
                    author_key = author_key[9:]  # Remove "/authors/" prefix
                
                # Get photo URL if available
                photo_url = "/static/img/no-cover.png"
                if "photos" in author and author["photos"] and len(author["photos"]) > 0:
                    photo_id = author["photos"][0]
                    photo_url = f"https://covers.openlibrary.org/a/id/{photo_id}-L.jpg"
                
                author_info = {
                    "id": author_key,
                    "name": author.get("name", "Unknown Author"),
                    "birth_date": author.get("birth_date", ""),
                    "death_date": author.get("death_date", ""),
                    "work_count": author.get("work_count", 0),
                    "top_work": author.get("top_work", ""),
                    "image_url": photo_url,
                    "is_author": True  # Flag to identify as an author result
                }
                
                results.append(author_info)
        
        return jsonify({
            "success": True,
            "results": {
                provider: results
            }
        })
        
    except Exception as e:
        LOGGER.error(f"Error searching authors: {e}")
        return jsonify({
            "error": f"Failed to search authors: {str(e)}"
        }), 500
