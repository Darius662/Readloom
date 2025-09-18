#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from flask import Blueprint, Response, jsonify, request

from backend.base.custom_exceptions import (APIError, DatabaseError,
                                           InvalidSettingValue, MetadataError)
from backend.base.logging import LOGGER
from backend.features.calendar import get_calendar_events, update_calendar
from backend.internals.db import execute_query
from backend.internals.settings import Settings

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.errorhandler(Exception)
def handle_error(error):
    """Handle errors in the API.

    Args:
        error (Exception): The error to handle.

    Returns:
        Response: The error response.
    """
    if isinstance(error, APIError):
        return jsonify({"error": str(error)}), 400
    elif isinstance(error, DatabaseError):
        return jsonify({"error": f"Database error: {str(error)}"}), 500
    elif isinstance(error, MetadataError):
        return jsonify({"error": f"Metadata error: {str(error)}"}), 400
    elif isinstance(error, InvalidSettingValue):
        return jsonify({"error": f"Invalid setting: {str(error)}"}), 400
    else:
        LOGGER.error(f"Unhandled API error: {error}")
        return jsonify({"error": "Internal server error"}), 500


# Calendar endpoints
@api_bp.route('/calendar', methods=['GET'])
def get_calendar():
    """Get calendar events.

    Returns:
        Response: The calendar events.
    """
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        series_id = request.args.get('series_id')
        
        # Convert series_id to int if provided
        if series_id:
            try:
                series_id = int(series_id)
            except ValueError:
                return jsonify({"error": "Invalid series ID"}), 400
        
        # If no dates provided, use default range
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        if not end_date:
            settings = Settings().get_settings()
            end_date = (datetime.now() + timedelta(days=settings.calendar_range_days)).strftime('%Y-%m-%d')
        
        events = get_calendar_events(start_date, end_date, series_id)
        return jsonify({"events": events})
    
    except Exception as e:
        LOGGER.error(f"Error getting calendar: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/calendar/refresh', methods=['POST'])
def refresh_calendar():
    """Refresh the calendar.

    Returns:
        Response: Success message.
    """
    try:
        update_calendar()
        return jsonify({"message": "Calendar refreshed successfully"})
    
    except Exception as e:
        LOGGER.error(f"Error refreshing calendar: {e}")
        return jsonify({"error": str(e)}), 500


# Series endpoints
@api_bp.route('/series', methods=['GET'])
def get_series_list():
    """Get all series.

    Returns:
        Response: The series list.
    """
    try:
        series = execute_query("""
        SELECT 
            id, title, description, author, publisher, cover_url, status, 
            metadata_source, metadata_id, created_at, updated_at
        FROM series
        ORDER BY title
        """)
        
        return jsonify({"series": series})
    
    except Exception as e:
        LOGGER.error(f"Error getting series list: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/series/<int:series_id>', methods=['GET'])
def get_series(series_id: int):
    """Get a specific series.

    Args:
        series_id (int): The series ID.

    Returns:
        Response: The series.
    """
    try:
        series = execute_query("""
        SELECT 
            id, title, description, author, publisher, cover_url, status, 
            metadata_source, metadata_id, created_at, updated_at
        FROM series
        WHERE id = ?
        """, (series_id,))
        
        if not series:
            return jsonify({"error": "Series not found"}), 404
        
        # Get volumes for this series
        volumes = execute_query("""
        SELECT 
            id, volume_number, title, description, cover_url, release_date, 
            created_at, updated_at
        FROM volumes
        WHERE series_id = ?
        ORDER BY CAST(volume_number AS REAL)
        """, (series_id,))
        
        # Get chapters for this series
        chapters = execute_query("""
        SELECT 
            id, volume_id, chapter_number, title, description, release_date, 
            status, read_status, created_at, updated_at
        FROM chapters
        WHERE series_id = ?
        ORDER BY CAST(chapter_number AS REAL)
        """, (series_id,))
        
        # Get upcoming calendar events
        events = get_calendar_events(
            start_date=datetime.now().strftime('%Y-%m-%d'),
            series_id=series_id
        )
        
        result = {
            "series": series[0],
            "volumes": volumes,
            "chapters": chapters,
            "upcoming_events": events
        }
        
        return jsonify(result)
    
    except Exception as e:
        LOGGER.error(f"Error getting series {series_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/series', methods=['POST'])
def add_series():
    """Add a new series.

    Returns:
        Response: The created series.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ["title"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Insert the series
        series_id = execute_query("""
        INSERT INTO series (
            title, description, author, publisher, cover_url, status, 
            metadata_source, metadata_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("title"),
            data.get("description"),
            data.get("author"),
            data.get("publisher"),
            data.get("cover_url"),
            data.get("status"),
            data.get("metadata_source"),
            data.get("metadata_id")
        ), commit=True)
        
        # Get the created series
        series = execute_query("""
        SELECT 
            id, title, description, author, publisher, cover_url, status, 
            metadata_source, metadata_id, created_at, updated_at
        FROM series
        WHERE id = last_insert_rowid()
        """)
        
        return jsonify({"series": series[0]}), 201
    
    except Exception as e:
        LOGGER.error(f"Error adding series: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/series/<int:series_id>', methods=['PUT'])
def update_series(series_id: int):
    """Update a series.

    Args:
        series_id (int): The series ID.

    Returns:
        Response: The updated series.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Check if series exists
        series = execute_query("SELECT id FROM series WHERE id = ?", (series_id,))
        if not series:
            return jsonify({"error": "Series not found"}), 404
        
        # Build update query
        update_fields = []
        params = []
        
        for field in ["title", "description", "author", "publisher", "cover_url", "status", "metadata_source", "metadata_id"]:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
        
        # Add updated_at and series_id
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(series_id)
        
        # Execute update
        execute_query(f"""
        UPDATE series
        SET {", ".join(update_fields)}
        WHERE id = ?
        """, tuple(params), commit=True)
        
        # Get the updated series
        updated_series = execute_query("""
        SELECT 
            id, title, description, author, publisher, cover_url, status, 
            metadata_source, metadata_id, created_at, updated_at
        FROM series
        WHERE id = ?
        """, (series_id,))
        
        return jsonify({"series": updated_series[0]})
    
    except Exception as e:
        LOGGER.error(f"Error updating series {series_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/series/<int:series_id>', methods=['DELETE'])
def delete_series(series_id: int):
    """Delete a series.

    Args:
        series_id (int): The series ID.

    Returns:
        Response: Success message.
    """
    try:
        # Check if series exists
        series = execute_query("SELECT id FROM series WHERE id = ?", (series_id,))
        if not series:
            return jsonify({"error": "Series not found"}), 404
        
        # Delete the series (cascade will delete volumes, chapters, and events)
        execute_query("DELETE FROM series WHERE id = ?", (series_id,), commit=True)
        
        return jsonify({"message": "Series deleted successfully"})
    
    except Exception as e:
        LOGGER.error(f"Error deleting series {series_id}: {e}")
        return jsonify({"error": str(e)}), 500


# Volume endpoints
@api_bp.route('/series/<int:series_id>/volumes', methods=['POST'])
def add_volume(series_id: int):
    """Add a volume to a series.

    Args:
        series_id (int): The series ID.

    Returns:
        Response: The created volume.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ["volume_number"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if series exists
        series = execute_query("SELECT id FROM series WHERE id = ?", (series_id,))
        if not series:
            return jsonify({"error": "Series not found"}), 404
        
        # Insert the volume
        volume_id = execute_query("""
        INSERT INTO volumes (
            series_id, volume_number, title, description, cover_url, release_date
        ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            series_id,
            data.get("volume_number"),
            data.get("title"),
            data.get("description"),
            data.get("cover_url"),
            data.get("release_date")
        ), commit=True)
        
        # Get the created volume
        volume = execute_query("""
        SELECT 
            id, series_id, volume_number, title, description, cover_url, 
            release_date, created_at, updated_at
        FROM volumes
        WHERE id = last_insert_rowid()
        """)
        
        # Update calendar if release date is provided
        if data.get("release_date"):
            update_calendar()
        
        return jsonify({"volume": volume[0]}), 201
    
    except Exception as e:
        LOGGER.error(f"Error adding volume to series {series_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/volumes/<int:volume_id>', methods=['PUT'])
def update_volume(volume_id: int):
    """Update a volume.

    Args:
        volume_id (int): The volume ID.

    Returns:
        Response: The updated volume.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Check if volume exists
        volume = execute_query("SELECT id FROM volumes WHERE id = ?", (volume_id,))
        if not volume:
            return jsonify({"error": "Volume not found"}), 404
        
        # Build update query
        update_fields = []
        params = []
        
        for field in ["volume_number", "title", "description", "cover_url", "release_date"]:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
        
        # Add updated_at and volume_id
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(volume_id)
        
        # Execute update
        execute_query(f"""
        UPDATE volumes
        SET {", ".join(update_fields)}
        WHERE id = ?
        """, tuple(params), commit=True)
        
        # Get the updated volume
        updated_volume = execute_query("""
        SELECT 
            id, series_id, volume_number, title, description, cover_url, 
            release_date, created_at, updated_at
        FROM volumes
        WHERE id = ?
        """, (volume_id,))
        
        # Update calendar if release date was updated
        if "release_date" in data:
            update_calendar()
        
        return jsonify({"volume": updated_volume[0]})
    
    except Exception as e:
        LOGGER.error(f"Error updating volume {volume_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/volumes/<int:volume_id>', methods=['DELETE'])
def delete_volume(volume_id: int):
    """Delete a volume.

    Args:
        volume_id (int): The volume ID.

    Returns:
        Response: Success message.
    """
    try:
        # Check if volume exists
        volume = execute_query("SELECT id FROM volumes WHERE id = ?", (volume_id,))
        if not volume:
            return jsonify({"error": "Volume not found"}), 404
        
        # Delete the volume
        execute_query("DELETE FROM volumes WHERE id = ?", (volume_id,), commit=True)
        
        # Update calendar to remove events for this volume
        update_calendar()
        
        return jsonify({"message": "Volume deleted successfully"})
    
    except Exception as e:
        LOGGER.error(f"Error deleting volume {volume_id}: {e}")
        return jsonify({"error": str(e)}), 500


# Chapter endpoints
@api_bp.route('/series/<int:series_id>/chapters', methods=['POST'])
def add_chapter(series_id: int):
    """Add a chapter to a series.

    Args:
        series_id (int): The series ID.

    Returns:
        Response: The created chapter.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ["chapter_number"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if series exists
        series = execute_query("SELECT id FROM series WHERE id = ?", (series_id,))
        if not series:
            return jsonify({"error": "Series not found"}), 404
        
        # Check if volume exists if provided
        volume_id = data.get("volume_id")
        if volume_id:
            volume = execute_query("SELECT id FROM volumes WHERE id = ?", (volume_id,))
            if not volume:
                return jsonify({"error": "Volume not found"}), 404
        
        # Insert the chapter
        chapter_id = execute_query("""
        INSERT INTO chapters (
            series_id, volume_id, chapter_number, title, description, 
            release_date, status, read_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            series_id,
            volume_id,
            data.get("chapter_number"),
            data.get("title"),
            data.get("description"),
            data.get("release_date"),
            data.get("status"),
            data.get("read_status", "UNREAD")
        ), commit=True)
        
        # Get the created chapter
        chapter = execute_query("""
        SELECT 
            id, series_id, volume_id, chapter_number, title, description, 
            release_date, status, read_status, created_at, updated_at
        FROM chapters
        WHERE id = last_insert_rowid()
        """)
        
        # Update calendar if release date is provided
        if data.get("release_date"):
            update_calendar()
        
        return jsonify({"chapter": chapter[0]}), 201
    
    except Exception as e:
        LOGGER.error(f"Error adding chapter to series {series_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
def update_chapter(chapter_id: int):
    """Update a chapter.

    Args:
        chapter_id (int): The chapter ID.

    Returns:
        Response: The updated chapter.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Check if chapter exists
        chapter = execute_query("SELECT id FROM chapters WHERE id = ?", (chapter_id,))
        if not chapter:
            return jsonify({"error": "Chapter not found"}), 404
        
        # Check if volume exists if provided
        volume_id = data.get("volume_id")
        if volume_id:
            volume = execute_query("SELECT id FROM volumes WHERE id = ?", (volume_id,))
            if not volume:
                return jsonify({"error": "Volume not found"}), 404
        
        # Build update query
        update_fields = []
        params = []
        
        for field in ["volume_id", "chapter_number", "title", "description", "release_date", "status", "read_status"]:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
        
        # Add updated_at and chapter_id
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(chapter_id)
        
        # Execute update
        execute_query(f"""
        UPDATE chapters
        SET {", ".join(update_fields)}
        WHERE id = ?
        """, tuple(params), commit=True)
        
        # Get the updated chapter
        updated_chapter = execute_query("""
        SELECT 
            id, series_id, volume_id, chapter_number, title, description, 
            release_date, status, read_status, created_at, updated_at
        FROM chapters
        WHERE id = ?
        """, (chapter_id,))
        
        # Update calendar if release date was updated
        if "release_date" in data:
            update_calendar()
        
        return jsonify({"chapter": updated_chapter[0]})
    
    except Exception as e:
        LOGGER.error(f"Error updating chapter {chapter_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/chapters/<int:chapter_id>', methods=['DELETE'])
def delete_chapter(chapter_id: int):
    """Delete a chapter.

    Args:
        chapter_id (int): The chapter ID.

    Returns:
        Response: Success message.
    """
    try:
        # Check if chapter exists
        chapter = execute_query("SELECT id FROM chapters WHERE id = ?", (chapter_id,))
        if not chapter:
            return jsonify({"error": "Chapter not found"}), 404
        
        # Delete the chapter
        execute_query("DELETE FROM chapters WHERE id = ?", (chapter_id,), commit=True)
        
        # Update calendar to remove events for this chapter
        update_calendar()
        
        return jsonify({"message": "Chapter deleted successfully"})
    
    except Exception as e:
        LOGGER.error(f"Error deleting chapter {chapter_id}: {e}")
        return jsonify({"error": str(e)}), 500


# Settings endpoints
@api_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get all settings.

    Returns:
        Response: The settings.
    """
    try:
        settings = Settings().get_settings()
        return jsonify({
            "host": settings.host,
            "port": settings.port,
            "url_base": settings.url_base,
            "log_level": settings.log_level,
            "log_rotation": settings.log_rotation,
            "log_size": settings.log_size,
            "metadata_cache_days": settings.metadata_cache_days,
            "calendar_range_days": settings.calendar_range_days,
            "calendar_refresh_hours": settings.calendar_refresh_hours,
            "task_interval_minutes": settings.task_interval_minutes
        })
    
    except Exception as e:
        LOGGER.error(f"Error getting settings: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/settings', methods=['PUT'])
def update_settings():
    """Update settings.

    Returns:
        Response: The updated settings.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        settings = Settings()
        settings.update(data)
        
        updated_settings = settings.get_settings()
        return jsonify({
            "host": updated_settings.host,
            "port": updated_settings.port,
            "url_base": updated_settings.url_base,
            "log_level": updated_settings.log_level,
            "log_rotation": updated_settings.log_rotation,
            "log_size": updated_settings.log_size,
            "metadata_cache_days": updated_settings.metadata_cache_days,
            "calendar_range_days": updated_settings.calendar_range_days,
            "calendar_refresh_hours": updated_settings.calendar_refresh_hours,
            "task_interval_minutes": updated_settings.task_interval_minutes
        })
    
    except InvalidSettingValue as e:
        return jsonify({"error": str(e)}), 400
    
    except Exception as e:
        LOGGER.error(f"Error updating settings: {e}")
        return jsonify({"error": str(e)}), 500


# Home Assistant integration endpoint
@api_bp.route('/integrations/home-assistant', methods=['GET'])
def get_home_assistant_data():
    """Get data for Home Assistant integration.

    Returns:
        Response: The Home Assistant data.
    """
    try:
        # Get upcoming releases for the next 7 days
        today = datetime.now().strftime('%Y-%m-%d')
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        events = get_calendar_events(today, next_week)
        
        # Get series count
        series_count = execute_query("SELECT COUNT(*) as count FROM series")
        
        # Get volume count
        volume_count = execute_query("SELECT COUNT(*) as count FROM volumes")
        
        # Get chapter count
        chapter_count = execute_query("SELECT COUNT(*) as count FROM chapters")
        
        # Format data for Home Assistant
        data = {
            "upcoming_releases": events,
            "stats": {
                "series_count": series_count[0]["count"],
                "volume_count": volume_count[0]["count"],
                "chapter_count": chapter_count[0]["count"]
            }
        }
        
        return jsonify(data)
    
    except Exception as e:
        LOGGER.error(f"Error getting Home Assistant data: {e}")
        return jsonify({"error": str(e)}), 500


# Homarr integration endpoint
@api_bp.route('/integrations/homarr', methods=['GET'])
def get_homarr_data():
    """Get data for Homarr integration.

    Returns:
        Response: The Homarr data.
    """
    try:
        # Get upcoming releases for today
        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        today_events = get_calendar_events(today, today)
        
        # Get series count
        series_count = execute_query("SELECT COUNT(*) as count FROM series")
        
        # Format data for Homarr
        data = {
            "app": "MangaArr",
            "version": "1.0.0",
            "status": "ok",
            "info": {
                "series_count": series_count[0]["count"],
                "releases_today": len(today_events)
            }
        }
        
        return jsonify(data)
    
    except Exception as e:
        LOGGER.error(f"Error getting Homarr data: {e}")
        return jsonify({"error": str(e)}), 500
