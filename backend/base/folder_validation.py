#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Folder validation utilities for checking if folders exist and are writable.
"""

import os
from pathlib import Path
from typing import Dict, Any

from backend.base.logging import LOGGER


def validate_folder(folder_path: str) -> Dict[str, Any]:
    """Validate if a folder exists and is writable.
    
    Args:
        folder_path (str): The path to the folder to validate.
        
    Returns:
        Dict[str, Any]: A dictionary containing validation results:
            - valid (bool): True if the folder is valid, False otherwise.
            - exists (bool): True if the folder exists, False otherwise.
            - writable (bool): True if the folder is writable, False otherwise.
            - message (str): A message describing the validation result.
    """
    result = {
        "valid": False,
        "exists": False,
        "writable": False,
        "message": ""
    }
    
    try:
        path = Path(folder_path)
        
        # Check if the path exists
        if not path.exists():
            result["message"] = f"Folder '{folder_path}' does not exist"
            return result
        
        result["exists"] = True
        
        # Check if it's a directory
        if not path.is_dir():
            result["message"] = f"Path '{folder_path}' is not a directory"
            return result
        
        # Check if it's writable
        if not os.access(path, os.W_OK):
            result["message"] = f"Folder '{folder_path}' is not writable"
            return result
        
        result["writable"] = True
        result["valid"] = True
        result["message"] = f"Folder '{folder_path}' exists and is writable"
        
    except Exception as e:
        LOGGER.error(f"Error validating folder '{folder_path}': {e}")
        result["message"] = f"Error validating folder: {str(e)}"
    
    return result


def create_folder_if_not_exists(folder_path: str) -> Dict[str, Any]:
    """Create a folder if it doesn't exist and validate it.
    
    Args:
        folder_path (str): The path to the folder to create and validate.
        
    Returns:
        Dict[str, Any]: A dictionary containing validation results:
            - valid (bool): True if the folder is valid, False otherwise.
            - exists (bool): True if the folder exists, False otherwise.
            - writable (bool): True if the folder is writable, False otherwise.
            - message (str): A message describing the validation result.
            - created (bool): True if the folder was created, False otherwise.
    """
    result = validate_folder(folder_path)
    result["created"] = False
    
    if not result["exists"]:
        try:
            path = Path(folder_path)
            path.mkdir(parents=True, exist_ok=True)
            result["created"] = True
            
            # Re-validate the folder
            validation = validate_folder(folder_path)
            result.update(validation)
            
            if result["valid"]:
                result["message"] = f"Folder '{folder_path}' was created successfully"
            
        except Exception as e:
            LOGGER.error(f"Error creating folder '{folder_path}': {e}")
            result["message"] = f"Error creating folder: {str(e)}"
    
    return result
