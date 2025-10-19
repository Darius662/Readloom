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
        
        # Use content_type for filtering
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


@api_series_bp.route('/api/series/recent', methods=['GET'])
@setup_required
def get_recent_series():
    """Get recent series.
    
    Returns:
        Response: The recent series.
    """
    try:
        # Get query parameters
        content_type = request.args.get('content_type', 'all')
        limit = request.args.get('limit', 10, type=int)
        
        # Build the query
        query = "SELECT s.* FROM series s"
        params = []
        
        # Add content type filter
        if content_type == 'book':
            query += " WHERE UPPER(s.content_type) IN ('BOOK', 'NOVEL')"
        elif content_type == 'manga':
            query += " WHERE UPPER(s.content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')"
        
        # Add order by and limit
        query += " ORDER BY s.created_at DESC LIMIT ?"
        params.append(limit)
        
        # Execute the query
        series = execute_query(query, params)
        
        return jsonify({
            "success": True,
            "series": series
        })
    except Exception as e:
        LOGGER.error(f"Error getting recent series: {e}")
        return jsonify({
            "success": False,
            "message": f"Error getting recent series: {str(e)}"
        }), 500
