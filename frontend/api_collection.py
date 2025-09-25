#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for collection management.
"""

from flask import Blueprint, jsonify, request

from backend.base.logging import LOGGER
from backend.features.collection import (
    get_collections,
    get_collection_by_id,
    get_default_collection,
)

# Create Blueprint
collection_api = Blueprint('collection_api', __name__)


@collection_api.route('/api/collection/stats', methods=['GET'])
def api_get_collection_stats():
    """Get collection statistics."""
    try:
        # For now, return dummy stats
        stats = {
            "total_series": 7,  # Number of series found in your root folders
            "owned_volumes": 42,
            "read_volumes": 35,
            "total_value": 420.69
        }
        
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        LOGGER.error(f"Error getting collection stats: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collection_api.route('/api/collection/items', methods=['GET'])
def api_get_collection_items():
    """Get collection items with optional filtering."""
    try:
        # Get filter parameters
        type_filter = request.args.get('type')
        ownership_filter = request.args.get('ownership')
        read_status_filter = request.args.get('read_status')
        format_filter = request.args.get('format')
        
        # For now, return dummy items
        items = [
            {
                "id": 1,
                "series_id": 1,
                "title": "Berserk",
                "type": "SERIES",
                "ownership": "OWNED",
                "read_status": "READ",
                "format": "PHYSICAL",
                "purchase_date": "2023-01-15",
                "price": 12.99,
                "cover_url": "/static/img/no-cover.jpg"
            },
            {
                "id": 2,
                "series_id": 2,
                "title": "Chainsaw Man",
                "type": "SERIES",
                "ownership": "OWNED",
                "read_status": "READING",
                "format": "PHYSICAL",
                "purchase_date": "2023-02-20",
                "price": 9.99,
                "cover_url": "/static/img/no-cover.jpg"
            },
            {
                "id": 3,
                "series_id": 3,
                "title": "Dandadan",
                "type": "SERIES",
                "ownership": "OWNED",
                "read_status": "READING",
                "format": "DIGITAL",
                "purchase_date": "2023-03-10",
                "price": 7.99,
                "cover_url": "/static/img/no-cover.jpg"
            },
            {
                "id": 4,
                "series_id": 4,
                "title": "Kaiju No. 8",
                "type": "SERIES",
                "ownership": "OWNED",
                "read_status": "READING",
                "format": "PHYSICAL",
                "purchase_date": "2023-04-05",
                "price": 10.99,
                "cover_url": "/static/img/no-cover.jpg"
            },
            {
                "id": 5,
                "series_id": 5,
                "title": "Savage Hero",
                "type": "SERIES",
                "ownership": "WANTED",
                "read_status": "UNREAD",
                "format": "NONE",
                "purchase_date": None,
                "price": None,
                "cover_url": "/static/img/no-cover.jpg"
            },
            {
                "id": 6,
                "series_id": 6,
                "title": "Shangri-La Frontier",
                "type": "SERIES",
                "ownership": "ORDERED",
                "read_status": "UNREAD",
                "format": "PHYSICAL",
                "purchase_date": None,
                "price": 11.99,
                "cover_url": "/static/img/no-cover.jpg"
            },
            {
                "id": 7,
                "series_id": 7,
                "title": "So I'm a Spider, So What",
                "type": "SERIES",
                "ownership": "OWNED",
                "read_status": "READ",
                "format": "DIGITAL",
                "purchase_date": "2023-05-15",
                "price": 8.99,
                "cover_url": "/static/img/no-cover.jpg"
            }
        ]
        
        # Apply filters
        filtered_items = items
        if type_filter:
            filtered_items = [item for item in filtered_items if item["type"] == type_filter]
        if ownership_filter:
            filtered_items = [item for item in filtered_items if item["ownership"] == ownership_filter]
        if read_status_filter:
            filtered_items = [item for item in filtered_items if item["read_status"] == read_status_filter]
        if format_filter:
            filtered_items = [item for item in filtered_items if item["format"] == format_filter]
        
        return jsonify({
            "success": True,
            "items": filtered_items
        })
    except Exception as e:
        LOGGER.error(f"Error getting collection items: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collection_api.route('/api/collection/items/<int:item_id>', methods=['DELETE'])
def api_delete_collection_item(item_id):
    """Delete a collection item."""
    try:
        # In a real implementation, this would delete the item from the database
        LOGGER.info(f"Deleting collection item with ID {item_id}")
        
        return jsonify({
            "success": True,
            "message": f"Item {item_id} deleted successfully"
        })
    except Exception as e:
        LOGGER.error(f"Error deleting collection item {item_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collection_api.route('/api/collection/items', methods=['POST'])
def api_add_collection_item():
    """Add a new item to the collection."""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # In a real implementation, this would add the item to the database
        LOGGER.info(f"Adding new collection item: {data}")
        
        return jsonify({
            "success": True,
            "message": "Item added to collection successfully",
            "item_id": 999  # Dummy ID
        })
    except Exception as e:
        LOGGER.error(f"Error adding collection item: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collection_api.route('/api/collection/export', methods=['GET'])
def api_export_collection():
    """Export the collection data."""
    try:
        # In a real implementation, this would fetch all collection items
        # For now, return the same dummy data as in api_get_collection_items
        items = [
            {
                "id": 1,
                "series_id": 1,
                "title": "Berserk",
                "type": "SERIES",
                "ownership": "OWNED",
                "read_status": "READ",
                "format": "PHYSICAL",
                "purchase_date": "2023-01-15",
                "price": 12.99
            },
            # ... other items
        ]
        
        return jsonify({
            "success": True,
            "collection": items
        })
    except Exception as e:
        LOGGER.error(f"Error exporting collection: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@collection_api.route('/api/collection/import', methods=['POST'])
def api_import_collection():
    """Import collection data."""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # In a real implementation, this would import the items to the database
        LOGGER.info(f"Importing collection data with {len(data)} items")
        
        return jsonify({
            "success": True,
            "message": f"Successfully imported {len(data)} items"
        })
    except Exception as e:
        LOGGER.error(f"Error importing collection: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
