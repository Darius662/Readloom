#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for metadata services.
"""

from flask import Blueprint, request, jsonify

from backend.base.logging import LOGGER
from backend.features.metadata_service import (
    search_manga, get_manga_details, get_chapter_list, get_chapter_images,
    get_latest_releases, get_providers, update_provider, clear_cache,
    import_manga_to_collection
)


# Create a Blueprint for the metadata API
metadata_api_bp = Blueprint('metadata_api', __name__)


@metadata_api_bp.route('/search', methods=['GET'])
def api_search_manga():
    """Search for manga.
    
    Returns:
        Response: The search results.
    """
    try:
        query = request.args.get('query', '')
        provider = request.args.get('provider', None)
        page = int(request.args.get('page', 1))
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        results = search_manga(query, provider, page)
        
        if "error" in results:
            return jsonify(results), 400
        
        return jsonify(results)
    except Exception as e:
        LOGGER.error(f"Error in search API: {e}")
        return jsonify({"error": str(e)}), 500


@metadata_api_bp.route('/manga/<provider>/<manga_id>', methods=['GET'])
def api_get_manga_details(provider, manga_id):
    """Get manga details.
    
    Args:
        provider: The provider name.
        manga_id: The manga ID.
        
    Returns:
        Response: The manga details.
    """
    try:
        details = get_manga_details(manga_id, provider)
        
        if "error" in details:
            return jsonify(details), 400
        
        return jsonify(details)
    except Exception as e:
        LOGGER.error(f"Error in manga details API: {e}")
        return jsonify({"error": str(e)}), 500


@metadata_api_bp.route('/manga/<provider>/<manga_id>/chapters', methods=['GET'])
def api_get_chapter_list(provider, manga_id):
    """Get chapter list.
    
    Args:
        provider: The provider name.
        manga_id: The manga ID.
        
    Returns:
        Response: The chapter list.
    """
    try:
        chapters = get_chapter_list(manga_id, provider)
        
        if "error" in chapters:
            return jsonify(chapters), 400
        
        return jsonify(chapters)
    except Exception as e:
        LOGGER.error(f"Error in chapter list API: {e}")
        return jsonify({"error": str(e)}), 500


@metadata_api_bp.route('/manga/<provider>/<manga_id>/chapter/<chapter_id>', methods=['GET'])
def api_get_chapter_images(provider, manga_id, chapter_id):
    """Get chapter images.
    
    Args:
        provider: The provider name.
        manga_id: The manga ID.
        chapter_id: The chapter ID.
        
    Returns:
        Response: The chapter images.
    """
    try:
        images = get_chapter_images(manga_id, chapter_id, provider)
        
        if "error" in images:
            return jsonify(images), 400
        
        return jsonify(images)
    except Exception as e:
        LOGGER.error(f"Error in chapter images API: {e}")
        return jsonify({"error": str(e)}), 500


@metadata_api_bp.route('/latest', methods=['GET'])
def api_get_latest_releases():
    """Get latest releases.
    
    Returns:
        Response: The latest releases.
    """
    try:
        provider = request.args.get('provider', None)
        page = int(request.args.get('page', 1))
        
        releases = get_latest_releases(provider, page)
        
        if "error" in releases:
            return jsonify(releases), 400
        
        return jsonify(releases)
    except Exception as e:
        LOGGER.error(f"Error in latest releases API: {e}")
        return jsonify({"error": str(e)}), 500


@metadata_api_bp.route('/providers', methods=['GET'])
def api_get_providers():
    """Get metadata providers.
    
    Returns:
        Response: The metadata providers.
    """
    try:
        providers = get_providers()
        
        if "error" in providers:
            return jsonify(providers), 400
        
        return jsonify(providers)
    except Exception as e:
        LOGGER.error(f"Error in providers API: {e}")
        return jsonify({"error": str(e)}), 500


@metadata_api_bp.route('/providers/<name>', methods=['PUT'])
def api_update_provider(name):
    """Update a metadata provider.
    
    Args:
        name: The provider name.
        
    Returns:
        Response: The result.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        enabled = data.get('enabled', True)
        settings = data.get('settings', {})
        
        result = update_provider(name, enabled, settings)
        
        if not result.get("success", False):
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        LOGGER.error(f"Error in update provider API: {e}")
        return jsonify({"error": str(e)}), 500


@metadata_api_bp.route('/cache', methods=['DELETE'])
def api_clear_cache():
    """Clear metadata cache.
    
    Returns:
        Response: The result.
    """
    try:
        provider = request.args.get('provider', None)
        type = request.args.get('type', None)
        
        result = clear_cache(provider, type)
        
        if not result.get("success", False):
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        LOGGER.error(f"Error in clear cache API: {e}")
        return jsonify({"error": str(e)}), 500


@metadata_api_bp.route('/import/<provider>/<manga_id>', methods=['POST'])
def api_import_manga(provider, manga_id):
    """Import a manga to the collection.
    
    Args:
        provider: The provider name.
        manga_id: The manga ID.
        
    Returns:
        Response: The result.
    """
    try:
        result = import_manga_to_collection(manga_id, provider)
        
        if not result.get("success", False):
            # Check if it's because the series already exists
            if "already exists" in result.get("message", "").lower():
                # Return a 200 status with the series_id for the UI to handle gracefully
                return jsonify({
                    "success": False,
                    "already_exists": True,
                    "message": result.get("message", "Series already exists in the collection"),
                    "series_id": result.get("series_id")
                }), 200
            # Otherwise it's a real error
            return jsonify(result), 400
        
        # Update the calendar to include the newly imported manga's release dates
        from backend.features.calendar import update_calendar
        update_calendar()
        
        return jsonify(result)
    except Exception as e:
        LOGGER.error(f"Error in import manga API: {e}")
        return jsonify({"error": str(e)}), 500
