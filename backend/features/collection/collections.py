#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collection management functions for Readloom.

This module provides functions for managing collections and their relationships
with root folders and series.
"""

from typing import Dict, List, Optional, Any, Union
import os
from pathlib import Path

from backend.base.custom_exceptions import DatabaseError, InvalidCollectionError
from backend.base.logging import LOGGER
from backend.base.helpers import ensure_dir_exists
from backend.internals.db import execute_query


def create_collection(name: str, description: str = "", is_default: bool = False, content_type: str = "MANGA") -> int:
    """Create a new collection.

    Args:
        name (str): The name of the collection.
        description (str, optional): The description of the collection. Defaults to "".
        is_default (bool, optional): Whether this is the default collection. Defaults to False.

    Returns:
        int: The ID of the newly created collection.

    Raises:
        InvalidCollectionError: If the collection name is invalid or already exists.
    """
    if not name:
        raise InvalidCollectionError("Collection name cannot be empty")
    
    # Check if collection with this name already exists
    existing = execute_query("SELECT id FROM collections WHERE name = ?", (name,))
    if existing:
        raise InvalidCollectionError(f"Collection with name '{name}' already exists")
    
    try:
        # First, try to fix any constraint issues in the database
        try:
            # Check if the unique_default constraint exists and is causing problems
            constraints = execute_query("PRAGMA table_info(collections)")
            has_constraint = False
            for constraint in constraints:
                if "unique_default" in str(constraint):
                    has_constraint = True
                    break
                    
            if has_constraint:
                LOGGER.warning("Found problematic unique_default constraint, attempting to fix...")
                
                # Try to create a unique index that will enforce only one default collection
                try:
                    execute_query("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_default 
                    ON collections(is_default) WHERE is_default = 1
                    """, commit=True)
                except Exception as e:
                    LOGGER.warning(f"Could not create index: {e}")
        except Exception as e:
            LOGGER.warning(f"Error checking constraints: {e}")
            
        # If this is set as default, unset any existing default for the same content_type
        if is_default:
            execute_query(
                "UPDATE collections SET is_default = 0 WHERE COALESCE(content_type, 'MANGA') = ?",
                (content_type or "MANGA",),
                commit=True,
            )
        
        # Create the collection
        execute_query(
            "INSERT INTO collections (name, description, content_type, is_default) VALUES (?, ?, ?, ?)",
            (name, description, content_type or "MANGA", 1 if is_default else 0),
            commit=True
        )
    except Exception as e:
        # If the constraint is still causing issues, try a more direct approach
        if "unique_default" in str(e):
            LOGGER.warning(f"Constraint error: {e}, trying alternative approach")
            
            # Create the collection without setting default flag
            execute_query(
                "INSERT INTO collections (name, description, content_type, is_default) VALUES (?, ?, ?, 0)",
                (name, description, content_type or "MANGA"),
                commit=True
            )
            
            # Get the ID
            result = execute_query("SELECT id FROM collections WHERE name = ?", (name,))
            if not result:
                raise DatabaseError("Failed to create collection")
            
            collection_id = result[0]["id"]
            
            # If we need to set as default, do it in a separate update
            if is_default:
                try:
                    # Unset any existing default for same type
                    execute_query(
                        "UPDATE collections SET is_default = 0 WHERE COALESCE(content_type, 'MANGA') = ?",
                        (content_type or "MANGA",),
                        commit=True,
                    )
                    
                    # Set this one as default
                    execute_query(
                        "UPDATE collections SET is_default = 1 WHERE id = ?",
                        (collection_id,),
                        commit=True
                    )
                except Exception as update_err:
                    LOGGER.warning(f"Could not set collection as default: {update_err}")
            
            LOGGER.info(f"Created collection '{name}' with ID {collection_id} using alternative approach")
            return collection_id
        else:
            # If it's a different error, re-raise it
            raise
    
    # Get the ID of the newly created collection
    result = execute_query("SELECT id FROM collections WHERE name = ?", (name,))
    if not result:
        raise DatabaseError("Failed to create collection")
    
    collection_id = result[0]["id"]
    LOGGER.info(f"Created collection '{name}' with ID {collection_id}")
    return collection_id


def get_collections() -> List[Dict[str, Any]]:
    """Get all collections.

    Returns:
        List[Dict[str, Any]]: A list of collections.
    """
    collections = execute_query("SELECT * FROM collections ORDER BY content_type ASC, is_default DESC, name ASC")
    
    # Add root folder count to each collection
    for collection in collections:
        folder_count = execute_query(
            "SELECT COUNT(*) as count FROM collection_root_folders WHERE collection_id = ?",
            (collection["id"],)
        )
        collection["root_folder_count"] = folder_count[0]["count"] if folder_count else 0
        
        series_count = execute_query(
            "SELECT COUNT(*) as count FROM series_collections WHERE collection_id = ?",
            (collection["id"],)
        )
        collection["series_count"] = series_count[0]["count"] if series_count else 0
    
    return collections


def get_collection_by_id(collection_id: int) -> Optional[Dict[str, Any]]:
    """Get a collection by ID.

    Args:
        collection_id (int): The ID of the collection.

    Returns:
        Optional[Dict[str, Any]]: The collection, or None if not found.
    """
    collections = execute_query("SELECT * FROM collections WHERE id = ?", (collection_id,))
    if not collections:
        return None
    
    collection = collections[0]
    
    # Add root folder count
    folder_count = execute_query(
        "SELECT COUNT(*) as count FROM collection_root_folders WHERE collection_id = ?",
        (collection_id,)
    )
    collection["root_folder_count"] = folder_count[0]["count"] if folder_count else 0
    
    # Add series count
    series_count = execute_query(
        "SELECT COUNT(*) as count FROM series_collections WHERE collection_id = ?",
        (collection_id,)
    )
    return collection

def update_collection(collection_id: int, name: Optional[str] = None,
                      description: Optional[str] = None, is_default: Optional[bool] = None,
                      content_type: Optional[str] = None) -> bool:
    """Update a collection.

    Args:
        collection_id (int): The ID of the collection to update.
        name (Optional[str], optional): The new name of the collection. Defaults to None.
        description (Optional[str], optional): The new description of the collection. Defaults to None.
        is_default (Optional[bool], optional): Whether this is the default collection. Defaults to None.
        content_type (Optional[str], optional): The content type for the collection. Defaults to None.

    Returns:
        bool: True if the collection was updated, False otherwise.

    Raises:
        InvalidCollectionError: If the collection doesn't exist or name conflicts.
    """
    # Check if collection exists
    collection = get_collection_by_id(collection_id)
    if not collection:
        raise InvalidCollectionError(f"Collection with ID {collection_id} does not exist")

    updates: List[str] = []
    params: List[Any] = []

    if name is not None:
        if not name:
            raise InvalidCollectionError("Collection name cannot be empty")
        # Ensure unique name
        existing = execute_query(
            "SELECT id FROM collections WHERE name = ? AND id != ?",
            (name, collection_id)
        )
        if existing:
            raise InvalidCollectionError(f"Collection with name '{name}' already exists")
        updates.append("name = ?")
        params.append(name)

    if description is not None:
        updates.append("description = ?")
        params.append(description)

    if content_type is not None:
        updates.append("content_type = ?")
        params.append(content_type)

    if is_default is not None:
        updates.append("is_default = ?")
        params.append(1 if is_default else 0)
        if is_default:
            # Determine target type for uniqueness
            target_type = content_type if content_type is not None else collection.get("content_type") or "MANGA"
            execute_query(
                "UPDATE collections SET is_default = 0 WHERE id != ? AND COALESCE(content_type, 'MANGA') = ?",
                (collection_id, target_type),
                commit=True
            )

    if not updates:
        return False

    query = f"UPDATE collections SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    params.append(collection_id)
    execute_query(query, tuple(params), commit=True)
    LOGGER.info(f"Updated collection with ID {collection_id}")
    return True


def delete_collection(collection_id: int) -> bool:
    """Delete a collection.

    Args:
        collection_id (int): The ID of the collection to delete.

    Returns:
        bool: True if the collection was deleted, False otherwise.

    Raises:
        InvalidCollectionError: If trying to delete the default collection or if the collection doesn't exist.
    """
    # Check if collection exists
    collection = get_collection_by_id(collection_id)
    if not collection:
        raise InvalidCollectionError(f"Collection with ID {collection_id} does not exist")
    
    # Don't allow deleting the default collection
    if collection.get("is_default", 0) == 1:
        raise InvalidCollectionError("Cannot delete the default collection")
    
    # Delete the collection (cascade will handle relationships)
    execute_query("DELETE FROM collections WHERE id = ?", (collection_id,), commit=True)
    LOGGER.info(f"Deleted collection with ID {collection_id}")
    return True


def create_root_folder(path: str, name: str, content_type: str = "MANGA") -> int:
    """Create a new root folder.

    Args:
        path (str): The path to the root folder.
        name (str): The name of the root folder.
        content_type (str, optional): The content type of the root folder. Defaults to "MANGA".

    Returns:
        int: The ID of the newly created root folder.

    Raises:
        InvalidCollectionError: If the path is invalid or already exists.
    """
    if not path or not name:
        raise InvalidCollectionError("Root folder path and name cannot be empty")
    
    # Normalize path
    path = os.path.normpath(path)
    
    # Check if root folder with this path already exists
    existing = execute_query("SELECT id FROM root_folders WHERE path = ?", (path,))
    if existing:
        raise InvalidCollectionError(f"Root folder with path '{path}' already exists")
    
    # Check if the directory exists
    if not os.path.exists(path):
        raise InvalidCollectionError(f"Directory '{path}' does not exist. Please create it first.")
    
    if not os.path.isdir(path):
        raise InvalidCollectionError(f"Path '{path}' is not a directory.")
        
    # Directory exists, we can use it
    
    # Create the root folder
    execute_query(
        "INSERT INTO root_folders (path, name, content_type) VALUES (?, ?, ?)",
        (path, name, content_type),
        commit=True
    )
    
    # Get the ID of the newly created root folder
    result = execute_query("SELECT id FROM root_folders WHERE path = ?", (path,))
    if not result:
        raise DatabaseError("Failed to create root folder")
    
    root_folder_id = result[0]["id"]
    
    # Update the root_folders setting
    from backend.internals.settings import Settings
    settings = Settings()
    
    # Get current root folders
    current_settings = settings.get_settings()
    current_root_folders = current_settings.root_folders
    
    # Add the new root folder
    new_root_folder = {
        "id": root_folder_id,
        "path": path,
        "name": name,
        "content_type": content_type
    }
    
    # Update the setting
    current_root_folders.append(new_root_folder)
    settings.update({"root_folders": current_root_folders})
    
    LOGGER.info(f"Created root folder '{name}' at '{path}' with ID {root_folder_id}")
    return root_folder_id


def get_root_folders() -> List[Dict[str, Any]]:
    """Get all root folders.

    Returns:
        List[Dict[str, Any]]: A list of root folders.
    """
    root_folders = execute_query("SELECT * FROM root_folders ORDER BY name ASC")
    
    # Add collection count to each root folder
    for folder in root_folders:
        collection_count = execute_query(
            "SELECT COUNT(*) as count FROM collection_root_folders WHERE root_folder_id = ?",
            (folder["id"],)
        )
        folder["collection_count"] = collection_count[0]["count"] if collection_count else 0
        
        # Check if directory exists
        folder["exists"] = os.path.exists(folder["path"]) and os.path.isdir(folder["path"])
    
    return root_folders


def get_root_folder_by_id(root_folder_id: int) -> Optional[Dict[str, Any]]:
    """Get a root folder by ID.

    Args:
        root_folder_id (int): The ID of the root folder.

    Returns:
        Optional[Dict[str, Any]]: The root folder, or None if not found.
    """
    root_folders = execute_query("SELECT * FROM root_folders WHERE id = ?", (root_folder_id,))
    if not root_folders:
        return None
    
    root_folder = root_folders[0]
    
    # Add collection count
    collection_count = execute_query(
        "SELECT COUNT(*) as count FROM collection_root_folders WHERE root_folder_id = ?",
        (root_folder_id,)
    )
    root_folder["collection_count"] = collection_count[0]["count"] if collection_count else 0
    
    # Check if directory exists
    root_folder["exists"] = os.path.exists(root_folder["path"]) and os.path.isdir(root_folder["path"])
    
    return root_folder


def update_root_folder(root_folder_id: int, path: Optional[str] = None, 
                       name: Optional[str] = None, content_type: Optional[str] = None) -> bool:
    """Update a root folder.

    Args:
        root_folder_id (int): The ID of the root folder to update.
        path (Optional[str], optional): The new path of the root folder. Defaults to None.
        name (Optional[str], optional): The new name of the root folder. Defaults to None.
        content_type (Optional[str], optional): The new content type of the root folder. Defaults to None.

    Returns:
        bool: True if the root folder was updated, False otherwise.

    Raises:
        InvalidCollectionError: If the path is invalid or already exists.
    """
    # Check if root folder exists
    root_folder = get_root_folder_by_id(root_folder_id)
    if not root_folder:
        raise InvalidCollectionError(f"Root folder with ID {root_folder_id} does not exist")
    
    # Build update query
    updates = []
    params = []
    
    if path is not None:
        if not path:
            raise InvalidCollectionError("Root folder path cannot be empty")
        
        # Normalize path
        path = os.path.normpath(path)
        
        # Check if another root folder with this path already exists
        existing = execute_query(
            "SELECT id FROM root_folders WHERE path = ? AND id != ?", 
            (path, root_folder_id)
        )
        if existing:
            raise InvalidCollectionError(f"Root folder with path '{path}' already exists")
        
        # Ensure the directory exists
        try:
            ensure_dir_exists(path)
        except Exception as e:
            raise InvalidCollectionError(f"Failed to create directory at '{path}': {e}")
        
        updates.append("path = ?")
        params.append(path)
    
    if name is not None:
        if not name:
            raise InvalidCollectionError("Root folder name cannot be empty")
        
        updates.append("name = ?")
        params.append(name)
    
    if content_type is not None:
        updates.append("content_type = ?")
        params.append(content_type)
    
    if not updates:
        return False  # Nothing to update
    
    # Execute update query
    query = f"UPDATE root_folders SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    params.append(root_folder_id)
    
    execute_query(query, tuple(params), commit=True)
    LOGGER.info(f"Updated root folder with ID {root_folder_id}")
    return True


def delete_root_folder(root_folder_id: int) -> bool:
    """Delete a root folder.

    Args:
        root_folder_id (int): The ID of the root folder to delete.

    Returns:
        bool: True if the root folder was deleted, False otherwise.

    Raises:
        InvalidCollectionError: If the root folder doesn't exist.
    """
    # Check if root folder exists
    root_folder = get_root_folder_by_id(root_folder_id)
    if not root_folder:
        raise InvalidCollectionError(f"Root folder with ID {root_folder_id} does not exist")
    
    # Update the root_folders setting
    from backend.internals.settings import Settings
    settings = Settings()
    
    # Get current root folders
    current_settings = settings.get_settings()
    current_root_folders = current_settings.root_folders
    
    # Remove the root folder from the settings
    updated_root_folders = [rf for rf in current_root_folders if rf.get('id') != root_folder_id]
    settings.update({"root_folders": updated_root_folders})
    
    # Delete the root folder (cascade will handle relationships)
    execute_query("DELETE FROM root_folders WHERE id = ?", (root_folder_id,), commit=True)
    LOGGER.info(f"Deleted root folder with ID {root_folder_id}")
    return True


def add_root_folder_to_collection(collection_id: int, root_folder_id: int) -> bool:
    """Add a root folder to a collection.

    Args:
        collection_id (int): The ID of the collection.
        root_folder_id (int): The ID of the root folder.

    Returns:
        bool: True if the root folder was added to the collection, False otherwise.

    Raises:
        InvalidCollectionError: If the collection or root folder doesn't exist.
    """
    # Check if collection exists
    collection = get_collection_by_id(collection_id)
    if not collection:
        raise InvalidCollectionError(f"Collection with ID {collection_id} does not exist")
    
    # Check if root folder exists
    root_folder = get_root_folder_by_id(root_folder_id)
    if not root_folder:
        raise InvalidCollectionError(f"Root folder with ID {root_folder_id} does not exist")
    
    # Check if relationship already exists
    existing = execute_query(
        "SELECT id FROM collection_root_folders WHERE collection_id = ? AND root_folder_id = ?",
        (collection_id, root_folder_id)
    )
    if existing:
        return False  # Relationship already exists
    
    # Add the relationship
    execute_query(
        "INSERT INTO collection_root_folders (collection_id, root_folder_id) VALUES (?, ?)",
        (collection_id, root_folder_id),
        commit=True
    )
    
    LOGGER.info(f"Added root folder {root_folder_id} to collection {collection_id}")
    return True


def remove_root_folder_from_collection(collection_id: int, root_folder_id: int) -> bool:
    """Remove a root folder from a collection.

    Args:
        collection_id (int): The ID of the collection.
        root_folder_id (int): The ID of the root folder.

    Returns:
        bool: True if the root folder was removed from the collection, False otherwise.

    Raises:
        InvalidCollectionError: If the collection or root folder doesn't exist.
    """
    # Check if collection exists
    collection = get_collection_by_id(collection_id)
    if not collection:
        raise InvalidCollectionError(f"Collection with ID {collection_id} does not exist")
    
    # Check if root folder exists
    root_folder = get_root_folder_by_id(root_folder_id)
    if not root_folder:
        raise InvalidCollectionError(f"Root folder with ID {root_folder_id} does not exist")
    
    # Remove the relationship
    execute_query(
        "DELETE FROM collection_root_folders WHERE collection_id = ? AND root_folder_id = ?",
        (collection_id, root_folder_id),
        commit=True
    )
    
    LOGGER.info(f"Removed root folder {root_folder_id} from collection {collection_id}")
    return True


def get_collection_root_folders(collection_id: int) -> List[Dict[str, Any]]:
    """Get all root folders for a collection.

    Args:
        collection_id (int): The ID of the collection.

    Returns:
        List[Dict[str, Any]]: A list of root folders.

    Raises:
        InvalidCollectionError: If the collection doesn't exist.
    """
    # Check if collection exists
    collection = get_collection_by_id(collection_id)
    if not collection:
        raise InvalidCollectionError(f"Collection with ID {collection_id} does not exist")
    
    # Get root folders for the collection
    query = """
    SELECT rf.* FROM root_folders rf
    JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
    WHERE crf.collection_id = ?
    ORDER BY rf.name ASC
    """
    
    root_folders = execute_query(query, (collection_id,))
    
    # Check if directories exist
    for folder in root_folders:
        folder["exists"] = os.path.exists(folder["path"]) and os.path.isdir(folder["path"])
    
    return root_folders


def add_series_to_collection(collection_id: int, series_id: int) -> bool:
    """Add a series to a collection.

    Args:
        collection_id (int): The ID of the collection.
        series_id (int): The ID of the series.

    Returns:
        bool: True if the series was added to the collection, False otherwise.

    Raises:
        InvalidCollectionError: If the collection or series doesn't exist.
    """
    # Check if collection exists
    collection = get_collection_by_id(collection_id)
    if not collection:
        raise InvalidCollectionError(f"Collection with ID {collection_id} does not exist")
    
    # Check if series exists
    series = execute_query("SELECT id FROM series WHERE id = ?", (series_id,))
    if not series:
        raise InvalidCollectionError(f"Series with ID {series_id} does not exist")
    
    # Check if relationship already exists
    existing = execute_query(
        "SELECT id FROM series_collections WHERE collection_id = ? AND series_id = ?",
        (collection_id, series_id)
    )
    if existing:
        return False  # Relationship already exists
    
    # Add the relationship
    execute_query(
        "INSERT INTO series_collections (collection_id, series_id) VALUES (?, ?)",
        (collection_id, series_id),
        commit=True
    )
    
    LOGGER.info(f"Added series {series_id} to collection {collection_id}")
    return True


def remove_series_from_collection(collection_id: int, series_id: int) -> bool:
    """Remove a series from a collection.

    Args:
        collection_id (int): The ID of the collection.
        series_id (int): The ID of the series.

    Returns:
        bool: True if the series was removed from the collection, False otherwise.

    Raises:
        InvalidCollectionError: If the collection or series doesn't exist.
    """
    # Check if collection exists
    collection = get_collection_by_id(collection_id)
    if not collection:
        raise InvalidCollectionError(f"Collection with ID {collection_id} does not exist")
    
    # Check if series exists
    series = execute_query("SELECT id FROM series WHERE id = ?", (series_id,))
    if not series:
        raise InvalidCollectionError(f"Series with ID {series_id} does not exist")
    
    # Remove the relationship
    execute_query(
        "DELETE FROM series_collections WHERE collection_id = ? AND series_id = ?",
        (collection_id, series_id),
        commit=True
    )
    
    LOGGER.info(f"Removed series {series_id} from collection {collection_id}")
    return True


def get_collection_series(collection_id: int) -> List[Dict[str, Any]]:
    """Get all series for a collection.

    Args:
        collection_id (int): The ID of the collection.

    Returns:
        List[Dict[str, Any]]: A list of series.

    Raises:
        InvalidCollectionError: If the collection doesn't exist.
    """
    # Check if collection exists
    collection = get_collection_by_id(collection_id)
    if not collection:
        raise InvalidCollectionError(f"Collection with ID {collection_id} does not exist")
    
    # Get series for the collection
    query = """
    SELECT s.* FROM series s
    JOIN series_collections sc ON s.id = sc.series_id
    WHERE sc.collection_id = ?
    ORDER BY s.title ASC
    """
    
    return execute_query(query, (collection_id,))


def get_default_collection(content_type: Optional[str] = None) -> Dict[str, Any]:
    """Get the default collection.

    Returns:
        Dict[str, Any]: The default collection.

    Raises:
        DatabaseError: If no default collection exists.
    """
    # If a content_type is specified, scope all operations to that type
    type_clause = "COALESCE(content_type, 'MANGA') = ?"
    type_param = (content_type or "MANGA",)
    
    # First check if there are multiple default collections per specified type and fix if needed
    default_collections = execute_query(
        f"SELECT * FROM collections WHERE {type_clause} AND is_default = 1",
        type_param,
    )
    
    if len(default_collections) > 1:
        # Keep only the first default collection and unset the others
        LOGGER.warning(f"Found {len(default_collections)} default collections. Fixing...")
        first_default_id = default_collections[0]['id']
        execute_query(
            f"UPDATE collections SET is_default = 0 WHERE {type_clause} AND is_default = 1 AND id != ?",
            (*type_param, first_default_id),
            commit=True
        )
        # Refresh the list
        default_collections = execute_query(
            f"SELECT * FROM collections WHERE {type_clause} AND is_default = 1",
            type_param,
        )
    
    # Check for duplicate "Default Collection" entries and clean them up
    named_default_collections = execute_query(
        f"SELECT * FROM collections WHERE name = ? AND {type_clause}",
        ("Default Collection", *type_param),
    )
    if len(named_default_collections) > 1:
        LOGGER.warning(f"Found {len(named_default_collections)} collections named 'Default Collection'. Cleaning up...")
        
        # Find if any is marked as default
        default_among_named = next((c for c in named_default_collections if c['is_default'] == 1), None)
        
        if default_among_named:
            keep_id = default_among_named['id']
        else:
            keep_id = named_default_collections[0]['id']
            # Set this one as default
            execute_query("UPDATE collections SET is_default = 1 WHERE id = ?", (keep_id,), commit=True)
        
        # Delete all other "Default Collection" entries
        for collection in named_default_collections:
            if collection['id'] != keep_id:
                try:
                    # First remove any relationships
                    execute_query("DELETE FROM collection_root_folders WHERE collection_id = ?", (collection['id'],))
                    execute_query("DELETE FROM series_collections WHERE collection_id = ?", (collection['id'],))
                    
                    # Then delete the collection
                    execute_query("DELETE FROM collections WHERE id = ?", (collection['id'],), commit=True)
                    LOGGER.info(f"Deleted duplicate Default Collection with ID {collection['id']}")
                except Exception as e:
                    LOGGER.error(f"Error deleting duplicate collection {collection['id']}: {e}")
        
        # Refresh the default collections list
        default_collections = execute_query("SELECT * FROM collections WHERE is_default = 1")
    
    if not default_collections:
        # Check if there's a collection named 'Default Collection' already
        existing = execute_query(
            f"SELECT * FROM collections WHERE name = ? AND {type_clause}",
            ("Default Collection", *type_param),
        )
        
        if existing:
            # Set the existing one as default
            execute_query(
                "UPDATE collections SET is_default = 1 WHERE id = ?",
                (existing[0]['id'],),
                commit=True
            )
            LOGGER.info(f"Set existing collection '{existing[0]['name']}' as default")
            return existing[0]
        else:
            # Create a default collection if none exists
            collection_id = create_collection(
                "Default Collection",
                "Default collection created by the system",
                True,
                content_type=content_type or "MANGA",
            )
            collections = execute_query("SELECT * FROM collections WHERE id = ?", (collection_id,))
            if not collections:
                raise DatabaseError("Failed to create default collection")
            return collections[0]
    
    return default_collections[0]
