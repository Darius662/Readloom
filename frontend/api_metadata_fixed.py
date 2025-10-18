#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for metadata services.
"""

from flask import Blueprint, request, jsonify

from backend.base.logging import LOGGER
from frontend.middleware import setup_required
from backend.features.metadata_service import (
    search_manga, get_manga_details, get_chapter_list, get_chapter_images,
    get_latest_releases, get_providers, update_provider, clear_cache,
    import_manga_to_collection
)


# Create a Blueprint for the metadata API
metadata_api_bp = Blueprint('metadata_api', __name__, url_prefix='/api/metadata')


@metadata_api_bp.route('/search', methods=['GET'])
def api_search_manga():
    """Search for manga or books.
    
    Returns:
        Response: The search results.
    """
    try:
        query = request.args.get('query', '')
        provider = request.args.get('provider', None)
        page = int(request.args.get('page', 1))
        search_type = request.args.get('search_type', 'title')
        
        # Validate search_type
        if search_type not in ['title', 'author']:
            return jsonify({"error": "Invalid search_type. Must be 'title' or 'author'"}), 400
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        results = search_manga(query, provider, page, search_type)
        
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
@setup_required
def api_import_manga(provider, manga_id):
    """Import a manga to the collection.
    
    Args:
        provider: The provider name.
        manga_id: The manga ID.
        
    Returns:
        Response: The result.
    """
    # Import LOGGER at the top of the function to ensure it's available in all code paths
    from backend.base.logging import LOGGER
    
    try:
        # Get optional overrides from request
        data = request.json or {}
        collection_id = data.get('collection_id')
        content_type = data.get('content_type')
        root_folder_id = data.get('root_folder_id')
        
        # Import the manga, passing optional parameters
        result = import_manga_to_collection(
            manga_id,
            provider,
            collection_id=collection_id,
            content_type=content_type,
            root_folder_id=root_folder_id,
        )
        
        if not result.get("success", False):
            # Check if it's because the series already exists
            if "already exists" in result.get("message", "").lower():
                # Get the series details to include folder information
                series_id = result.get("series_id")
                
                # Get the series folder path
                from backend.base.helpers import get_safe_folder_name
                from pathlib import Path
                from backend.internals.db import execute_query
                from backend.internals.settings import Settings
                
                # Get series title
                series_info = execute_query("SELECT title FROM series WHERE id = ?", (series_id,))
                if series_info:
                    series_title = series_info[0]['title']
                    safe_title = get_safe_folder_name(series_title)
                    
                    # Check if folder exists in any root folder
                    settings = Settings().get_settings()
                    root_folders = settings.root_folders
                    folder_path = None
                    
                    if root_folders:
                        for root_folder in root_folders:
                            root_path = Path(root_folder['path'])
                            potential_series_dir = root_path / safe_title
                            
                            if potential_series_dir.exists() and potential_series_dir.is_dir():
                                folder_path = str(potential_series_dir)
                                break
                    
                    # Return a 200 status with the series_id and folder information
                    return jsonify({
                        "success": False,
                        "already_exists": True,
                        "message": result.get("message", "Series already exists in the collection"),
                        "series_id": series_id,
                        "folder_path": folder_path
                    }), 200
                else:
                    # Return a 200 status with just the series_id
                    return jsonify({
                        "success": False,
                        "already_exists": True,
                        "message": result.get("message", "Series already exists in the collection"),
                        "series_id": series_id
                    }), 200
            # Otherwise it's a real error
            return jsonify(result), 400
        
        # Update the calendar to include the newly imported manga's release dates
        from backend.features.calendar import update_calendar
        
        # Log the import source
        LOGGER.info(f"Imported manga from {provider}, updating calendar...")
        
        # Make sure we update the calendar
        try:
            update_calendar()
            LOGGER.info(f"Calendar updated successfully after importing from {provider}")
        except Exception as e:
            LOGGER.error(f"Error updating calendar after import: {e}")
            # Continue anyway - we don't want to fail the import if calendar update fails
        
        # Get the folder path for the newly imported series
        series_id = result.get("series_id")
        folder_path = None
        
        if series_id:
            from backend.base.helpers import get_safe_folder_name
            from pathlib import Path
            from backend.internals.db import execute_query
            from backend.internals.settings import Settings
            
            # Get series title
            series_info = execute_query("SELECT title FROM series WHERE id = ?", (series_id,))
            if series_info:
                series_title = series_info[0]['title']
                safe_title = get_safe_folder_name(series_title)
                
                # Check if folder exists in any root folder
                settings = Settings().get_settings()
                root_folders = settings.root_folders
                
                if root_folders:
                    for root_folder in root_folders:
                        root_path = Path(root_folder['path'])
                        potential_series_dir = root_path / safe_title
                        
                        if potential_series_dir.exists() and potential_series_dir.is_dir():
                            folder_path = str(potential_series_dir)
                            break
        
        # Add folder path to the result
        result["folder_path"] = folder_path
        
        # Get e-book files for the series if any were found during import
        if series_id:
            from backend.features.ebook_files import get_ebook_files_for_series
            ebook_files = get_ebook_files_for_series(series_id)
            result["ebook_files_found"] = len(ebook_files)
        
        return jsonify(result)
    except Exception as e:
        LOGGER.error(f"Error in import manga API: {e}")
        return jsonify({"error": str(e)}), 500
