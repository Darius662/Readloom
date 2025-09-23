#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for managing collections and root folders.
"""

from typing import Dict, List, Optional, Any, Union
import os
from pathlib import Path
import json

from flask import Blueprint, request, jsonify

from backend.base.custom_exceptions import InvalidCollectionError
from backend.base.logging import LOGGER
from backend.features.collection import (
    create_collection,
    get_collections,
    get_collection_by_id,
    update_collection,
    delete_collection,
    add_root_folder_to_collection,
    remove_root_folder_from_collection,
    get_collection_root_folders,
    create_root_folder,
    get_root_folders,
    get_root_folder_by_id,
    update_root_folder,
    delete_root_folder,
    add_series_to_collection,
    remove_series_from_collection,
    get_collection_series,
    get_default_collection,
)

# Create Blueprint
collections_api = Blueprint('collections_api', __name__)


@collections_api.route('/api/collections', methods=['GET'])
def api_get_collections():
    """Get all collections."""
    try:
        collections = get_collections()
        return jsonify({
            "success": True,
            "collections": collections
        })
    except Exception as e:
        LOGGER.error(f"Error getting collections: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collections_api.route('/api/collections/<int:collection_id>', methods=['GET'])
def api_get_collection(collection_id: int):
    """Get a collection by ID."""
    try:
        collection = get_collection_by_id(collection_id)
        if not collection:
            return jsonify({
                "success": False,
                "error": f"Collection with ID {collection_id} not found"
            }), 404
        
        return jsonify({
            "success": True,
            "collection": collection
        })
    except Exception as e:
        LOGGER.error(f"Error getting collection {collection_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collections_api.route('/api/collections', methods=['POST'])
def api_create_collection():
    """Create a new collection."""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        name = data.get('name')
        description = data.get('description', '')
        is_default = data.get('is_default', False)
        
        if not name:
            return jsonify({
                "success": False,
                "error": "Collection name is required"
            }), 400
        
        collection_id = create_collection(name, description, is_default)
        collection = get_collection_by_id(collection_id)
        
        return jsonify({
            "success": True,
            "message": f"Collection '{name}' created successfully",
            "collection": collection
        }), 201
    except InvalidCollectionError as e:
        LOGGER.error(f"Invalid collection error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        LOGGER.error(f"Error creating collection: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collections_api.route('/api/collections/<int:collection_id>', methods=['PUT'])
def api_update_collection(collection_id: int):
    """Update a collection."""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        name = data.get('name')
        description = data.get('description')
        is_default = data.get('is_default')
        
        updated = update_collection(collection_id, name, description, is_default)
        if not updated:
            return jsonify({
                "success": True,
                "message": "No changes made to collection"
            })
        
        collection = get_collection_by_id(collection_id)
        
        return jsonify({
            "success": True,
            "message": f"Collection updated successfully",
            "collection": collection
        })
    except InvalidCollectionError as e:
        LOGGER.error(f"Invalid collection error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        LOGGER.error(f"Error updating collection {collection_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collections_api.route('/api/collections/<int:collection_id>', methods=['DELETE'])
def api_delete_collection(collection_id: int):
    """Delete a collection."""
    try:
        deleted = delete_collection(collection_id)
        
        return jsonify({
            "success": True,
            "message": f"Collection deleted successfully"
        })
    except InvalidCollectionError as e:
        LOGGER.error(f"Invalid collection error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        LOGGER.error(f"Error deleting collection {collection_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collections_api.route('/api/collections/default', methods=['GET'])
def api_get_default_collection():
    """Get the default collection."""
    try:
        collection = get_default_collection()
        return jsonify({
            "success": True,
            "collection": collection
        })
    except Exception as e:
        LOGGER.error(f"Error getting default collection: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Root Folder Endpoints

@collections_api.route('/api/root-folders', methods=['GET'])
def api_get_root_folders():
    """Get all root folders."""
    try:
        root_folders = get_root_folders()
        return jsonify({
            "success": True,
            "root_folders": root_folders
        })
    except Exception as e:
        LOGGER.error(f"Error getting root folders: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collections_api.route('/api/root-folders/<int:root_folder_id>', methods=['GET'])
def api_get_root_folder(root_folder_id: int):
    """Get a root folder by ID."""
    try:
        root_folder = get_root_folder_by_id(root_folder_id)
        if not root_folder:
            return jsonify({
                "success": False,
                "error": f"Root folder with ID {root_folder_id} not found"
            }), 404
        
        return jsonify({
            "success": True,
            "root_folder": root_folder
        })
    except Exception as e:
        LOGGER.error(f"Error getting root folder {root_folder_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collections_api.route('/api/root-folders', methods=['POST'])
def api_create_root_folder():
    """Create a new root folder."""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        path = data.get('path')
        name = data.get('name')
        content_type = data.get('content_type', 'MANGA')
        
        if not path or not name:
            return jsonify({
                "success": False,
                "error": "Root folder path and name are required"
            }), 400
        
        root_folder_id = create_root_folder(path, name, content_type)
        root_folder = get_root_folder_by_id(root_folder_id)
        
        return jsonify({
            "success": True,
            "message": f"Root folder '{name}' created successfully",
            "root_folder": root_folder
        }), 201
    except InvalidCollectionError as e:
        LOGGER.error(f"Invalid root folder error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        LOGGER.error(f"Error creating root folder: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collections_api.route('/api/root-folders/<int:root_folder_id>', methods=['PUT'])
def api_update_root_folder(root_folder_id: int):
    """Update a root folder."""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        path = data.get('path')
        name = data.get('name')
        content_type = data.get('content_type')
        
        updated = update_root_folder(root_folder_id, path, name, content_type)
        if not updated:
            return jsonify({
                "success": True,
                "message": "No changes made to root folder"
            })
        
        root_folder = get_root_folder_by_id(root_folder_id)
        
        return jsonify({
            "success": True,
            "message": f"Root folder updated successfully",
            "root_folder": root_folder
        })
    except InvalidCollectionError as e:
        LOGGER.error(f"Invalid root folder error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        LOGGER.error(f"Error updating root folder {root_folder_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collections_api.route('/api/root-folders/<int:root_folder_id>', methods=['DELETE'])
def api_delete_root_folder(root_folder_id: int):
    """Delete a root folder."""
    try:
        deleted = delete_root_folder(root_folder_id)
        
        return jsonify({
            "success": True,
            "message": f"Root folder deleted successfully"
        })
    except InvalidCollectionError as e:
        LOGGER.error(f"Invalid root folder error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        LOGGER.error(f"Error deleting root folder {root_folder_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Collection-Root Folder Relationship Endpoints

@collections_api.route('/api/collections/<int:collection_id>/root-folders', methods=['GET'])
def api_get_collection_root_folders(collection_id: int):
    """Get all root folders for a collection."""
    try:
        root_folders = get_collection_root_folders(collection_id)
        return jsonify({
            "success": True,
            "root_folders": root_folders
        })
    except InvalidCollectionError as e:
        LOGGER.error(f"Invalid collection error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        LOGGER.error(f"Error getting root folders for collection {collection_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collections_api.route('/api/collections/<int:collection_id>/root-folders/<int:root_folder_id>', methods=['POST'])
def api_add_root_folder_to_collection(collection_id: int, root_folder_id: int):
    """Add a root folder to a collection."""
    try:
        added = add_root_folder_to_collection(collection_id, root_folder_id)
        
        if not added:
            return jsonify({
                "success": True,
                "message": "Root folder is already in the collection"
            })
        
        return jsonify({
            "success": True,
            "message": f"Root folder added to collection successfully"
        })
    except InvalidCollectionError as e:
        LOGGER.error(f"Invalid collection or root folder error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        LOGGER.error(f"Error adding root folder {root_folder_id} to collection {collection_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collections_api.route('/api/collections/<int:collection_id>/root-folders/<int:root_folder_id>', methods=['DELETE'])
def api_remove_root_folder_from_collection(collection_id: int, root_folder_id: int):
    """Remove a root folder from a collection."""
    try:
        removed = remove_root_folder_from_collection(collection_id, root_folder_id)
        
        return jsonify({
            "success": True,
            "message": f"Root folder removed from collection successfully"
        })
    except InvalidCollectionError as e:
        LOGGER.error(f"Invalid collection or root folder error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        LOGGER.error(f"Error removing root folder {root_folder_id} from collection {collection_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Collection-Series Relationship Endpoints

@collections_api.route('/api/collections/<int:collection_id>/series', methods=['GET'])
def api_get_collection_series(collection_id: int):
    """Get all series for a collection."""
    try:
        series = get_collection_series(collection_id)
        return jsonify({
            "success": True,
            "series": series
        })
    except InvalidCollectionError as e:
        LOGGER.error(f"Invalid collection error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        LOGGER.error(f"Error getting series for collection {collection_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collections_api.route('/api/collections/<int:collection_id>/series/<int:series_id>', methods=['POST'])
def api_add_series_to_collection(collection_id: int, series_id: int):
    """Add a series to a collection."""
    try:
        added = add_series_to_collection(collection_id, series_id)
        
        if not added:
            return jsonify({
                "success": True,
                "message": "Series is already in the collection"
            })
        
        return jsonify({
            "success": True,
            "message": f"Series added to collection successfully"
        })
    except InvalidCollectionError as e:
        LOGGER.error(f"Invalid collection or series error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        LOGGER.error(f"Error adding series {series_id} to collection {collection_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collections_api.route('/api/collections/<int:collection_id>/series/<int:series_id>', methods=['DELETE'])
def api_remove_series_from_collection(collection_id: int, series_id: int):
    """Remove a series from a collection."""
    try:
        removed = remove_series_from_collection(collection_id, series_id)
        
        return jsonify({
            "success": True,
            "message": f"Series removed from collection successfully"
        })
    except InvalidCollectionError as e:
        LOGGER.error(f"Invalid collection or series error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        LOGGER.error(f"Error removing series {series_id} from collection {collection_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
