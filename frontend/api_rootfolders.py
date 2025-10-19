#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from flask import Blueprint, jsonify, request

from backend.base.logging import LOGGER
from backend.internals.settings import Settings
from backend.base.custom_exceptions import InvalidSettingValue
from backend.base.folder_validation import validate_folder, create_folder_if_not_exists

# Create root folders API blueprint
rootfolders_api_bp = Blueprint('rootfolders_api', __name__, url_prefix='/api/rootfolders')


@rootfolders_api_bp.route('', methods=['GET'])
def get_root_folders():
    """Get all root folders.

    Returns:
        Response: The root folders.
    """
    try:
        settings = Settings().get_settings()
        return jsonify({"root_folders": settings.root_folders})
    
    except Exception as e:
        LOGGER.error(f"Error getting root folders: {e}")
        return jsonify({"error": str(e)}), 500


@rootfolders_api_bp.route('', methods=['POST'])
def add_root_folder():
    """Add a new root folder.

    Returns:
        Response: The updated root folders.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if "path" not in data or "name" not in data:
            return jsonify({"error": "Path and name are required"}), 400
        
        path = data["path"]
        name = data["name"]
        
        # Validate path exists and is writable
        validation = validate_folder(path)
        
        if not validation["exists"]:
            # Try to create the directory
            creation_result = create_folder_if_not_exists(path)
            if not creation_result["valid"]:
                LOGGER.error(f"Error creating root folder directory: {creation_result['message']}")
                return jsonify({"error": f"Path does not exist and could not be created: {path}"}), 400
            LOGGER.info(f"Created root folder directory: {path}")
        elif not validation["valid"]:
            return jsonify({"error": validation["message"]}), 400
        
        # Get current settings
        settings = Settings()
        current_settings = settings.get_settings()
        root_folders = list(current_settings.root_folders)  # Create a copy
        
        # Check if path already exists
        for folder in root_folders:
            if folder["path"] == path:
                return jsonify({"error": "Path already exists"}), 400
            if folder["name"] == name:
                return jsonify({"error": "Name already exists"}), 400
        
        # Add new root folder
        root_folders.append({"path": path, "name": name})
        
        # Update settings
        settings.update({"root_folders": root_folders})
        
        # Return updated root folders
        updated_settings = settings.get_settings()
        return jsonify({"root_folders": updated_settings.root_folders}), 201
    
    except InvalidSettingValue as e:
        return jsonify({"error": str(e)}), 400
    
    except Exception as e:
        LOGGER.error(f"Error adding root folder: {e}")
        return jsonify({"error": str(e)}), 500


@rootfolders_api_bp.route('/<int:index>', methods=['DELETE'])
def delete_root_folder(index: int):
    """Delete a root folder.

    Args:
        index (int): The index of the root folder to delete.

    Returns:
        Response: The updated root folders.
    """
    try:
        # Get current settings
        settings = Settings()
        current_settings = settings.get_settings()
        root_folders = list(current_settings.root_folders)  # Create a copy
        
        # Check if index is valid
        if index < 0 or index >= len(root_folders):
            return jsonify({"error": "Invalid root folder index"}), 400
        
        # Delete root folder
        deleted_folder = root_folders.pop(index)
        
        # Update settings
        settings.update({"root_folders": root_folders})
        
        # Return updated root folders
        updated_settings = settings.get_settings()
        return jsonify({
            "deleted": deleted_folder,
            "root_folders": updated_settings.root_folders
        })
    
    except InvalidSettingValue as e:
        return jsonify({"error": str(e)}), 400
    
    except Exception as e:
        LOGGER.error(f"Error deleting root folder: {e}")
        return jsonify({"error": str(e)}), 500


@rootfolders_api_bp.route('/check', methods=['POST'])
def check_path():
    """Check if a path exists and is a directory.

    Returns:
        Response: The path check result.
    """
    try:
        data = request.json
        if not data or "path" not in data:
            return jsonify({"error": "Path is required"}), 400
        
        path = data["path"]
        validation_result = validate_folder(path)
        
        result = {
            "path": path,
            "exists": validation_result["exists"],
            "is_dir": validation_result["exists"] and validation_result["valid"],
            "is_writable": validation_result["writable"],
            "message": validation_result["message"]
        }
        
        return jsonify(result)
    
    except Exception as e:
        LOGGER.error(f"Error checking path: {e}")
        return jsonify({"error": str(e)}), 500


@rootfolders_api_bp.route('/check-configured', methods=['GET'])
def check_configured():
    """Check if any root folders are configured.

    Returns:
        Response: Whether root folders are configured.
    """
    try:
        settings = Settings().get_settings()
        root_folders = settings.root_folders
        
        return jsonify({
            "configured": len(root_folders) > 0,
            "count": len(root_folders),
            "root_folders": root_folders
        })
    
    except Exception as e:
        LOGGER.error(f"Error checking if root folders are configured: {e}")
        return jsonify({"error": str(e)}), 500
