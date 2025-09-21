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


def add_ebook_file(series_id: int, volume_id: int, file_path: str, file_type: Optional[str] = None) -> Dict:
    """Add an e-book file to the database and storage.
    
    Args:
        series_id (int): The series ID.
        volume_id (int): The volume ID.
        file_path (str): The path to the e-book file.
        file_type (Optional[str]): The file type. If None, it will be detected from the file extension.
        
    Returns:
        Dict: The file information if successful, empty dict otherwise.
    """
    try:
        # Check if the file exists
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
        
        # Generate a unique filename to prevent overwriting
        timestamp = int(time.time())
        unique_file_name = f"{timestamp}_{file_name}"
        
        # Organize the file path
        target_path = organize_ebook_path(series_id, volume_id, unique_file_name)
        
        # Copy the file to the storage location
        if not copy_file_to_storage(source_path, target_path):
            LOGGER.error(f"Failed to copy file: {file_path}")
            return {}
        
        # Add file to the database
        file_id = execute_query("""
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
        
        # Get the created file
        file_info = get_ebook_file(file_id)
        
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
        LOGGER.error(f"Error adding e-book file: {e}")
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


def scan_for_ebooks(specific_series_id: Optional[int] = None) -> Dict:
    """Scan the data directory for e-book files and add them to the database.
    
    Args:
        specific_series_id (Optional[int]): If provided, only scan for this specific series.
        
    Returns:
        Dict: Statistics about the scan.
    """
    try:
        stats = {
            'scanned': 0,
            'added': 0,
            'skipped': 0,
            'errors': 0,
            'series_processed': 0
        }
        
        # Get the e-book storage directory
        ebook_dir = get_ebook_storage_dir()
        
        # If scanning for a specific series, get its details
        if specific_series_id:
            series_info = execute_query(
                "SELECT title, content_type FROM series WHERE id = ?", 
                (specific_series_id,)
            )
            
            if not series_info:
                return {'error': f"Series with ID {specific_series_id} not found"}
                
            series_title = series_info[0]['title']
            content_type = series_info[0]['content_type']
            safe_title = get_safe_folder_name(series_title)
            
            # Only scan this specific series directory
            content_types = [content_type]
            series_dirs = {content_type: [ebook_dir / content_type / safe_title]}
        else:
            # Get all content types
            content_types = [d.name for d in ebook_dir.iterdir() if d.is_dir()]
            
            # Get all series directories for each content type
            series_dirs = {}
            for content_type in content_types:
                content_type_dir = ebook_dir / content_type
                if content_type_dir.is_dir():
                    series_dirs[content_type] = [d for d in content_type_dir.iterdir() if d.is_dir()]
        
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
        
        # Process each content type directory
        for content_type in content_types:
            if content_type not in series_dirs:
                continue
                
            # Process each series directory
            for series_dir in series_dirs[content_type]:
                if not series_dir.is_dir():
                    continue
                
                # Get or create series
                series_title = series_dir.name.replace('_', ' ')
                
                # If scanning all series, get or create the series
                if not specific_series_id:
                    series_id = get_or_create_series(series_title, content_type)
                else:
                    series_id = specific_series_id
                
                if not series_id:
                    stats['errors'] += 1
                    continue
                
                stats['series_processed'] += 1
                LOGGER.info(f"Processing series: {series_title} (ID: {series_id})")
                
                # Keep track of processed files to avoid duplicates
                processed_files = set()
                
                # Process each file in the series directory (recursive)
                for file_path in series_dir.glob('**/*'):
                    if not file_path.is_file():
                        continue
                        
                    # Skip if already processed (can happen with symlinks)
                    file_key = str(file_path.resolve())
                    if file_key in processed_files:
                        continue
                        
                    processed_files.add(file_key)
                    
                    stats['scanned'] += 1
                    
                    # Get file extension and check if supported
                    file_ext = file_path.suffix.lower()
                    if file_ext not in supported_extensions:
                        stats['skipped'] += 1
                        continue
                    
                    # Extract volume number from filename or path
                    volume_number = extract_volume_number(file_path)
                    
                    if not volume_number:
                        LOGGER.warning(f"Could not extract volume number from {file_path}")
                        stats['skipped'] += 1
                        continue
                    
                    # Get or create volume
                    volume_id = get_or_create_volume(series_id, volume_number)
                    
                    if not volume_id:
                        stats['errors'] += 1
                        continue
                    
                    # Check if file already exists in database
                    existing_files = get_ebook_files_for_volume(volume_id)
                    
                    # Check if file path matches or if file is identical (same path after resolving symlinks)
                    file_exists = False
                    for ef in existing_files:
                        if not os.path.exists(ef['file_path']):
                            continue
                            
                        try:
                            if os.path.samefile(file_path, Path(ef['file_path'])):
                                file_exists = True
                                break
                        except OSError:
                            # Handle case where files can't be compared
                            pass
                    
                    if file_exists:
                        stats['skipped'] += 1
                        continue
                    
                    # Get file type from extension
                    file_type = supported_extensions[file_ext]
                    
                    # Add file to database
                    file_info = add_ebook_file(series_id, volume_id, str(file_path), file_type)
                    
                    if file_info:
                        stats['added'] += 1
                        LOGGER.info(f"Added file: {file_path.name} as Volume {volume_number}")
                        
                        # Update collection item to mark it as having a file
                        update_collection_for_volume(series_id, volume_id, file_type)
                    else:
                        stats['errors'] += 1
        
        return stats
    
    except Exception as e:
        LOGGER.error(f"Error scanning for e-books: {e}")
        return {'error': str(e)}


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


def get_or_create_volume(series_id: int, volume_number: str) -> Optional[int]:
    """Get or create a volume with the given series ID and volume number.
    
    Args:
        series_id (int): The series ID.
        volume_number (str): The volume number.
        
    Returns:
        Optional[int]: The volume ID, or None if an error occurred.
    """
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
        LOGGER.error(f"Error getting/creating volume: {e}")
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
        r'\b(\d+(?:\.\d+)?)\s*(?:of|\/)\s*\d+\b',    # 1 of 10, 1/10, etc.
        
        # Standalone numbers (last resort)
        r'^(\d+(?:\.\d+)?)$',                       # Filename is just a number like "1" or "1.5"
        r'\b(\d+(?:\.\d+)?)\b',                     # Any number in the filename
    ]
    
    # First try the filename
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            return match.group(1)
    
    # Then try the full filename with extension
    full_filename = file_path.name
    for pattern in patterns:
        match = re.search(pattern, full_filename)
        if match:
            return match.group(1)
    
    # If no match in filename, try parent directory name
    parent_dir = file_path.parent.name
    for pattern in patterns:
        match = re.search(pattern, parent_dir)
        if match:
            return match.group(1)
    
    # If still no match, check if the filename itself is a number or starts with a number
    if filename.isdigit():
        return filename
    
    # Extract leading digits if filename starts with numbers
    match = re.match(r'^(\d+)', filename)
    if match:
        return match.group(1)
    
    # If still no match, use a default
    return '1'  # Default to volume 1