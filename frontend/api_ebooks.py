#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from typing import Dict, List, Optional

from flask import (Blueprint, Response, jsonify, request,
                  send_file, url_for)

from backend.base.logging import LOGGER
from backend.features.ebook_files import (add_ebook_file, delete_ebook_file,
                                         get_ebook_file, get_ebook_files_for_series,
                                         get_ebook_files_for_volume, scan_for_ebooks)
from backend.internals.db import execute_query
from frontend.middleware import root_folders_required

# Create API blueprint
ebooks_api_bp = Blueprint('api_ebooks', __name__, url_prefix='/api/ebooks')


@ebooks_api_bp.route('/volume/<int:volume_id>', methods=['GET'])
def get_files_for_volume(volume_id: int):
    """Get e-book files for a volume.
    
    Args:
        volume_id (int): The volume ID.
        
    Returns:
        Response: The files.
    """
    try:
        # Check if volume exists
        volume = execute_query("SELECT id FROM volumes WHERE id = ?", (volume_id,))
        if not volume:
            return jsonify({"error": "Volume not found"}), 404
        
        files = get_ebook_files_for_volume(volume_id)
        return jsonify({"files": files})
    
    except Exception as e:
        LOGGER.error(f"Error getting e-book files for volume {volume_id}: {e}")
        return jsonify({"error": str(e)}), 500


@ebooks_api_bp.route('/series/<int:series_id>', methods=['GET'])
def get_files_for_series(series_id: int):
    """Get e-book files for a series.
    
    Args:
        series_id (int): The series ID.
        
    Returns:
        Response: The files.
    """
    try:
        # Check if series exists
        series = execute_query("SELECT id FROM series WHERE id = ?", (series_id,))
        if not series:
            return jsonify({"error": "Series not found"}), 404
        
        files = get_ebook_files_for_series(series_id)
        return jsonify({"files": files})
    
    except Exception as e:
        LOGGER.error(f"Error getting e-book files for series {series_id}: {e}")
        return jsonify({"error": str(e)}), 500


@ebooks_api_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload an e-book file.
    
    Returns:
        Response: The file information if successful.
    """
    try:
        # Check if required fields are provided
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        series_id = request.form.get('series_id')
        volume_id = request.form.get('volume_id')
        
        if not series_id or not volume_id:
            return jsonify({"error": "Missing series_id or volume_id"}), 400
        
        # Convert to integers
        try:
            series_id = int(series_id)
            volume_id = int(volume_id)
        except ValueError:
            return jsonify({"error": "Invalid series_id or volume_id"}), 400
        
        # Check if series and volume exist
        series = execute_query("SELECT id FROM series WHERE id = ?", (series_id,))
        if not series:
            return jsonify({"error": "Series not found"}), 404
            
        volume = execute_query("SELECT id FROM volumes WHERE id = ?", (volume_id,))
        if not volume:
            return jsonify({"error": "Volume not found"}), 404
        
        # Get the file
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Create a temporary file
        temp_file = Path(os.path.join("data", "temp", file.filename))
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the file temporarily
        file.save(temp_file)
        
        # Add the file to the database and storage
        file_type = request.form.get('file_type')
        file_info = add_ebook_file(series_id, volume_id, str(temp_file), file_type)
        
        # Delete the temporary file
        if temp_file.exists():
            os.remove(temp_file)
        
        if not file_info:
            return jsonify({"error": "Failed to add e-book file"}), 500
        
        return jsonify({"file": file_info}), 201
    
    except Exception as e:
        LOGGER.error(f"Error uploading e-book file: {e}")
        return jsonify({"error": str(e)}), 500


@ebooks_api_bp.route('/<int:file_id>', methods=['GET'])
def download_file(file_id: int):
    """Download an e-book file.
    
    Args:
        file_id (int): The file ID.
        
    Returns:
        Response: The file.
    """
    try:
        # Get the file info
        file_info = get_ebook_file(file_id)
        
        if not file_info:
            return jsonify({"error": "File not found"}), 404
        
        # Check if the file exists
        file_path = file_info.get('file_path')
        if not file_path or not os.path.exists(file_path):
            return jsonify({"error": "File not found on disk"}), 404
        
        # Send the file
        return send_file(
            file_path,
            download_name=file_info.get('original_name', file_info.get('file_name')),
            as_attachment=True
        )
    
    except Exception as e:
        LOGGER.error(f"Error downloading e-book file {file_id}: {e}")
        return jsonify({"error": str(e)}), 500


@ebooks_api_bp.route('/<int:file_id>', methods=['DELETE'])
def delete_file(file_id: int):
    """Delete an e-book file.
    
    Args:
        file_id (int): The file ID.
        
    Returns:
        Response: Success message.
    """
    try:
        # Check if the file exists
        file_info = get_ebook_file(file_id)
        
        if not file_info:
            return jsonify({"error": "File not found"}), 404
        
        # Delete the file
        if delete_ebook_file(file_id):
            return jsonify({"message": "File deleted successfully"})
        
        return jsonify({"error": "Failed to delete file"}), 500
    
    except Exception as e:
        LOGGER.error(f"Error deleting e-book file {file_id}: {e}")
        return jsonify({"error": str(e)}), 500


@ebooks_api_bp.route('/scan', methods=['POST'])
@root_folders_required
def scan_files():
    """Scan the data directory for e-book files and add them to the database.
    
    Returns:
        Response: Statistics about the scan.
    """
    try:
        # Check if a specific series ID is provided
        data = request.json or {}
        series_id = data.get('series_id')
        
        if series_id:
            try:
                series_id = int(series_id)
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid series ID"}), 400
                
            LOGGER.info(f"Scanning for e-books for series ID: {series_id}")
            stats = scan_for_ebooks(specific_series_id=series_id)
        else:
            LOGGER.info("Scanning for all e-books")
            stats = scan_for_ebooks()
            
        return jsonify({"stats": stats})
    
    except Exception as e:
        LOGGER.error(f"Error scanning for e-book files: {e}")
        return jsonify({"error": str(e)}), 500


@ebooks_api_bp.route('/content-types', methods=['GET'])
def get_content_types():
    """Get all content types.
    
    Returns:
        Response: The content types.
    """
    try:
        from backend.base.definitions import ContentType
        
        # Get all content types from the enum
        content_types = [{
            "id": content_type.name,
            "name": content_type.name.title(),
            "description": content_type.__doc__ or ""
        } for content_type in ContentType]
        
        return jsonify({"content_types": content_types})
    
    except Exception as e:
        LOGGER.error(f"Error getting content types: {e}")
        return jsonify({"error": str(e)}), 500


@ebooks_api_bp.route('/by-content-type/<content_type>', methods=['GET'])
def get_files_by_content_type(content_type: str):
    """Get e-book files by content type.
    
    Args:
        content_type (str): The content type.
        
    Returns:
        Response: The files.
    """
    try:
        # Get all series with the given content type
        series_list = execute_query("""
        SELECT id, title, content_type FROM series WHERE content_type = ?
        """, (content_type,))
        
        if not series_list:
            return jsonify({"files": []})
        
        # Get all files for these series
        all_files = []
        for series in series_list:
            series_files = get_ebook_files_for_series(series['id'])
            for file in series_files:
                file['series_title'] = series['title']
                file['content_type'] = series['content_type']
                all_files.append(file)
        
        return jsonify({"files": all_files})
    
    except Exception as e:
        LOGGER.error(f"Error getting e-book files for content type {content_type}: {e}")
        return jsonify({"error": str(e)}), 500
