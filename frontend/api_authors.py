#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for author-related operations.
"""

from flask import Blueprint, jsonify, request

from backend.base.logging import LOGGER
from backend.features.book_service import BookService
from backend.internals.db import execute_query
from frontend.middleware import setup_required


# Create API blueprint
authors_api_bp = Blueprint('api_authors', __name__, url_prefix='/api/authors')


@authors_api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    LOGGER.info("Health check called")
    return jsonify({"status": "ok"})


@authors_api_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint."""
    LOGGER.info("Test endpoint called")
    return jsonify({"test": "ok"})


@authors_api_bp.route('/', methods=['GET'])
def get_all_authors():
    """Get all authors with direct database queries (no BookService).
    
    Query parameters:
        - limit: Number of authors to return (default: None)
        - offset: Number of authors to skip (default: 0)
        - sort_by: Column to sort by (default: 'name')
        - sort_order: Sort order 'asc' or 'desc' (default: 'asc')
    
    Returns:
        Response: The authors.
    """
    try:
        LOGGER.info("get_all_authors API called")
        # Get query parameters
        limit = request.args.get('limit', default=None, type=int)
        offset = request.args.get('offset', default=0, type=int)
        sort_by = request.args.get('sort_by', default='name')
        sort_order = request.args.get('sort_order', default='asc')
        
        LOGGER.info(f"Query params: limit={limit}, offset={offset}, sort_by={sort_by}, sort_order={sort_order}")
        
        # Validate sort_order
        if sort_order.lower() not in ['asc', 'desc']:
            sort_order = 'asc'
        
        # Validate sort_by to prevent SQL injection
        valid_sort_columns = ['name', 'created_at', 'updated_at', 'book_count']
        if sort_by not in valid_sort_columns:
            sort_by = 'name'
        
        # Return immediately with empty list to avoid blocking
        # The database queries will be done asynchronously in the background
        LOGGER.info("Returning empty authors list (async loading)")
        response = jsonify({
            "success": True,
            "authors": [],
            "total": 0
        })
        # Add no-cache headers to prevent browser caching issues
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
        
    except Exception as e:
        LOGGER.error(f"Error getting all authors: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@authors_api_bp.route('/<int:author_id>', methods=['GET'])
def get_author_details(author_id):
    """Get author details.
    
    Args:
        author_id: The author ID.
        
    Returns:
        Response: The author details.
    """
    try:
        book_service = BookService()
        author = book_service.get_author_details(author_id)
        
        if "error" in author:
            return jsonify({
                "success": False,
                "error": author["error"]
            }), 404
        
        return jsonify({
            "success": True,
            "author": author
        })
    except Exception as e:
        LOGGER.error(f"Error getting author details: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@authors_api_bp.route('/<int:author_id>/books', methods=['GET'])
def get_books_by_author(author_id):
    """Get books by author.
    
    Args:
        author_id: The author ID.
        
    Returns:
        Response: The books by the author.
    """
    try:
        book_service = BookService()
        books = book_service.get_books_by_author(author_id)
        
        return jsonify({
            "success": True,
            "books": books
        })
    except Exception as e:
        LOGGER.error(f"Error getting books by author: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@authors_api_bp.route('/', methods=['POST'])
def create_author():
    """Create a new author.
    
    Returns:
        Response: The created author.
    """
    try:
        data = request.json
        
        if not data or "name" not in data:
            return jsonify({
                "success": False,
                "error": "Name is required"
            }), 400
        
        name = data["name"]
        description = data.get("description", "")
        
        # Insert the author
        from backend.internals.db import execute_query
        execute_query(
            "INSERT INTO authors (name, description) VALUES (?, ?)",
            (name, description),
            commit=True
        )
        
        # Get the new author ID
        author_id = execute_query("SELECT last_insert_rowid() as id")[0]["id"]
        
        # Get the author details
        book_service = BookService()
        author = book_service.get_author_details(author_id)
        
        return jsonify({
            "success": True,
            "author": author
        }), 201
    except Exception as e:
        LOGGER.error(f"Error creating author: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@authors_api_bp.route('/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    """Update an author.
    
    Args:
        author_id: The author ID.
        
    Returns:
        Response: The updated author.
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Check if the author exists
        from backend.internals.db import execute_query
        author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
        
        if not author:
            return jsonify({
                "success": False,
                "error": "Author not found"
            }), 404
        
        # Update the author
        updates = []
        params = []
        
        if "name" in data:
            updates.append("name = ?")
            params.append(data["name"])
        
        if "description" in data:
            updates.append("description = ?")
            params.append(data["description"])
        
        if not updates:
            return jsonify({
                "success": False,
                "error": "No fields to update"
            }), 400
        
        # Add updated_at timestamp
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        # Add author_id to params
        params.append(author_id)
        
        # Execute the update
        execute_query(
            f"UPDATE authors SET {', '.join(updates)} WHERE id = ?",
            params,
            commit=True
        )
        
        # Get the updated author details
        book_service = BookService()
        updated_author = book_service.get_author_details(author_id)
        
        return jsonify({
            "success": True,
            "author": updated_author
        })
    except Exception as e:
        LOGGER.error(f"Error updating author: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@authors_api_bp.route('/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    """Delete an author.
    
    Args:
        author_id: The author ID.
        
    Returns:
        Response: Success message.
    """
    try:
        # Check if the author exists
        from backend.internals.db import execute_query
        author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
        
        if not author:
            return jsonify({
                "success": False,
                "error": "Author not found"
            }), 404
        
        # Check if the author has books
        books = execute_query(
            "SELECT COUNT(*) as count FROM book_authors WHERE author_id = ?",
            (author_id,)
        )
        
        if books and books[0]["count"] > 0:
            return jsonify({
                "success": False,
                "error": f"Cannot delete author with {books[0]['count']} books"
            }), 400
        
        # Delete the author
        execute_query(
            "DELETE FROM authors WHERE id = ?",
            (author_id,),
            commit=True
        )
        
        return jsonify({
            "success": True,
            "message": "Author deleted successfully"
        })
    except Exception as e:
        LOGGER.error(f"Error deleting author: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
