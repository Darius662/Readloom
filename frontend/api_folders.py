#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for folder operations.
"""

from flask import Blueprint, jsonify, request

from backend.base.folder_validation import validate_folder, create_folder_if_not_exists
from backend.base.logging import LOGGER

folders_api = Blueprint('folders_api', __name__)


@folders_api.route('/api/folders/validate', methods=['POST'])
def validate_folder_endpoint():
    """Validate if a folder exists and is writable.
    
    Request JSON:
        {
            "path": "/path/to/folder"
        }
        
    Returns:
        JSON response with validation results.
    """
    data = request.json
    
    if not data or 'path' not in data:
        return jsonify({
            "success": False,
            "message": "Missing folder path"
        }), 400
    
    folder_path = data['path']
    result = validate_folder(folder_path)
    
    return jsonify({
        "success": result["valid"],
        "exists": result["exists"],
        "writable": result["writable"],
        "message": result["message"]
    })


@folders_api.route('/api/folders/create', methods=['POST'])
def create_folder_endpoint():
    """Create a folder if it doesn't exist and validate it.
    
    Request JSON:
        {
            "path": "/path/to/folder"
        }
        
    Returns:
        JSON response with creation and validation results.
    """
    data = request.json
    
    if not data or 'path' not in data:
        return jsonify({
            "success": False,
            "message": "Missing folder path"
        }), 400
    
    folder_path = data['path']
    result = create_folder_if_not_exists(folder_path)
    
    return jsonify({
        "success": result["valid"],
        "exists": result["exists"],
        "writable": result["writable"],
        "created": result["created"],
        "message": result["message"]
    })
