#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for author-related operations.
"""

from flask import Blueprint, jsonify, request

from backend.base.logging import LOGGER
from backend.features.book_service import BookService
from frontend.middleware import setup_required


# Create API blueprint
authors_api_bp = Blueprint('api_authors', __name__, url_prefix='/api/authors')


@authors_api_bp.route('/', methods=['GET'])
@setup_required
def get_all_authors():
    """Get all authors.
    
    Returns:
        Response: The authors.
    """
    try:
        # Get query parameters
        limit = request.args.get('limit', default=None, type=int)
        offset = request.args.get('offset', default=0, type=int)
        sort_by = request.args.get('sort_by', default='name')
        sort_order = request.args.get('sort_order', default='asc')
        
        book_service = BookService()
        authors = book_service.get_all_authors()
        
        # Apply sorting
        if sort_by == 'book_count':
            authors = sorted(authors, key=lambda x: x.get('book_count', 0), reverse=(sort_order.lower() == 'desc'))
        elif sort_by == 'name':
            authors = sorted(authors, key=lambda x: x.get('name', '').lower(), reverse=(sort_order.lower() == 'desc'))
        elif sort_by == 'created_at':
            authors = sorted(authors, key=lambda x: x.get('created_at', ''), reverse=(sort_order.lower() == 'desc'))
        
        # Get total count before pagination
        total_count = len(authors)
        
        # Apply pagination
        if limit is not None:
            authors = authors[offset:offset + limit]
        
        return jsonify({
            "success": True,
            "authors": authors,
            "total": total_count
        })
    except Exception as e:
        LOGGER.error(f"Error getting all authors: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@authors_api_bp.route('/<int:author_id>', methods=['GET'])
@setup_required
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
@setup_required
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
@setup_required
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
@setup_required
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
@setup_required
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
