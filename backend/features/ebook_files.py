#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import hashlib
import re
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path

from backend.base.helpers import (
    get_ebook_storage_dir, organize_ebook_path, 
    copy_file_to_storage, ensure_dir_exists, get_safe_folder_name
)
from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from backend.features.collection import add_to_collection, update_collection_item


def add_ebook_file(series_id: int, volume_id: int, file_path: str, file_type: Optional[str] = None, max_retries: int = 5) -> Dict:
    """Add an e-book file to the database and storage.
    
    Args:
        series_id (int): The series ID.
        volume_id (int): The volume ID.
        file_path (str): The path to the e-book file.
        file_type (Optional[str]): The file type. If None, it will be detected from the file extension.
        max_retries (int, optional): Maximum number of retries for database operations. Defaults to 5.
        
    Returns:
        Dict: The file information if successful, empty dict otherwise.
    """
    retries = 0
    retry_delay = 0.5
    
    # Check if the file exists before entering retry loop
    source_path = Path(file_path)
    if not source_path.exists() or not source_path.is_file():
        LOGGER.error(f"File does not exist: {file_path}")
        return {}
    
    # Get file info
    file_name = source_path.name
    file_size = source_path.stat().st_size
    
    # Detect file type from extension if not provided
    if file_type is None:
        ext = source_path.suffix.lower()
        if ext in ['.pdf']:
            file_type = 'PDF'
        elif ext in ['.epub']:
            file_type = 'EPUB'
        elif ext in ['.cbz']:
            file_type = 'CBZ'
        elif ext in ['.cbr']:
            file_type = 'CBR'
        elif ext in ['.mobi']:
            file_type = 'MOBI'
        elif ext in ['.azw', '.azw3']:
            file_type = 'AZW'
        else:
            file_type = ext.lstrip('.')
    
    # Check if the file is already in a managed location
    from backend.internals.settings import Settings
    from backend.base.helpers import get_safe_folder_name as safe_folder_name
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    # Get the series info for folder name comparison
    series_info = execute_query("SELECT title FROM series WHERE id = ?", (series_id,))
    if not series_info:
        LOGGER.error(f"Series with ID {series_id} not found")
        return {}
    
    series_title = series_info[0]['title']
    safe_series_title = safe_folder_name(series_title)
    
    # Check if the file is already in a managed location
    is_already_managed = False
    file_in_correct_location = False
    
    # Convert source_path to absolute path
    source_path_abs = source_path.absolute()
    LOGGER.info(f"Checking if file is already managed: {source_path_abs}")
    
    # Special case: if the source path contains the series name, consider it already managed
    if safe_series_title in str(source_path_abs):
        is_already_managed = True
        file_in_correct_location = True
        LOGGER.info(f"File is already in a folder with the series name: {source_path_abs}")
    else:
        # Check if file is in any root folder
        for root_folder in root_folders:
            root_path = Path(root_folder['path'])
            if str(source_path_abs).startswith(str(root_path)):
                # File is in a managed root folder
                is_already_managed = True
                
                # Check if it's in the correct series folder
                expected_series_path = root_path / safe_series_title
                if str(source_path_abs).startswith(str(expected_series_path)):
                    file_in_correct_location = True
                    LOGGER.info(f"File is already in the correct location: {source_path_abs}")
                    break
    
    if is_already_managed and file_in_correct_location:
        # Use the existing file path without copying
        target_path = source_path_abs
        unique_file_name = source_path.name
        LOGGER.info(f"Using existing file in managed location: {target_path}")
    else:
        # Generate a unique filename to prevent overwriting
        unique_file_name = file_name  # Use original filename without timestamp
        
        # Organize the file path
        target_path = organize_ebook_path(series_id, volume_id, unique_file_name)
        
        # Copy the file to the storage location if it's not already there
        if source_path_abs != target_path:
            LOGGER.info(f"Copying file from {source_path_abs} to {target_path}")
            if not copy_file_to_storage(source_path, target_path):
                LOGGER.error(f"Failed to copy file: {file_path}")
                return {}
        else:
            LOGGER.info(f"File is already at target path: {target_path}")

    
    # Start retry loop for database operations
    while retries <= max_retries:
        try:
            # Add file to the database
            try:
                # First try with RETURNING id
                result = execute_query("""
                INSERT INTO ebook_files (
                    series_id, volume_id, file_path, file_name, file_size,
                    file_type, original_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id
                """, (
                    series_id,
                    volume_id,
                    str(target_path),
                    unique_file_name,
                    file_size,
                    file_type,
                    file_name
                ), commit=True)
                
                # Get the inserted ID
                if result and len(result) > 0:
                    file_id = result[0]['id']
                    # Get the created file
                    file_info = get_ebook_file(file_id)
                else:
                    # If RETURNING id didn't work, get the last inserted ID
                    LOGGER.info(f"RETURNING id didn't work, trying to get last_insert_rowid() for: {target_path}")
                    last_id_result = execute_query("SELECT last_insert_rowid() as id")
                    if last_id_result and len(last_id_result) > 0:
                        file_id = last_id_result[0]['id']
                        file_info = get_ebook_file(file_id)
                    else:
                        LOGGER.error(f"Failed to get ID for inserted file: {target_path}")
                        file_info = None
            except Exception as e:
                LOGGER.error(f"Error during file insertion: {e}")
                # Try a simpler insert without RETURNING
                execute_query("""
                INSERT INTO ebook_files (
                    series_id, volume_id, file_path, file_name, file_size,
                    file_type, original_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    series_id,
                    volume_id,
                    str(target_path),
                    unique_file_name,
                    file_size,
                    file_type,
                    file_name
                ), commit=True)
                
                # Get the last inserted ID
                last_id_result = execute_query("SELECT last_insert_rowid() as id")
                if last_id_result and len(last_id_result) > 0:
                    file_id = last_id_result[0]['id']
                    file_info = get_ebook_file(file_id)
                else:
                    LOGGER.error(f"Failed to get ID for inserted file after fallback: {target_path}")
                    file_info = None
            
            if file_info:
                # Update the collection item to link to this file
                execute_query("""
                UPDATE collection_items 
                SET has_file = 1, ebook_file_id = ?,
                    digital_format = ?,
                    format = CASE
                        WHEN format = 'PHYSICAL' THEN 'BOTH'
                        ELSE 'DIGITAL'
                    END
                WHERE series_id = ? AND volume_id = ? AND item_type = 'VOLUME'
                """, (file_id, file_type, series_id, volume_id), commit=True)
            
            return file_info
        
        except Exception as e:
            if "database is locked" in str(e) and retries < max_retries:
                retries += 1
                LOGGER.warning(f"Database locked while adding e-book file, retrying ({retries}/{max_retries}) in {retry_delay}s")
                time.sleep(retry_delay)
                retry_delay *= 1.5
            else:
                LOGGER.error(f"Error adding e-book file: {e}")
                return {}
    
    LOGGER.error(f"Failed to add e-book file after {max_retries} retries")
    return {}


def get_ebook_file(file_id: int) -> Dict:
    """Get an e-book file by ID.
    
    Args:
        file_id (int): The file ID.
        
    Returns:
        Dict: The file information.
    """
    try:
        file_info = execute_query("""
        SELECT 
            id, series_id, volume_id, file_path, file_name, file_size,
            file_type, original_name, added_date, created_at, updated_at
        FROM ebook_files
        WHERE id = ?
        """, (file_id,))
        
        if file_info:
            return file_info[0]
        
        return {}
    
    except Exception as e:
        LOGGER.error(f"Error getting e-book file {file_id}: {e}")
        return {}


def get_ebook_files_for_volume(volume_id: int) -> List[Dict]:
    """Get all e-book files for a volume.
    
    Args:
        volume_id (int): The volume ID.
        
    Returns:
        List[Dict]: The file information.
    """
    try:
        files = execute_query("""
        SELECT 
            id, series_id, volume_id, file_path, file_name, file_size,
            file_type, original_name, added_date, created_at, updated_at
        FROM ebook_files
        WHERE volume_id = ?
        ORDER BY added_date DESC
        """, (volume_id,))
        
        return files
    
    except Exception as e:
        LOGGER.error(f"Error getting e-book files for volume {volume_id}: {e}")
        return []


def get_ebook_files_for_series(series_id: int) -> List[Dict]:
    """Get all e-book files for a series.
    
    Args:
        series_id (int): The series ID.
        
    Returns:
        List[Dict]: The file information.
    """
    try:
        files = execute_query("""
        SELECT 
            ef.id, ef.series_id, ef.volume_id, ef.file_path, ef.file_name, ef.file_size,
            ef.file_type, ef.original_name, ef.added_date, ef.created_at, ef.updated_at,
            v.volume_number, v.title as volume_title
        FROM ebook_files ef
        JOIN volumes v ON ef.volume_id = v.id
        WHERE ef.series_id = ?
        ORDER BY CAST(v.volume_number AS REAL), ef.added_date DESC
        """, (series_id,))
        
        return files
    
    except Exception as e:
        LOGGER.error(f"Error getting e-book files for series {series_id}: {e}")
        return []


def delete_ebook_file(file_id: int) -> bool:
    """Delete an e-book file.
    
    Args:
        file_id (int): The file ID.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Get the file info
        file_info = get_ebook_file(file_id)
        
        if not file_info:
            return False
        
        # Delete the file from storage
        file_path = file_info.get('file_path')
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                LOGGER.error(f"Error deleting file {file_path}: {e}")
        
        # Update the collection item to unlink this file
        execute_query("""
        UPDATE collection_items 
        SET has_file = 0, ebook_file_id = NULL
        WHERE ebook_file_id = ?
        """, (file_id,), commit=True)
        
        # Delete the file from the database
        execute_query("""
        DELETE FROM ebook_files
        WHERE id = ?
        """, (file_id,), commit=True)
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error deleting e-book file {file_id}: {e}")
        return False


def scan_for_ebooks(specific_series_id: Optional[int] = None, custom_path: Optional[str] = None) -> Dict:
    """Scan the data directory for e-book files and add them to the database.
    
    Args:
        specific_series_id (Optional[int]): If provided, only scan for this specific series.
        
    Returns:
        Dict: Statistics about the scan.
    """
    LOGGER.info(f"Starting e-book scan with specific_series_id={specific_series_id}, custom_path={custom_path}")
    try:
        stats = {
            'scanned': 0,
            'added': 0,
            'skipped': 0,
            'errors': 0,
            'series_processed': 0
        }
        
        # Get root folders from settings
        from backend.internals.settings import Settings
        settings = Settings().get_settings()
        root_folders = settings.root_folders
        
        # If no root folders configured, use default ebook storage
        if not root_folders:
            LOGGER.warning("No root folders configured, using default ebook storage")
            # Get the e-book storage directory
            ebook_dir = get_ebook_storage_dir()
            root_paths = [ebook_dir]
        else:
            # Use all configured root folders
            root_paths = [Path(folder['path']) for folder in root_folders]
            LOGGER.info(f"Using {len(root_paths)} root folders for scanning")
        
        # If scanning for a specific series, get its details
        if specific_series_id:
            # Get series info with all needed fields
            series_info = execute_query(
                "SELECT title, content_type, custom_path FROM series WHERE id = ?", 
                (specific_series_id,)
            )
            
            if not series_info:
                return {'error': f"Series with ID {specific_series_id} not found"}
            
            # Get series title and content type
            series_title = series_info[0]['title']
            content_type = series_info[0]['content_type']
            
            # Get custom path if it exists
            try:
                series_custom_path = series_info[0]['custom_path']
                if series_custom_path:
                    LOGGER.info(f"Found custom path for series {specific_series_id}: {series_custom_path}")
            except (KeyError, IndexError):
                LOGGER.warning(f"No custom path found for series {specific_series_id}")
                series_custom_path = None
            from backend.base.helpers import get_safe_folder_name
            safe_title = get_safe_folder_name(series_title)
            
            LOGGER.info(f"Scanning for series: {series_title} (ID: {specific_series_id})")
            LOGGER.info(f"Safe folder name: {safe_title}")
            
            # Only scan this specific series directory in all root folders
            series_dirs = []
            
            # Check if a custom path was provided in the function call
            if custom_path:
                LOGGER.info(f"Using provided custom path from function call: {custom_path}")
                custom_path_obj = Path(custom_path)
                if custom_path_obj.exists() and custom_path_obj.is_dir():
                    LOGGER.info(f"Custom path exists: {custom_path}")
                    series_dirs.append((custom_path_obj, content_type, specific_series_id))
                    # If we have a custom path, we don't need to check the standard paths
            # Check if the series has a custom path in the database
            elif series_custom_path:
                LOGGER.info(f"Using custom path from database: {series_custom_path}")
                custom_path_obj = Path(series_custom_path)
                if custom_path_obj.exists() and custom_path_obj.is_dir():
                    LOGGER.info(f"Custom path exists: {series_custom_path}")
                    series_dirs.append((custom_path_obj, content_type, specific_series_id))
                    # If we have a custom path, we don't need to check the standard paths
                else:
                    LOGGER.warning(f"Custom path does not exist or is not a directory: {custom_path}")
            
            # Also check standard root folders if no custom path was found
            if not series_dirs:
                for root_path in root_paths:
                    LOGGER.info(f"Checking root path: {root_path}")
                    series_dir = root_path / safe_title
                    LOGGER.info(f"Looking for series directory: {series_dir}")
                    
                    if series_dir.exists() and series_dir.is_dir():
                        LOGGER.info(f"Found series directory: {series_dir}")
                        series_dirs.append((series_dir, content_type, specific_series_id))
                    else:
                        LOGGER.warning(f"Series directory not found: {series_dir}")
                    
            # If no directories found, try to look for the exact path
            if not series_dirs and specific_series_id:
                # Try the exact path that might be stored in the database
                exact_path = execute_query(
                    "SELECT folder_path FROM series_folders WHERE series_id = ?",
                    (specific_series_id,)
                )
                
                if exact_path and exact_path[0]['folder_path']:
                    path_obj = Path(exact_path[0]['folder_path'])
                    LOGGER.info(f"Trying exact path from database: {path_obj}")
                    if path_obj.exists() and path_obj.is_dir():
                        LOGGER.info(f"Exact path exists: {path_obj}")
                        series_dirs.append((path_obj, content_type, specific_series_id))
                    else:
                        LOGGER.warning(f"Exact path does not exist or is not a directory: {path_obj}")
        else:
            # Initialize series directories
            series_dirs = []
            
            # Process each root folder
            for root_path in root_paths:
                if not root_path.exists() or not root_path.is_dir():
                    LOGGER.warning(f"Root folder does not exist or is not a directory: {root_path}")
                    continue
                    
                # Get all series directories directly in the root folder
                for series_dir in root_path.iterdir():
                    if not series_dir.is_dir():
                        continue
                    
                    # Try to find the series in the database to get its content type
                    # The folder name should match the series title (with invalid chars replaced)
                    series_dir_name = series_dir.name
                    LOGGER.info(f"Looking for series with folder name: {series_dir_name}")
                    
                    # First try exact match
                    series_info = execute_query(
                        "SELECT id, content_type FROM series WHERE title = ?", 
                        (series_dir_name,)
                    )
                    
                    # If not found, try case-insensitive match
                    if not series_info:
                        LOGGER.info(f"No exact match found, trying case-insensitive match")
                        series_info = execute_query(
                            "SELECT id, content_type FROM series WHERE LOWER(title) = LOWER(?)", 
                            (series_dir_name,)
                        )
                        
                    # If still not found, try with similar name (replace special chars)
                    if not series_info:
                        LOGGER.info(f"No case-insensitive match found, trying with similar name")
                        from backend.base.helpers import get_safe_folder_name
                        # Get all series
                        all_series = execute_query("SELECT id, title, content_type FROM series")
                        
                        # Find a match where the safe folder name matches
                        for series in all_series:
                            safe_title = get_safe_folder_name(series['title'])
                            LOGGER.debug(f"Comparing: '{safe_title}' with '{series_dir_name}'")
                            if safe_title == series_dir_name:
                                series_info = [series]
                                LOGGER.info(f"Found match: {series['title']} -> {safe_title}")
                                break
                    
                    if series_info:
                        series_id = series_info[0]['id']
                        content_type = series_info[0]['content_type']
                        series_dirs.append((series_dir, content_type, series_id))
                        
                        # Ensure README file exists
                        from backend.base.helpers import ensure_readme_file
                        # Get series title from database
                        series_title_info = execute_query(
                            "SELECT title FROM series WHERE id = ?", 
                            (series_id,)
                        )
                        if series_title_info:
                            series_title = series_title_info[0]['title']
                            # Ensure README file exists
                            ensure_readme_file(series_dir, series_title, series_id, content_type)
                    else:
                        # If series not found in database, skip it
                        LOGGER.warning(f"Series directory found but not in database: {series_dir}")
                        continue
        
        # Define supported file extensions
        supported_extensions = {
            '.pdf': 'PDF',
            '.epub': 'EPUB',
            '.cbz': 'CBZ',
            '.cbr': 'CBR',
            '.mobi': 'MOBI',
            '.azw': 'AZW',
            '.azw3': 'AZW'
        }
        
        # Process each series directory
        for series_dir, content_type, series_id in series_dirs:
            if not series_dir.is_dir():
                LOGGER.warning(f"Skipping {series_dir} as it's not a directory")
                continue
            
            LOGGER.info(f"Processing directory: {series_dir} for series ID: {series_id}")
            
            if not series_id:
                stats['errors'] += 1
                continue
            
            stats['series_processed'] += 1
            LOGGER.info(f"Processing series: {series_title} (ID: {series_id})")
            
            # Keep track of processed files to avoid duplicates
            processed_files = set()
            
            # Process each file in the series directory (recursive)
            LOGGER.info(f"Scanning directory {series_dir} for e-book files")
            try:
                # Check if we have permission to access the directory
                if not os.access(str(series_dir), os.R_OK):
                    LOGGER.error(f"No read permission for directory: {series_dir}")
                    stats['errors'] += 1
                    all_files = []
                else:
                    LOGGER.info(f"Have read permission for directory: {series_dir}")
                    all_files = list(series_dir.glob('**/*'))
                    LOGGER.info(f"Found {len(all_files)} total files/directories")
                    # Log the first 10 files for debugging
                    for i, f in enumerate(all_files[:10]):
                        LOGGER.debug(f"File {i}: {f} (is_file: {f.is_file()})")
            except Exception as e:
                LOGGER.error(f"Error listing files in directory {series_dir}: {e}")
                all_files = []
            
            for file_path in all_files:
                if not file_path.is_file():
                    continue
                    
                LOGGER.debug(f"Checking file: {file_path}")
                    
                # Skip if already processed (can happen with symlinks)
                file_key = str(file_path.resolve())
                if file_key in processed_files:
                    LOGGER.debug(f"Skipping already processed file: {file_path}")
                    continue
                    
                processed_files.add(file_key)
                
                # Get file extension and check if supported
                file_ext = file_path.suffix.lower()
                LOGGER.info(f"File extension: {file_ext} for file {file_path}")
                
                # Special handling for CBZ files
                if file_ext == '.cbz':
                    LOGGER.info(f"Found CBZ file: {file_path}")
                
                if file_ext not in supported_extensions:
                    LOGGER.info(f"Skipping unsupported file type: {file_path}")
                    stats['skipped'] = stats.get('skipped', 0) + 1
                    continue
                else:
                    LOGGER.info(f"Found supported file type: {file_ext} for file {file_path}")
                    # Count this file as scanned
                    stats['scanned'] = stats.get('scanned', 0) + 1
                    
                LOGGER.info(f"Found supported file: {file_path} with extension {file_ext}")
                
                # Extract volume number from filename or path
                LOGGER.info(f"Attempting to extract volume number from {file_path}")
                volume_number = extract_volume_number(file_path)
                
                if not volume_number:
                    LOGGER.warning(f"Could not extract volume number from {file_path}")
                    stats['skipped'] = stats.get('skipped', 0) + 1
                    continue
                
                LOGGER.info(f"Successfully extracted volume number: {volume_number} from {file_path}")
                
                # Get or create volume
                volume_id = get_or_create_volume(series_id, volume_number)
                
                if not volume_id:
                    LOGGER.error(f"Failed to get or create volume for series {series_id}, volume {volume_number}")
                    stats['errors'] = stats.get('errors', 0) + 1
                    continue
                    
                LOGGER.info(f"Using volume ID: {volume_id} for volume {volume_number}")
                
                # Check if file already exists in database
                existing_files = get_ebook_files_for_volume(volume_id)
                LOGGER.info(f"Found {len(existing_files)} existing files for volume {volume_id}")
                
                # Check if file path matches or if file is identical (same path after resolving symlinks)
                file_exists = False
                for ef in existing_files:
                    if not os.path.exists(ef['file_path']):
                        LOGGER.debug(f"Existing file path not found: {ef['file_path']}")
                        continue
                        
                    try:
                        if os.path.samefile(file_path, Path(ef['file_path'])):
                            LOGGER.info(f"File already exists in database: {file_path}")
                            file_exists = True
                            break
                    except OSError as e:
                        LOGGER.warning(f"Error comparing files: {e}")
                        # Handle case where files can't be compared
                        pass
                
                if file_exists:
                    LOGGER.info(f"Skipping existing file: {file_path}")
                    stats['skipped'] = stats.get('skipped', 0) + 1
                    continue
                
                # Get file type from extension
                file_type = supported_extensions[file_ext]
                LOGGER.info(f"File type: {file_type} for file: {file_path}")
                
                # Add file to database
                LOGGER.info(f"Adding file to database: {file_path}")
                file_info = add_ebook_file(series_id, volume_id, str(file_path), file_type)
                
                if file_info:
                    stats['added'] = stats.get('added', 0) + 1
                    LOGGER.info(f"Successfully added file: {file_path.name} as Volume {volume_number}")
                    
                    # Update collection item to mark it as having a file
                    update_collection_for_volume(series_id, volume_id, file_type)
                else:
                    LOGGER.error(f"Failed to add file to database: {file_path}")
                    stats['errors'] = stats.get('errors', 0) + 1
        
        # Log the final stats
        LOGGER.info(f"Scan completed with stats: {stats}")
        
        # Convert any None values to 0 to avoid 'undefined' in the UI
        for key in stats:
            if stats[key] is None:
                stats[key] = 0
                
        # Make sure all required keys exist
        required_keys = ['scanned', 'added', 'skipped', 'errors', 'series_processed']
        for key in required_keys:
            if key not in stats:
                stats[key] = 0
                
        LOGGER.info(f"Final stats after cleanup: {stats}")
        return stats
    
    except Exception as e:
        LOGGER.error(f"Error scanning for e-books: {e}")
        return {'error': str(e), 'scanned': 0, 'added': 0, 'skipped': 0, 'errors': 1, 'series_processed': 0}


def get_or_create_series(title: str, content_type: str) -> Optional[int]:
    """Get or create a series with the given title and content type.
    
    Args:
        title (str): The series title.
        content_type (str): The content type.
        
    Returns:
        Optional[int]: The series ID, or None if an error occurred.
    """
    try:
        # Check if series exists
        series = execute_query("""
        SELECT id FROM series WHERE title = ?
        """, (title,))
        
        if series:
            # Update content type if needed
            execute_query("""
            UPDATE series SET content_type = ? WHERE id = ?
            """, (content_type, series[0]['id']), commit=True)
            
            return series[0]['id']
        
        # Create new series
        series_id = execute_query("""
        INSERT INTO series (title, content_type)
        VALUES (?, ?)
        """, (title, content_type), commit=True)
        
        return series_id
    
    except Exception as e:
        LOGGER.error(f"Error getting/creating series: {e}")
        return None


def update_collection_for_volume(series_id: int, volume_id: int, file_type: str) -> bool:
    """Update the collection item for a volume when a file is found.
    
    Args:
        series_id (int): The series ID.
        volume_id (int): The volume ID.
        file_type (str): The file type (PDF, EPUB, etc.).
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Check if collection item exists
        collection_item = execute_query("""
        SELECT id, format, digital_format, has_file FROM collection_items 
        WHERE series_id = ? AND volume_id = ? AND item_type = 'VOLUME'
        """, (series_id, volume_id))
        
        if collection_item:
            # Update existing collection item
            item_id = collection_item[0]['id']
            current_format = collection_item[0]['format']
            
            # Determine the new format
            new_format = current_format
            if current_format == 'PHYSICAL':
                new_format = 'BOTH'
            elif current_format == 'NONE' or not current_format:
                new_format = 'DIGITAL'
            
            # Update the collection item
            update_collection_item(
                item_id=item_id,
                format=new_format,
                digital_format=file_type,
                has_file=1
            )
        else:
            # Create new collection item
            add_to_collection(
                series_id=series_id,
                volume_id=volume_id,
                item_type='VOLUME',
                ownership_status='OWNED',
                read_status='UNREAD',
                format='DIGITAL',
                digital_format=file_type,
                has_file=1
            )
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error updating collection for volume {volume_id}: {e}")
        return False


def get_or_create_volume(series_id: int, volume_number: str, max_retries: int = 5) -> Optional[int]:
    """Get or create a volume with the given series ID and volume number.
    
    Args:
        series_id (int): The series ID.
        volume_number (str): The volume number.
        max_retries (int, optional): Maximum number of retries. Defaults to 5.
        
    Returns:
        Optional[int]: The volume ID, or None if an error occurred.
    """
    retries = 0
    retry_delay = 0.5
    
    while retries <= max_retries:
        try:
            # Check if volume exists
            volume = execute_query("""
            SELECT id FROM volumes WHERE series_id = ? AND volume_number = ?
            """, (series_id, volume_number))
            
            if volume:
                return volume[0]['id']
            
            # Create new volume
            volume_id = execute_query("""
            INSERT INTO volumes (series_id, volume_number)
            VALUES (?, ?)
            """, (series_id, volume_number), commit=True)
            
            return volume_id
        
        except Exception as e:
            if "database is locked" in str(e) and retries < max_retries:
                retries += 1
                LOGGER.warning(f"Database locked while getting/creating volume, retrying ({retries}/{max_retries}) in {retry_delay}s")
                time.sleep(retry_delay)
                retry_delay *= 1.5
            else:
                LOGGER.error(f"Error getting/creating volume: {e}")
                return None
    
    LOGGER.error(f"Failed to get/create volume after {max_retries} retries")
    return None


def extract_volume_number(file_path: Path) -> Optional[str]:
    """Extract the volume number from a file path.
    
    Args:
        file_path (Path): The file path.
        
    Returns:
        Optional[str]: The volume number, or None if it couldn't be extracted.
    """
    # Try to extract from filename without extension
    filename = file_path.stem  # Get filename without extension
    LOGGER.debug(f"Extracting volume number from filename: {filename}")
    
    # Special case for filenames like "Vol 1.cbz", "Vol 2.cbz", etc.
    if filename.startswith("Vol ") and filename[4:].isdigit():
        vol_num = filename[4:]
        LOGGER.debug(f"Direct match for 'Vol N' pattern: {vol_num}")
        return vol_num
    
    # Common patterns for volume numbers (in order of specificity)
    patterns = [
        # Explicit volume indicators
        r'[vV]ol(?:ume)?[\s._-]*(\d+(?:\.\d+)?)',  # Vol 1, Volume 1, Vol.1, Vol 1.5, etc.
        r'[vV](\d+(?:\.\d+)?)',                     # v1, V1, v1.5, etc.
        
        # Common abbreviations
        r'\bv[\s._-]*(\d+(?:\.\d+)?)',              # v 1, v.1, v_1, v-1, v1.5, etc.
        r'\btome[\s._-]*(\d+(?:\.\d+)?)',           # tome 1, tome.1, etc.
        r'\bch(?:apter)?[\s._-]*(\d+(?:\.\d+)?)',    # ch 1, chapter 1, ch.1, etc.
        
        # Numbers with context
        r'\#(\d+(?:\.\d+)?)',                        # #1, #1.5, etc.
        r'\b(\d+(?:\.\d+)?)\s*(?:of|\/|\\)\s*\d+\b',    # 1 of 10, 1/10, etc.
        
        # Standalone numbers (last resort)
        r'^(\d+(?:\.\d+)?)$',                       # Filename is just a number like "1" or "1.5"
        r'\b(\d+(?:\.\d+)?)\b',                     # Any number in the filename
    ]
    
    # First try the filename
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            vol_num = match.group(1)
            LOGGER.debug(f"Found volume number {vol_num} using pattern {pattern} in filename")
            return vol_num
    
    # Then try the full filename with extension
    full_filename = file_path.name
    LOGGER.debug(f"Trying full filename: {full_filename}")
    for pattern in patterns:
        match = re.search(pattern, full_filename)
        if match:
            vol_num = match.group(1)
            LOGGER.debug(f"Found volume number {vol_num} using pattern {pattern} in full filename")
            return vol_num
    
    # If no match in filename, try parent directory name
    parent_dir = file_path.parent.name
    LOGGER.debug(f"Trying parent directory name: {parent_dir}")
    for pattern in patterns:
        match = re.search(pattern, parent_dir)
        if match:
            vol_num = match.group(1)
            LOGGER.debug(f"Found volume number {vol_num} using pattern {pattern} in parent directory")
            return vol_num
    
    # If still no match, check if the filename itself is a number or starts with a number
    if filename.isdigit():
        LOGGER.debug(f"Filename is a digit: {filename}")
        return filename
    
    # Extract leading digits if filename starts with numbers
    match = re.match(r'^(\d+)', filename)
    if match:
        vol_num = match.group(1)
        LOGGER.debug(f"Found volume number {vol_num} from leading digits in filename")
        return vol_num
    
    # If still no match, use a default
    LOGGER.debug(f"No volume number found, defaulting to 1")
    return '1'  # Default to volume 1