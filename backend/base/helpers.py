#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Union


def check_min_python_version(major: int, minor: int) -> bool:
    """Check if the current Python version is at least the given version.

    Args:
        major (int): The major version to check.
        minor (int): The minor version to check.

    Returns:
        bool: True if the current Python version is at least the given version.
    """
    current_major, current_minor = sys.version_info[:2]
    if current_major > major:
        return True
    if current_major == major and current_minor >= minor:
        return True
    
    print(f"ERROR: Python {major}.{minor} or higher is required. "
          f"You are using Python {current_major}.{current_minor}.")
    return False


def get_python_exe() -> Optional[str]:
    """Get the path to the Python executable.

    Returns:
        Optional[str]: The path to the Python executable, or None if not found.
    """
    if hasattr(sys, 'executable') and sys.executable:
        return sys.executable
    
    return None


def ensure_dir_exists(path: Union[str, Path]) -> bool:
    """Ensure a directory exists.

    Args:
        path (Union[str, Path]): The directory path.

    Returns:
        bool: True if the directory exists or was created, False otherwise.
    """
    from backend.base.logging import LOGGER
    
    if isinstance(path, str):
        path = Path(path)
    
    LOGGER.info(f"Ensuring directory exists: {path}")
    
    try:
        path.mkdir(parents=True, exist_ok=True)
        LOGGER.info(f"Directory created or already exists: {path}")
        return True
    except Exception as e:
        LOGGER.error(f"Error creating directory {path}: {e}")
        return False


def get_app_dir() -> Path:
    """Get the application directory.

    Returns:
        Path: The application directory.
    """
    return Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def get_data_dir() -> Path:
    """Get the data directory.

    Returns:
        Path: The data directory.
    """
    app_dir = get_app_dir()
    data_dir = app_dir / "data"
    ensure_dir_exists(data_dir)
    return data_dir


def get_config_dir() -> Path:
    """Get the configuration directory.

    Returns:
        Path: The configuration directory.
    """
    data_dir = get_data_dir()
    config_dir = data_dir / "config"
    ensure_dir_exists(config_dir)
    return config_dir


def get_logs_dir() -> Path:
    """Get the logs directory.

    Returns:
        Path: The logs directory.
    """
    data_dir = get_data_dir()
    logs_dir = data_dir / "logs"
    ensure_dir_exists(logs_dir)
    return logs_dir


def get_ebook_storage_dir() -> Path:
    """Get the e-book storage directory.

    Returns:
        Path: The e-book storage directory.
    """
    data_dir = get_data_dir()
    
    # Try to get the ebook_storage setting
    try:
        from backend.internals.settings import Settings
        settings = Settings().get_settings()
        ebook_storage = settings.ebook_storage
    except Exception:
        # If there's an error (e.g., during initial setup), use the default
        from backend.base.definitions import Constants
        ebook_storage = Constants.DEFAULT_EBOOK_STORAGE
    
    # Handle absolute and relative paths
    ebook_path = Path(ebook_storage)
    if ebook_path.is_absolute():
        ebook_dir = ebook_path
    else:
        ebook_dir = data_dir / ebook_storage
    
    ensure_dir_exists(ebook_dir)
    return ebook_dir


def organize_ebook_path(series_id: int, volume_id: int, filename: str) -> Path:
    """Organize e-book path by series title and volume.

    Args:
        series_id (int): The series ID.
        volume_id (int): The volume ID.
        filename (str): The original filename.

    Returns:
        Path: The organized path for the e-book file.
    """
    from backend.internals.db import execute_query
    from backend.base.logging import LOGGER
    from backend.internals.settings import Settings
    
    # Get series info
    series_info = execute_query(
        "SELECT title, content_type, custom_path FROM series WHERE id = ?", 
        (series_id,)
    )
    
    if not series_info:
        # Fallback to old structure if series not found
        ebook_dir = get_ebook_storage_dir()
        series_dir = ebook_dir / f"series_{series_id}"
        ensure_dir_exists(series_dir)
        return series_dir / filename
    
    # Get series title, content type, and custom path
    series_title = series_info[0]['title']
    content_type = series_info[0].get('content_type', 'MANGA')
    custom_path = series_info[0].get('custom_path')
    
    # Get volume info
    volume_info = execute_query(
        "SELECT volume_number FROM volumes WHERE id = ?", 
        (volume_id,)
    )
    volume_number = volume_info[0]['volume_number'] if volume_info else f"volume_{volume_id}"
    
    # Create safe directory name
    safe_series_title = get_safe_folder_name(series_title)
    
    # Check if custom path is set
    if custom_path:
        LOGGER.info(f"Using custom path for series {series_id}: {custom_path}")
        series_dir = Path(custom_path)
    else:
        # Get root folders from settings
        settings = Settings().get_settings()
        root_folders = settings.root_folders
        
        # Determine the series directory
        if not root_folders:
            # If no root folders configured, use default ebook storage
            ebook_dir = get_ebook_storage_dir()
            series_dir = ebook_dir / safe_series_title
        else:
            # Use the first root folder
            root_folder = root_folders[0]
            root_path = Path(root_folder['path'])
            series_dir = root_path / safe_series_title
    
    # Create directories
    ensure_dir_exists(series_dir)
    
    # Return full path without adding Volume_ prefix
    return series_dir / filename


def get_safe_folder_name(name: str) -> str:
    """Create a safe folder name from a string.

    Args:
        name (str): The original name.

    Returns:
        str: A safe folder name that preserves spaces but replaces invalid characters.
    """
    from backend.base.logging import LOGGER
    
    # Characters not allowed in Windows filenames
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    
    # Replace invalid characters with underscores but keep spaces and other valid characters
    safe_name = name
    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Remove leading/trailing periods and spaces as they can cause issues
    safe_name = safe_name.strip('. ')
    
    # Ensure the name is not empty
    if not safe_name:
        safe_name = "unnamed"
    
    LOGGER.info(f"Original name: '{name}', Safe name: '{safe_name}'")
    return safe_name


def ensure_readme_file(series_dir: Path, series_title: str, series_id: int, content_type: str) -> bool:
    """Ensure a README file exists in the series directory.

    Args:
        series_dir (Path): The series directory.
        series_title (str): The series title.
        series_id (int): The series ID.
        content_type (str): The content type.

    Returns:
        bool: True if the README file exists or was created, False otherwise.
    """
    from backend.base.logging import LOGGER
    import os
    
    readme_path = series_dir / "README.txt"
    LOGGER.info(f"Ensuring README file exists: {readme_path}")
    
    if readme_path.exists():
        LOGGER.info(f"README file already exists: {readme_path}")
        return True
    
    try:
        # Make sure the directory exists
        if not series_dir.exists():
            LOGGER.warning(f"Series directory does not exist: {series_dir}")
            try:
                LOGGER.info(f"Creating series directory: {series_dir}")
                os.makedirs(str(series_dir), exist_ok=True)
                LOGGER.info(f"Series directory created: {series_dir}, exists: {series_dir.exists()}")
            except Exception as e:
                LOGGER.error(f"Failed to create series directory: {e}")
                import traceback
                LOGGER.error(traceback.format_exc())
                return False
        
        # Create the README file
        LOGGER.info(f"Creating README file: {readme_path}")
        with open(readme_path, 'w') as f:
            f.write(f"Series: {series_title}\n")
            f.write(f"ID: {series_id}\n")
            f.write(f"Type: {content_type}\n")
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\nThis folder is managed by Readloom. Place your e-book files here.\n")
        
        # Verify the file was created
        if readme_path.exists():
            LOGGER.info(f"README file created successfully: {readme_path}")
            return True
        else:
            LOGGER.error(f"Failed to create README file: {readme_path}")
            return False
    except Exception as e:
        LOGGER.error(f"Error creating README file: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


def create_series_folder_structure(series_id: int, series_title: str, content_type: str, collection_id: Optional[int] = None, root_folder_id: Optional[int] = None) -> Path:
    """Create folder structure for a series.

    Args:
        series_id (int): The series ID.
        series_title (str): The series title.
        content_type (str): The content type.
        collection_id (Optional[int], optional): The collection ID. Defaults to None.

    Returns:
        Path: The path to the series folder.
    """
    from backend.base.logging import LOGGER
    from backend.internals.db import execute_query
    import os
    
    LOGGER.info(f"Creating folder structure for series: {series_title} (ID: {series_id}, Type: {content_type})")
    
    # Create directory name that preserves spaces but replaces invalid characters
    safe_series_title = get_safe_folder_name(series_title)
    LOGGER.info(f"Original series title: '{series_title}', Safe series title for folder: '{safe_series_title}'")
    
    # If an explicit root_folder_id is provided, use it directly
    root_folders = []
    if root_folder_id is not None:
        LOGGER.info(f"Using explicit root_folder_id={root_folder_id}")
        query = "SELECT * FROM root_folders WHERE id = ?"
        root_folders = execute_query(query, (root_folder_id,))
    # Else if collection_id is provided, get root folders for that collection
    elif collection_id is not None:
        LOGGER.info(f"Getting root folders for collection ID: {collection_id}")
        query = """
        SELECT rf.* FROM root_folders rf
        JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
        WHERE crf.collection_id = ?
        ORDER BY rf.name ASC
        """
        root_folders = execute_query(query, (collection_id,))
        LOGGER.info(f"Found {len(root_folders)} root folders for collection ID {collection_id}")
    
    # If no collection specified or no root folders found for the collection, use default root folders
    if not root_folders:
        LOGGER.info("No collection-specific root folders found, checking for per-type default collection")
        # Try to get the default collection for this content_type
        default_collections = execute_query("SELECT id FROM collections WHERE is_default = 1 AND UPPER(content_type) = UPPER(?)", (content_type,))
        if default_collections:
            default_collection_id = default_collections[0]["id"]
            LOGGER.info(f"Using default collection ID: {default_collection_id}")
            query = """
            SELECT rf.* FROM root_folders rf
            JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
            WHERE crf.collection_id = ?
            ORDER BY rf.name ASC
            """
            root_folders = execute_query(query, (default_collection_id,))
            LOGGER.info(f"Found {len(root_folders)} root folders for default collection")
    
    # If still no root folders, use the first root folder from the database
    if not root_folders:
        LOGGER.info("No collection-specific or default root folders found, checking for any root folders")
        root_folders = execute_query("SELECT * FROM root_folders ORDER BY name ASC LIMIT 1")
        LOGGER.info(f"Found {len(root_folders)} root folders in database")
    
    # If still no root folders, use default ebook storage
    if not root_folders:
        LOGGER.warning("No root folders configured, using default ebook storage")
        # Use default ebook storage directory
        ebook_dir = get_ebook_storage_dir()
        LOGGER.info(f"E-book directory: {ebook_dir}")
        
        # Create series directory directly in the ebook directory
        series_dir = ebook_dir / safe_series_title
    else:
        # Use the first root folder
        root_folder = root_folders[0]
        LOGGER.info(f"Using root folder: {root_folder['name']} ({root_folder['path']})")
        
        # Create series directory directly in the root folder
        root_path = Path(root_folder['path'])
        LOGGER.info(f"Root path exists: {root_path.exists()}, is directory: {root_path.is_dir() if root_path.exists() else False}")
        
        # Check if root path exists, if not try to create it
        if not root_path.exists():
            try:
                LOGGER.info(f"Root path doesn't exist, creating: {root_path}")
                root_path.mkdir(parents=True, exist_ok=True)
                LOGGER.info(f"Created root path: {root_path}")
            except Exception as e:
                LOGGER.error(f"Failed to create root path: {e}")
                import traceback
                LOGGER.error(traceback.format_exc())
        
        series_dir = root_path / safe_series_title
    
    LOGGER.info(f"Series directory: {series_dir}")
    
    # Create series directory using os.makedirs for more robust directory creation
    try:
        LOGGER.info(f"Attempting to create directory: {series_dir}")
        os.makedirs(str(series_dir), exist_ok=True)
        LOGGER.info(f"Directory created or already exists: {series_dir}")
        LOGGER.info(f"Directory exists after creation: {series_dir.exists()}, is directory: {series_dir.is_dir() if series_dir.exists() else False}")
    except Exception as e:
        LOGGER.error(f"Error creating series directory: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        raise  # Re-raise to ensure caller knows there was an error
    
    # Create a README file with series information
    ensure_readme_file(series_dir, series_title, series_id, content_type)
    
    return series_dir


def copy_file_to_storage(source_path: Union[str, Path], target_path: Union[str, Path]) -> bool:
    """Copy a file to the storage location.

    Args:
        source_path (Union[str, Path]): The source file path.
        target_path (Union[str, Path]): The target file path.

    Returns:
        bool: True if the file was copied successfully, False otherwise.
    """
    try:
        if isinstance(source_path, str):
            source_path = Path(source_path)
        if isinstance(target_path, str):
            target_path = Path(target_path)
            
        if not source_path.exists() or not source_path.is_file():
            return False
        
        # Ensure the target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(source_path, target_path)
        return True
    except Exception:
        return False
