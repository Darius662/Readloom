#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for series.
"""

from flask import Blueprint, jsonify, request

from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from frontend.middleware import setup_required


# Create Blueprint for series API
api_series_bp = Blueprint('api_series', __name__)


@api_series_bp.route('/api/series', methods=['GET'])
@setup_required
def get_all_series():
    """Get all series.
    
    Returns:
        Response: All series.
    """
    try:
        # Get content type filter
        content_type = request.args.get('content_type', None)
        
        # Try to use is_book column if it exists
        try:
            if content_type == 'book':
                series = execute_query("""
                    SELECT * FROM series WHERE is_book = 1 ORDER BY title
                """)
            elif content_type == 'manga':
                series = execute_query("""
                    SELECT * FROM series WHERE is_book = 0 ORDER BY title
                """)
            else:
                series = execute_query("""
                    SELECT * FROM series ORDER BY title
                """)
        except Exception:
            # Fallback to content_type if is_book doesn't exist
            if content_type == 'book':
                series = execute_query("""
                    SELECT * FROM series 
                    WHERE UPPER(content_type) IN ('BOOK', 'NOVEL')
                    ORDER BY title
                """)
            elif content_type == 'manga':
                series = execute_query("""
                    SELECT * FROM series 
                    WHERE UPPER(content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')
                    ORDER BY title
                """)
            else:
                series = execute_query("""
                    SELECT * FROM series ORDER BY title
                """)
        
        return jsonify({"series": series})
    except Exception as e:
        LOGGER.error(f"Error getting series: {e}")
        return jsonify({"error": str(e)}), 500


@api_series_bp.route('/api/series/<int:series_id>', methods=['GET'])
@setup_required
def get_series(series_id: int):
    """Get a series by ID.
    
    Args:
        series_id: The series ID.
        
    Returns:
        Response: The series.
    """
    try:
        series = execute_query("""
            SELECT * FROM series WHERE id = ?
        """, (series_id,))
        
        if not series:
            return jsonify({"error": "Series not found"}), 404
        
        return jsonify({"series": series[0]})
    except Exception as e:
        LOGGER.error(f"Error getting series: {e}")
        return jsonify({"error": str(e)}), 500
