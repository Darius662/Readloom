#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced book import functionality that creates author folders.
"""

import os
from pathlib import Path
from flask import Blueprint, request, jsonify

from backend.base.logging import LOGGER
from backend.base.helpers import get_safe_folder_name
from backend.internals.db import execute_query
from backend.internals.settings import Settings
from frontend.middleware import setup_required

# Create a Blueprint for the enhanced book import API
enhanced_book_import_api_bp = Blueprint('api_enhanced_book_import', __name__, url_prefix='/api/metadata/enhanced_import')


@enhanced_book_import_api_bp.route('/<provider>/<book_id>', methods=['POST'])
@setup_required
def import_book_with_author_folder(provider, book_id):
    """Import a book to the collection and create an author folder.
    
    Args:
        provider: The provider name.
        book_id: The book ID.
        
    Returns:
        Response: The result.
    """
    try:
        # Get optional overrides from request
        data = request.json or {}
        collection_id = data.get('collection_id')
        content_type = data.get('content_type', 'BOOK')
        root_folder_id = data.get('root_folder_id')
        
        # Get book details from the provider
        from backend.features.metadata_service import get_manga_details
        book_data = get_manga_details(book_id, provider)
        
        if not book_data:
            return jsonify({
                "success": False,
                "message": "Failed to fetch book details"
            }), 400
        
        # Extract book and author information
        book_title = book_data.get('title', 'Unknown Book')
        author_name = book_data.get('author', 'Unknown Author')
        
        # Create safe folder names
        safe_author_name = get_safe_folder_name(author_name)
        safe_book_title = get_safe_folder_name(book_title)
        
        # Get the root folder to use
        settings = Settings().get_settings()
        root_folders = settings.root_folders
        
        if not root_folders:
            return jsonify({
                "success": False,
                "message": "No root folders configured"
            }), 400
        
        # Use the specified root folder or the first one
        root_folder = None
        if root_folder_id:
            for rf in root_folders:
                if rf['id'] == root_folder_id:
                    root_folder = rf
                    break
        
        if not root_folder:
            root_folder = root_folders[0]
        
        # Extract author ID from book data if available
        author_id = book_data.get('author_key', '')
        if not author_id and 'authors' in book_data and book_data['authors']:
            # Try to get author ID from the authors list
            for author in book_data['authors']:
                if 'key' in author:
                    # Extract the author ID from the key (format: /authors/OL123456A)
                    key_parts = author['key'].split('/')
                    if len(key_parts) > 1:
                        author_id = key_parts[-1]
                        break
        
        # Check if the author already exists in the database
        author_exists = execute_query(
            "SELECT id, folder_path FROM authors WHERE provider = ? AND provider_id = ?",
            (provider, author_id)
        ) if author_id else None
        
        # Create or get the author folder
        root_path = Path(root_folder['path'])
        author_folder_path = root_path / safe_author_name
        
        # If author exists, use their existing folder path
        if author_exists:
            author_db_id = author_exists[0]['id']
            existing_folder_path = author_exists[0]['folder_path']
            
            if existing_folder_path and Path(existing_folder_path).exists():
                author_folder_path = Path(existing_folder_path)
                LOGGER.info(f"Using existing author folder: {author_folder_path}")
            else:
                # If folder doesn't exist, create it
                try:
                    if not author_folder_path.exists():
                        author_folder_path.mkdir(parents=True, exist_ok=True)
                        LOGGER.info(f"Created author folder: {author_folder_path}")
                        
                        # Update the author record with the new folder path
                        execute_query(
                            "UPDATE authors SET folder_path = ? WHERE id = ?",
                            (str(author_folder_path), author_db_id)
                        )
                except Exception as e:
                    LOGGER.error(f"Error creating author folder: {e}")
                    return jsonify({
                        "success": False,
                        "message": f"Failed to create author folder: {str(e)}"
                    }), 500
        else:
            # Author doesn't exist, create the folder
            try:
                if not author_folder_path.exists():
                    author_folder_path.mkdir(parents=True, exist_ok=True)
                    LOGGER.info(f"Created author folder: {author_folder_path}")
            except Exception as e:
                LOGGER.error(f"Error creating author folder: {e}")
                return jsonify({
                    "success": False,
                    "message": f"Failed to create author folder: {str(e)}"
                }), 500
        
        # Create the book folder inside the author folder
        book_folder_path = author_folder_path / safe_book_title
        
        try:
            if not book_folder_path.exists():
                book_folder_path.mkdir(parents=True, exist_ok=True)
                LOGGER.info(f"Created book folder: {book_folder_path}")
        except Exception as e:
            LOGGER.error(f"Error creating book folder: {e}")
            return jsonify({
                "success": False,
                "message": f"Failed to create book folder: {str(e)}"
            }), 500
        
        # Now import the book using the standard import function
        from backend.features.metadata_service import import_manga_to_collection
        
        result = import_manga_to_collection(
            book_id,
            provider,
            collection_id=collection_id,
            content_type=content_type,
            root_folder_id=root_folder_id,
        )
        
        # Add folder paths to the result
        result["author_folder_path"] = str(author_folder_path)
        result["book_folder_path"] = str(book_folder_path)
        
        return jsonify(result)
        
    except Exception as e:
        LOGGER.error(f"Error importing book with author folder: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to import book: {str(e)}"
        }), 500
