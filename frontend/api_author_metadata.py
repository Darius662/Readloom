#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API endpoints for author metadata.
"""

import logging
import requests
from flask import Blueprint, jsonify, request, current_app
from backend.features.metadata_providers.openlibrary.provider import OpenLibraryProvider
from backend.base.decorators import setup_required

# Set up logger
LOGGER = logging.getLogger(__name__)

# Create API blueprint
author_metadata_api_bp = Blueprint('api_author_metadata', __name__, url_prefix='/api/metadata/author')


@author_metadata_api_bp.route('/<provider>/<author_id>', methods=['GET'])
@setup_required
def get_author_details(provider, author_id):
    """Get author details from a specific provider.
    
    Args:
        provider: The provider name.
        author_id: The author ID.
        
    Returns:
        Response: The author details.
    """
    try:
        # Currently only supporting OpenLibrary
        if provider.lower() != 'openlibrary':
            return jsonify({
                "error": f"Provider {provider} not supported for author details"
            }), 400
        
        # Initialize OpenLibrary provider
        openlibrary_provider = OpenLibraryProvider(enabled=True)
        
        # Fetch author details from OpenLibrary
        author_url = f"{openlibrary_provider.base_url}/authors/{author_id}.json"
        response = requests.get(author_url, headers=openlibrary_provider.headers)
        
        if not response.ok:
            return jsonify({
                "error": f"Failed to fetch author details: {response.status_code}"
            }), response.status_code
        
        author_data = response.json()
        
        # Extract relevant information
        author_info = {
            "id": author_id,
            "name": author_data.get("name", "Unknown Author"),
            "birth_date": author_data.get("birth_date", "Unknown"),
            "death_date": author_data.get("death_date", ""),
            "biography": author_data.get("bio", {}).get("value", "") if isinstance(author_data.get("bio"), dict) else author_data.get("bio", ""),
            "wikipedia": author_data.get("wikipedia", ""),
            "personal_name": author_data.get("personal_name", ""),
            "alternate_names": author_data.get("alternate_names", []),
            "links": []
        }
        
        # Extract links
        if "links" in author_data and isinstance(author_data["links"], list):
            for link in author_data["links"]:
                if isinstance(link, dict) and "url" in link:
                    author_info["links"].append({
                        "title": link.get("title", "Link"),
                        "url": link["url"]
                    })
        
        # Get photo URL if available
        if "photos" in author_data and author_data["photos"] and len(author_data["photos"]) > 0:
            photo_id = author_data["photos"][0]
            author_info["image_url"] = f"https://covers.openlibrary.org/a/id/{photo_id}-L.jpg"
        else:
            author_info["image_url"] = "/static/img/no-cover.png"
        
        # Extract subject information if available
        author_info["subjects"] = []
        for field in ["subjects", "subject_places", "subject_times", "subject_people"]:
            if field in author_data:
                author_info["subjects"].extend(author_data[field])
        
        return jsonify(author_info)
        
    except Exception as e:
        LOGGER.error(f"Error getting author details: {e}")
        return jsonify({
            "error": f"Failed to get author details: {str(e)}"
        }), 500
