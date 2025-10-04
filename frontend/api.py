#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from pathlib import Path

from flask import Blueprint, Response, jsonify, request

from backend.base.custom_exceptions import (APIError, DatabaseError,
                                           InvalidSettingValue, MetadataError)
from backend.base.helpers import (
    create_series_folder_structure, ensure_dir_exists, get_safe_folder_name,
    get_ebook_storage_dir
)
from backend.base.logging import LOGGER
from frontend.middleware import root_folders_required
from backend.features.calendar import get_calendar_events, update_calendar
from backend.features.collection import (
    add_to_collection,
    export_collection,
    get_collection_items,
    get_collection_stats,
    import_collection,
    remove_from_collection,
    update_collection_item,
    update_collection_stats,
    add_series_to_collection,
    get_default_collection,
)
from backend.features.home_assistant import (get_home_assistant_sensor_data,
                                            get_home_assistant_setup_instructions)
from backend.features.homarr import get_homarr_data, get_homarr_setup_instructions
from backend.features.metadata_service import init_metadata_service
from backend.features.notifications import (check_upcoming_releases, create_notification,
                                           delete_all_notifications, delete_notification,
                                           get_notification_settings, get_notifications,
                                           get_subscriptions, is_subscribed, mark_all_notifications_as_read,
                                           mark_notification_as_read, send_notification,
                                           subscribe_to_series, unsubscribe_from_series,
                                           update_notification_settings)
from backend.internals.db import execute_query
from backend.internals.settings import Settings
from frontend.api_metadata_fixed import metadata_api_bp
from backend.features.move_service import move_series_db_only, plan_series_move

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize metadata service
init_metadata_service()


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


# Dashboard endpoint
@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard data.

    Returns:
        Response: The dashboard data.
    """
    try:
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get upcoming releases for today
        today_events = get_calendar_events(today, today)
        
        # Get series count
        series_count = execute_query("SELECT COUNT(*) as count FROM series")
        
        # Get volume count
        volume_count = execute_query("SELECT COUNT(*) as count FROM volumes")
        
        # Get chapter count
        chapter_count = execute_query("SELECT COUNT(*) as count FROM chapters")
        
        # Get owned volumes count
        owned_volumes = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'VOLUME' AND ownership_status = 'OWNED'
        """)
        
        # Get read volumes count
        read_volumes = execute_query("""
        SELECT COUNT(*) as count
        FROM collection_items
        WHERE item_type = 'VOLUME' AND read_status = 'READ'
        """)
        
        # Get collection value
        collection_value = execute_query("""
        SELECT SUM(purchase_price) as total
        FROM collection_items
        WHERE purchase_price IS NOT NULL
        """)
        
        # Format data for dashboard
        data = {
            "stats": {
                "series_count": series_count[0]["count"],
                "volume_count": volume_count[0]["count"],
                "chapter_count": chapter_count[0]["count"],
                "releases_today": len(today_events),
                "owned_volumes": owned_volumes[0]["count"] if owned_volumes else 0,
                "read_volumes": read_volumes[0]["count"] if read_volumes else 0,
                "collection_value": collection_value[0]["total"] if collection_value and collection_value[0]["total"] else 0
            },
            "today_events": today_events
        }
        
        return jsonify(data)
    
    except Exception as e:
        LOGGER.error(f"Error getting dashboard data: {e}")
        return jsonify({"error": str(e)}), 500


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
@api_bp.route('/series/folder-path', methods=['POST'])
def get_series_folder_path():
    """Get the folder path for a series.

    Returns:
        Response: The folder path.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Check if required fields are provided
        required_fields = ["series_id", "title", "content_type"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Get the folder path inputs
        series_id = data["series_id"]
        title = data["title"]
        content_type = (data.get("content_type") or "MANGA").upper()
        collection_id = data.get("collection_id")
        root_folder_id = data.get("root_folder_id")
        
        # Check if the series has a custom path
        custom_path = execute_query("SELECT custom_path FROM series WHERE id = ?", (series_id,))
        has_custom_path = False
        
        if custom_path:
            try:
                if custom_path[0]['custom_path']:
                    has_custom_path = True
            except (KeyError, IndexError) as e:
                LOGGER.warning(f"Error accessing custom path: {e}")
        
        if has_custom_path:
            # Use the custom path
            series_dir = Path(custom_path[0]['custom_path'])
            LOGGER.info(f"Using custom path for series {series_id}: {series_dir}")
        else:
            # Create folder name that preserves spaces but replaces invalid characters
            safe_title = get_safe_folder_name(title)
            LOGGER.info(f"Original title: '{title}', Safe title for folder: '{safe_title}'")

            # Resolve preferred root folder without creating any directories
            from backend.internals.settings import Settings
            settings = Settings().get_settings()

            chosen_root_path = None

            # 1) explicit root_folder_id
            if root_folder_id:
                try:
                    rf = execute_query("SELECT path FROM root_folders WHERE id = ?", (int(root_folder_id),))
                    if rf:
                        chosen_root_path = Path(rf[0]['path'])
                except Exception:
                    pass

            # 2) collection's root folders
            if chosen_root_path is None and collection_id:
                try:
                    rows = execute_query(
                        """
                        SELECT rf.path FROM root_folders rf
                        JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
                        WHERE crf.collection_id = ?
                        ORDER BY rf.name ASC
                        """,
                        (int(collection_id),)
                    )
                    if rows:
                        chosen_root_path = Path(rows[0]['path'])
                except Exception:
                    pass

            # 3) default collection for type
            if chosen_root_path is None:
                try:
                    rows = execute_query(
                        """
                        SELECT rf.path FROM root_folders rf
                        JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
                        JOIN collections c ON c.id = crf.collection_id
                        WHERE c.is_default = 1 AND UPPER(c.content_type) = ?
                        ORDER BY rf.name ASC
                        """,
                        (content_type.upper(),)
                    )
                    if rows:
                        chosen_root_path = Path(rows[0]['path'])
                except Exception:
                    pass

            # 4) any settings root folder matching type
            if chosen_root_path is None and settings.root_folders:
                try:
                    rf = next((rf for rf in settings.root_folders if (rf.get('content_type') or 'MANGA').upper() == content_type), None)
                    if rf:
                        chosen_root_path = Path(rf['path'])
                except Exception:
                    pass

            # 5) fallback: first configured root folder or default ebooks dir
            if chosen_root_path is None:
                if settings.root_folders:
                    chosen_root_path = Path(settings.root_folders[0]['path'])
                else:
                    chosen_root_path = get_ebook_storage_dir()

            series_dir = chosen_root_path / safe_title
        
        # Return the folder path
        return jsonify({"folder_path": str(series_dir)})
    
    except Exception as e:
        LOGGER.error(f"Error getting folder path: {e}")
        return jsonify({"error": str(e)}), 500


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
            content_type, metadata_source, metadata_id, created_at, updated_at
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
            content_type, metadata_source, metadata_id, created_at, updated_at
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
@root_folders_required
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
        
        # Set default content type if not provided
        content_type = data.get("content_type", "MANGA")
        
        # Ensure content_type is uppercase
        if content_type:
            content_type = content_type.upper()
        else:
            content_type = "MANGA"
            
        LOGGER.info(f"Adding series with content type: {content_type}")
        
        # Insert the series
        series_id = execute_query("""
        INSERT INTO series (
            title, description, author, publisher, cover_url, status, 
            content_type, metadata_source, metadata_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("title"),
            data.get("description"),
            data.get("author"),
            data.get("publisher"),
            data.get("cover_url"),
            data.get("status"),
            content_type,
            data.get("metadata_source"),
            data.get("metadata_id")
        ), commit=True)
        
        # Get the created series
        series = execute_query("""
        SELECT 
            id, title, description, author, publisher, cover_url, status, 
            content_type, metadata_source, metadata_id, created_at, updated_at
        FROM series
        WHERE id = last_insert_rowid()
        """)
        
        # Optionally link the series to a collection
        try:
            collection_id = data.get("collection_id")
            if collection_id:
                try:
                    collection_id = int(collection_id)
                except Exception:
                    collection_id = None
            if collection_id:
                add_series_to_collection(collection_id, series_id)
            else:
                # Auto-link to default collection for the selected content_type if available
                try:
                    default_coll = get_default_collection(content_type)
                    if default_coll and default_coll.get('id'):
                        add_series_to_collection(default_coll['id'], series_id)
                except Exception as _e:
                    LOGGER.warning(f"Could not auto-link series to default collection: {_e}")
        except Exception as link_err:
            LOGGER.warning(f"Link to collection failed: {link_err}")

        # Create folder structure
        try:
            series_data = series[0]
            LOGGER.info(f"Creating folder structure for series: {series_data['title']} (ID: {series_data['id']})")
            LOGGER.info(f"Series content type: {series_data['content_type']}")
            
            # Get root folders from settings
            from backend.internals.settings import Settings
            from pathlib import Path
            import os
            settings = Settings().get_settings()
            LOGGER.info(f"Root folders: {settings.root_folders}")
            
            # Check if root folders are configured
            if not settings.root_folders:
                LOGGER.warning("No root folders configured, using default ebook storage")
            else:
                # Prefer a root folder that matches the collection type if possible (simple heuristic)
                preferred_root = None
                try:
                    # find any root folder whose content_type matches selected content_type
                    preferred_root = next((rf for rf in settings.root_folders if (rf.get('content_type') or 'MANGA').upper() == content_type), None)
                except Exception:
                    preferred_root = None
                root_folder = preferred_root or settings.root_folders[0]
                root_path = Path(root_folder['path'])
                LOGGER.info(f"Root folder path: {root_path}, exists: {root_path.exists()}, is directory: {root_path.is_dir() if root_path.exists() else False}")
                
                # Try to create the root folder if it doesn't exist
                if not root_path.exists():
                    try:
                        LOGGER.info(f"Creating root folder: {root_path}")
                        os.makedirs(str(root_path), exist_ok=True)
                        LOGGER.info(f"Root folder created: {root_path}")
                    except Exception as e:
                        LOGGER.error(f"Error creating root folder: {e}")
                        import traceback
                        LOGGER.error(traceback.format_exc())
            
            series_path = create_series_folder_structure(
                series_data['id'],
                series_data['title'],
                series_data['content_type'],
                collection_id=data.get('collection_id'),
                root_folder_id=data.get('root_folder_id')
            )
            
            LOGGER.info(f"Folder structure created at: {series_path}")
            LOGGER.info(f"Folder exists: {os.path.exists(str(series_path))}, is directory: {os.path.isdir(str(series_path)) if os.path.exists(str(series_path)) else False}")
            
            # Add folder path to response
            series_data['folder_path'] = str(series_path)
        except Exception as e:
            LOGGER.error(f"Error creating folder structure: {e}")
            import traceback
            LOGGER.error(traceback.format_exc())
            # Continue even if folder creation fails
        
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
        
        for field in ["title", "description", "author", "publisher", "cover_url", "status", "content_type", "metadata_source", "metadata_id", "custom_path"]:
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
            content_type, metadata_source, metadata_id, created_at, updated_at
        FROM series
        WHERE id = ?
        """, (series_id,))
        
        # Check if title or content_type was updated
        if 'title' in data or 'content_type' in data:
            try:
                series_data = updated_series[0]
                series_path = create_series_folder_structure(
                    series_data['id'],
                    series_data['title'],
                    series_data['content_type']
                )
                
                # Add folder path to response
                series_data['folder_path'] = str(series_path)
            except Exception as e:
                LOGGER.error(f"Error updating folder structure: {e}")
                # Continue even if folder update fails
        
        return jsonify({"series": updated_series[0]})
    
    except Exception as e:
        LOGGER.error(f"Error updating series {series_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/series/<int:series_id>/move', methods=['POST'])
def move_series(series_id: int):
    """Move a series between collections and/or root folders.

    Body JSON fields:
    - target_collection_id: int (optional)
    - target_root_folder_id: int (optional)
    - move_files: bool (optional, default false)
    - clear_custom_path: bool (optional, default false)
    - dry_run: bool (optional, default false)

    Returns:
        Response: Plan and/or result summary including before/after memberships, paths, and flags.
    """
    try:
        data = request.json or {}
        target_collection_id = data.get('target_collection_id')
        target_root_folder_id = data.get('target_root_folder_id')
        move_files = bool(data.get('move_files', False))
        clear_custom_path = bool(data.get('clear_custom_path', False))
        dry_run = bool(data.get('dry_run', False))

        # Normalize numeric inputs
        if isinstance(target_collection_id, str) and target_collection_id.isdigit():
            target_collection_id = int(target_collection_id)
        if isinstance(target_root_folder_id, str) and target_root_folder_id.isdigit():
            target_root_folder_id = int(target_root_folder_id)

        result = plan_series_move(
            series_id=series_id,
            target_collection_id=target_collection_id,
            target_root_folder_id=target_root_folder_id,
            move_files=move_files,
            clear_custom_path=clear_custom_path,
            dry_run=dry_run,
        )
        return jsonify({"result": result})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        LOGGER.error(f"Error moving series {series_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/series/<int:series_id>/custom-path', methods=['PUT'])
def set_series_custom_path(series_id: int):
    """Set a custom path for a series.
    
    Args:
        series_id (int): The series ID.
        
    Returns:
        Response: Success message or error.
    """
    try:
        data = request.json or {}
        custom_path = data.get('custom_path')
        
        if not custom_path:
            return jsonify({"error": "Custom path is required"}), 400
        
        # Check if series exists
        series = execute_query("SELECT * FROM series WHERE id = ?", (series_id,))
        if not series:
            return jsonify({"error": f"Series with ID {series_id} not found"}), 404
        
        # Validate the custom path
        import os
        from pathlib import Path
        
        path_obj = Path(custom_path)
        if not path_obj.exists():
            return jsonify({"error": f"Path does not exist: {custom_path}"}), 400
        
        if not path_obj.is_dir():
            return jsonify({"error": f"Path is not a directory: {custom_path}"}), 400
        
        if not os.access(custom_path, os.R_OK):
            return jsonify({"error": f"No read permission for path: {custom_path}"}), 400
        
        # Update the series with the custom path
        execute_query("""
        UPDATE series 
        SET custom_path = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """, (custom_path, series_id), commit=True)
        
        # Check if the default folder is empty and remove it if needed
        series_title = series[0]['title']
        safe_title = get_safe_folder_name(series_title)
        
        # Get root folders from settings
        from backend.internals.settings import Settings
        settings = Settings().get_settings()
        root_folders = settings.root_folders
        
        for root_folder in root_folders:
            default_path = Path(root_folder['path']) / safe_title
            if default_path.exists() and default_path.is_dir():
                # Check if the folder is empty (except for README.txt)
                files = list(default_path.glob('*'))
                if not files or (len(files) == 1 and files[0].name == 'README.txt'):
                    # Folder is empty or only contains README.txt, remove it
                    import shutil
                    LOGGER.info(f"Removing empty default folder: {default_path}")
                    shutil.rmtree(default_path)
        
        return jsonify({"message": f"Custom path set successfully: {custom_path}"})
    
    except Exception as e:
        LOGGER.error(f"Error setting custom path: {e}")
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
            "task_interval_minutes": settings.task_interval_minutes,
            "ebook_storage": settings.ebook_storage,
            "root_folders": settings.root_folders
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
            "task_interval_minutes": updated_settings.task_interval_minutes,
            "ebook_storage": updated_settings.ebook_storage,
            "root_folders": updated_settings.root_folders
        })
    
    except InvalidSettingValue as e:
        return jsonify({"error": str(e)}), 400
    
    except Exception as e:
        LOGGER.error(f"Error updating settings: {e}")
        return jsonify({"error": str(e)}), 500


# Home Assistant integration endpoints
@api_bp.route('/integrations/home-assistant', methods=['GET'])
def get_home_assistant_data():
    """Get data for Home Assistant integration.
    
    Returns:
        Response: The Home Assistant data.
    """
    try:
        data = get_home_assistant_sensor_data()
        return jsonify(data)
    
    except Exception as e:
        LOGGER.error(f"Error getting Home Assistant data: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/integrations/home-assistant/setup', methods=['GET'])
def get_home_assistant_setup():
    """Get Home Assistant setup instructions.
    
    Returns:
        Response: The Home Assistant setup instructions.
    """
    try:
        instructions = get_home_assistant_setup_instructions()
        return jsonify(instructions)
    
    except Exception as e:
        LOGGER.error(f"Error getting Home Assistant setup instructions: {e}")
        return jsonify({"error": str(e)}), 500


# Homarr integration endpoints
@api_bp.route('/integrations/homarr', methods=['GET'])
def get_homarr_data_api():
    """Get data for Homarr integration.

    Returns:
        Response: The Homarr data.
    """
    try:
        data = get_homarr_data()
        return jsonify(data)
    
    except Exception as e:
        LOGGER.error(f"Error getting Homarr data: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/integrations/homarr/setup', methods=['GET'])
def get_homarr_setup():
    """Get Homarr setup instructions.
    
    Returns:
        Response: The Homarr setup instructions.
    """
    try:
        instructions = get_homarr_setup_instructions()
        return jsonify(instructions)
    
    except Exception as e:
        LOGGER.error(f"Error getting Homarr setup instructions: {e}")
        return jsonify({"error": str(e)}), 500


# Collection tracking endpoints
@api_bp.route('/collection', methods=['GET'])
def get_collection():
    """Get collection items with optional filters.
    
    Returns:
        Response: The collection items.
    """
    try:
        series_id = request.args.get('series_id')
        item_type = request.args.get('item_type')
        ownership_status = request.args.get('ownership_status')
        read_status = request.args.get('read_status')
        format = request.args.get('format')
        
        # Convert series_id to int if provided
        if series_id:
            try:
                series_id = int(series_id)
            except ValueError:
                return jsonify({"error": "Invalid series ID"}), 400
        
        items = get_collection_items(
            series_id=series_id,
            item_type=item_type,
            ownership_status=ownership_status,
            read_status=read_status,
            format=format
        )
        
        return jsonify({"items": items})
    
    except Exception as e:
        LOGGER.error(f"Error getting collection: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/collection/stats', methods=['GET'])
def get_collection_statistics():
    """Get collection statistics.
    
    Returns:
        Response: The collection statistics.
    """
    try:
        stats = get_collection_stats()
        return jsonify(stats)
    
    except Exception as e:
        LOGGER.error(f"Error getting collection stats: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/collection/volume/<int:volume_id>/format', methods=['PUT'])
def update_volume_format(volume_id: int):
    """Update the format of a volume in the collection.
    
    Args:
        volume_id (int): The volume ID.
        
    Returns:
        Response: Success message.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Check if volume exists
        volume = execute_query("SELECT id FROM volumes WHERE id = ?", (volume_id,))
        if not volume:
            return jsonify({"error": "Volume not found"}), 404
        
        # Get series_id for this volume
        volume_info = execute_query("SELECT series_id FROM volumes WHERE id = ?", (volume_id,))
        series_id = volume_info[0]['series_id'] if volume_info else None
        
        if not series_id:
            return jsonify({"error": "Volume has no associated series"}), 400
            
        # Check if this volume is in the collection
        collection_item = execute_query("""
        SELECT id FROM collection_items 
        WHERE volume_id = ? AND item_type = 'VOLUME'
        """, (volume_id,))
        
        format_value = data.get('format')
        digital_format_value = data.get('digital_format')
        
        if collection_item:
            # Update existing collection item
            update_result = update_collection_item(
                item_id=collection_item[0]['id'],
                format=format_value
            )
            
            if update_result:
                return jsonify({"message": "Format updated successfully"})
            else:
                return jsonify({"error": "Failed to update format"}), 500
        else:
            # Add new collection item
            add_to_collection(
                series_id=series_id,
                item_type="VOLUME",
                volume_id=volume_id,
                format=format_value
            )
            
            return jsonify({"message": "Format set successfully"})
    
    except Exception as e:
        LOGGER.error(f"Error updating volume format: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/collection/volume/<int:volume_id>/digital-format', methods=['PUT'])
def update_volume_digital_format(volume_id: int):
    """Update the digital format of a volume in the collection.
    
    Args:
        volume_id (int): The volume ID.
        
    Returns:
        Response: Success message.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Check if volume exists
        volume = execute_query("SELECT id FROM volumes WHERE id = ?", (volume_id,))
        if not volume:
            return jsonify({"error": "Volume not found"}), 404
        
        # Get series_id for this volume
        volume_info = execute_query("SELECT series_id FROM volumes WHERE id = ?", (volume_id,))
        series_id = volume_info[0]['series_id'] if volume_info else None
        
        if not series_id:
            return jsonify({"error": "Volume has no associated series"}), 400
            
        # Check if this volume is in the collection
        collection_item = execute_query("""
        SELECT id FROM collection_items 
        WHERE volume_id = ? AND item_type = 'VOLUME'
        """, (volume_id,))
        
        digital_format_value = data.get('digital_format')
        
        if collection_item:
            # Update existing collection item
            update_result = update_collection_item(
                item_id=collection_item[0]['id'],
                digital_format=digital_format_value
            )
            
            if update_result:
                return jsonify({"message": "Digital format updated successfully"})
            else:
                return jsonify({"error": "Failed to update digital format"}), 500
        else:
            # Add new collection item
            add_to_collection(
                series_id=series_id,
                item_type="VOLUME",
                volume_id=volume_id,
                format="DIGITAL",
                digital_format=digital_format_value
            )
            
            return jsonify({"message": "Digital format set successfully"})
    
    except Exception as e:
        LOGGER.error(f"Error updating volume digital format: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/collection', methods=['POST'])
@root_folders_required
def add_to_collection_api():
    """Add an item to the collection.
    
    Returns:
        Response: The created collection item ID.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ["series_id", "item_type"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate series_id
        series_id = data.get("series_id")
        series = execute_query("SELECT id FROM series WHERE id = ?", (series_id,))
        if not series:
            return jsonify({"error": "Series not found"}), 404
        
        # Validate item_type
        item_type = data.get("item_type")
        if item_type not in ["SERIES", "VOLUME", "CHAPTER"]:
            return jsonify({"error": "Invalid item type"}), 400
        
        # Validate volume_id if provided for VOLUME type
        volume_id = data.get("volume_id")
        if item_type == "VOLUME" and volume_id:
            volume = execute_query("SELECT id FROM volumes WHERE id = ?", (volume_id,))
            if not volume:
                return jsonify({"error": "Volume not found"}), 404
        
        # Validate chapter_id if provided for CHAPTER type
        chapter_id = data.get("chapter_id")
        if item_type == "CHAPTER" and chapter_id:
            chapter = execute_query("SELECT id FROM chapters WHERE id = ?", (chapter_id,))
            if not chapter:
                return jsonify({"error": "Chapter not found"}), 404
        
        # Add to collection
        item_id = add_to_collection(
            series_id=series_id,
            item_type=item_type,
            volume_id=volume_id,
            chapter_id=chapter_id,
            ownership_status=data.get("ownership_status", "OWNED"),
            read_status=data.get("read_status", "UNREAD"),
            format=data.get("format", "PHYSICAL"),
            condition=data.get("condition", "NONE"),
            purchase_date=data.get("purchase_date"),
            purchase_price=data.get("purchase_price"),
            purchase_location=data.get("purchase_location"),
            notes=data.get("notes"),
            custom_tags=data.get("custom_tags")
        )
        
        # Ensure folder structure is created for the series
        if item_type == "SERIES":
            try:
                # Get series details
                series_details = execute_query(
                    "SELECT title, content_type FROM series WHERE id = ?", 
                    (series_id,)
                )
                
                if series_details:
                    LOGGER.info(f"Creating folder structure for series added to collection: {series_details[0]['title']} (ID: {series_id})")
                    
                    # Import necessary modules
                    from backend.base.helpers import create_series_folder_structure
                    from pathlib import Path
                    import os
                    
                    # Create folder structure
                    series_path = create_series_folder_structure(
                        series_id,
                        series_details[0]['title'],
                        series_details[0]['content_type']
                    )
                    
                    LOGGER.info(f"Folder structure created at: {series_path}")
                    LOGGER.info(f"Folder exists: {os.path.exists(str(series_path))}, is directory: {os.path.isdir(str(series_path)) if os.path.exists(str(series_path)) else False}")
            except Exception as e:
                LOGGER.error(f"Error creating folder structure for series added to collection: {e}")
                import traceback
                LOGGER.error(traceback.format_exc())
                # Continue even if folder creation fails
        
        return jsonify({"id": item_id}), 201
    
    except Exception as e:
        LOGGER.error(f"Error adding to collection: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/collection/<int:item_id>', methods=['PUT'])
def update_collection_item_api(item_id: int):
    """Update a collection item.
    
    Args:
        item_id (int): The collection item ID.
        
    Returns:
        Response: Success message.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update collection item
        success = update_collection_item(
            item_id=item_id,
            ownership_status=data.get("ownership_status"),
            read_status=data.get("read_status"),
            format=data.get("format"),
            condition=data.get("condition"),
            purchase_date=data.get("purchase_date"),
            purchase_price=data.get("purchase_price"),
            purchase_location=data.get("purchase_location"),
            notes=data.get("notes"),
            custom_tags=data.get("custom_tags")
        )
        
        if not success:
            return jsonify({"error": "Collection item not found"}), 404
        
        return jsonify({"message": "Collection item updated successfully"})
    
    except Exception as e:
        LOGGER.error(f"Error updating collection item: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/collection/<int:item_id>', methods=['DELETE'])
def remove_from_collection_api(item_id: int):
    """Remove an item from the collection.
    
    Args:
        item_id (int): The collection item ID.
        
    Returns:
        Response: Success message.
    """
    try:
        success = remove_from_collection(item_id)
        
        if not success:
            return jsonify({"error": "Collection item not found"}), 404
        
        return jsonify({"message": "Collection item removed successfully"})
    
    except Exception as e:
        LOGGER.error(f"Error removing from collection: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/collection/import', methods=['POST'])
def import_collection_api():
    """Import collection data.
    
    Returns:
        Response: Import statistics.
    """
    try:
        data = request.json
        if not data or not isinstance(data, list):
            return jsonify({"error": "Invalid data format. Expected a list of collection items"}), 400
        
        stats = import_collection(data)
        return jsonify(stats)
    
    except Exception as e:
        LOGGER.error(f"Error importing collection: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/collection/export', methods=['GET'])
def export_collection_api():
    """Export collection data.
    
    Returns:
        Response: The collection data.
    """
    try:
        data = export_collection()
        return jsonify({"items": data})
    
    except Exception as e:
        LOGGER.error(f"Error exporting collection: {e}")
        return jsonify({"error": str(e)}), 500


# Notifications endpoints
@api_bp.route('/notifications', methods=['GET'])
def get_notifications_api():
    """Get notifications.
    
    Returns:
        Response: The notifications.
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        unread_only = request.args.get('unread_only', False, type=bool)
        
        notifications = get_notifications(limit, unread_only)
        return jsonify({"notifications": notifications})
    
    except Exception as e:
        LOGGER.error(f"Error getting notifications: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_as_read_api(notification_id: int):
    """Mark a notification as read.
    
    Args:
        notification_id (int): The notification ID.
        
    Returns:
        Response: Success message.
    """
    try:
        success = mark_notification_as_read(notification_id)
        
        if not success:
            return jsonify({"error": "Failed to mark notification as read"}), 500
        
        return jsonify({"message": "Notification marked as read"})
    
    except Exception as e:
        LOGGER.error(f"Error marking notification as read: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notifications/read', methods=['PUT'])
def mark_all_notifications_as_read_api():
    """Mark all notifications as read.
    
    Returns:
        Response: Success message.
    """
    try:
        success = mark_all_notifications_as_read()
        
        if not success:
            return jsonify({"error": "Failed to mark all notifications as read"}), 500
        
        return jsonify({"message": "All notifications marked as read"})
    
    except Exception as e:
        LOGGER.error(f"Error marking all notifications as read: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification_api(notification_id: int):
    """Delete a notification.
    
    Args:
        notification_id (int): The notification ID.
        
    Returns:
        Response: Success message.
    """
    try:
        success = delete_notification(notification_id)
        
        if not success:
            return jsonify({"error": "Failed to delete notification"}), 500
        
        return jsonify({"message": "Notification deleted"})
    
    except Exception as e:
        LOGGER.error(f"Error deleting notification: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notifications', methods=['DELETE'])
def delete_all_notifications_api():
    """Delete all notifications.
    
    Returns:
        Response: Success message.
    """
    try:
        success = delete_all_notifications()
        
        if not success:
            return jsonify({"error": "Failed to delete all notifications"}), 500
        
        return jsonify({"message": "All notifications deleted"})
    
    except Exception as e:
        LOGGER.error(f"Error deleting all notifications: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notifications/settings', methods=['GET'])
def get_notification_settings_api():
    """Get notification settings.
    
    Returns:
        Response: The notification settings.
    """
    try:
        settings = get_notification_settings()
        return jsonify(settings)
    
    except Exception as e:
        LOGGER.error(f"Error getting notification settings: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notifications/settings', methods=['PUT'])
def update_notification_settings_api():
    """Update notification settings.
    
    Returns:
        Response: Success message.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        success = update_notification_settings(
            email_enabled=data.get('email_enabled'),
            email_address=data.get('email_address'),
            browser_enabled=data.get('browser_enabled'),
            discord_enabled=data.get('discord_enabled'),
            discord_webhook=data.get('discord_webhook'),
            telegram_enabled=data.get('telegram_enabled'),
            telegram_bot_token=data.get('telegram_bot_token'),
            telegram_chat_id=data.get('telegram_chat_id'),
            notify_new_volumes=data.get('notify_new_volumes'),
            notify_new_chapters=data.get('notify_new_chapters'),
            notify_releases_days_before=data.get('notify_releases_days_before')
        )
        
        if not success:
            return jsonify({"error": "Failed to update notification settings"}), 500
        
        return jsonify({"message": "Notification settings updated"})
    
    except Exception as e:
        LOGGER.error(f"Error updating notification settings: {e}")
        return jsonify({"error": str(e)}), 500


# Subscriptions endpoints
@api_bp.route('/subscriptions', methods=['GET'])
def get_subscriptions_api():
    """Get subscriptions.
    
    Returns:
        Response: The subscriptions.
    """
    try:
        subscriptions = get_subscriptions()
        return jsonify({"subscriptions": subscriptions})
    
    except Exception as e:
        LOGGER.error(f"Error getting subscriptions: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/subscriptions/<int:series_id>', methods=['GET'])
def is_subscribed_api(series_id: int):
    """Check if a series is subscribed to.
    
    Args:
        series_id (int): The series ID.
        
    Returns:
        Response: Whether the series is subscribed to.
    """
    try:
        subscribed = is_subscribed(series_id)
        return jsonify({"subscribed": subscribed})
    
    except Exception as e:
        LOGGER.error(f"Error checking subscription: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/subscriptions', methods=['POST'])
def subscribe_to_series_api():
    """Subscribe to a series.
    
    Returns:
        Response: The created subscription ID.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if 'series_id' not in data:
            return jsonify({"error": "Missing required field: series_id"}), 400
        
        series_id = data.get('series_id')
        notify_new_volumes = data.get('notify_new_volumes', True)
        notify_new_chapters = data.get('notify_new_chapters', True)
        
        subscription_id = subscribe_to_series(
            series_id=series_id,
            notify_new_volumes=notify_new_volumes,
            notify_new_chapters=notify_new_chapters
        )
        
        return jsonify({"id": subscription_id}), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    
    except Exception as e:
        LOGGER.error(f"Error subscribing to series: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/subscriptions/<int:series_id>', methods=['DELETE'])
def unsubscribe_from_series_api(series_id: int):
    """Unsubscribe from a series.
    
    Args:
        series_id (int): The series ID.
        
    Returns:
        Response: Success message.
    """
    try:
        success = unsubscribe_from_series(series_id)
        
        if not success:
            return jsonify({"error": "Failed to unsubscribe from series"}), 500
        
        return jsonify({"message": "Unsubscribed from series"})
    
    except Exception as e:
        LOGGER.error(f"Error unsubscribing from series: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/monitor/check-releases', methods=['POST'])
def check_releases_api():
    """Check for upcoming releases and send notifications.
    
    Returns:
        Response: The upcoming releases that were notified about.
    """
    try:
        releases = check_upcoming_releases()
        return jsonify({"releases": releases})
    
    except Exception as e:
        LOGGER.error(f"Error checking releases: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notifications/test', methods=['POST'])
def send_test_notification_api():
    """Send a test notification.
    
    Returns:
        Response: Success message.
    """
    try:
        data = request.json or {}
        title = data.get('title', 'Test Notification')
        message = data.get('message', 'This is a test notification from Readloom.')
        type = data.get('type', 'INFO')
        
        success = send_notification(title, message, type)
        
        if not success:
            return jsonify({"error": "Failed to send test notification"}), 500
        
        return jsonify({"message": "Test notification sent"})
    
    except Exception as e:
        LOGGER.error(f"Error sending test notification: {e}")
        return jsonify({"error": str(e)}), 500
