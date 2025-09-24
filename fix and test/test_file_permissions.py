#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FilePermissionTest")

def test_file_creation(directory_path):
    """Test if we can create files in the specified directory."""
    try:
        # Convert to Path object if string
        directory = Path(directory_path)
        
        # Check if directory exists
        logger.info(f"Checking if directory exists: {directory}")
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            try:
                logger.info(f"Attempting to create directory: {directory}")
                os.makedirs(str(directory), exist_ok=True)
                logger.info(f"Directory created: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory: {e}")
                return False
        
        # Try to create a test file
        test_file = directory / "test_permissions.txt"
        logger.info(f"Attempting to create test file: {test_file}")
        
        import datetime
        with open(test_file, 'w') as f:
            f.write("This is a test file to check write permissions.\n")
            f.write(f"Created at: {datetime.datetime.now()}\n")
        
        # Verify file was created
        if test_file.exists():
            logger.info(f"Successfully created test file: {test_file}")
            
            # Try to delete the test file
            try:
                logger.info(f"Attempting to delete test file: {test_file}")
                os.remove(test_file)
                logger.info(f"Successfully deleted test file: {test_file}")
            except Exception as e:
                logger.warning(f"Could not delete test file: {e}")
            
            return True
        else:
            logger.error(f"Failed to create test file: {test_file}")
            return False
            
    except Exception as e:
        logger.error(f"Error testing file creation: {e}")
        return False

if __name__ == "__main__":
    # Test the root folder
    root_folder = "C:\\Users\\dariu\\Documents\\Mangas"
    logger.info(f"Testing file creation in root folder: {root_folder}")
    
    result = test_file_creation(root_folder)
    logger.info(f"Root folder test result: {'Success' if result else 'Failed'}")
    
    # Test a series folder
    series_folder = Path(root_folder) / "Tensei Shitara Slime Datta Ken"
    logger.info(f"Testing file creation in series folder: {series_folder}")
    
    result = test_file_creation(series_folder)
    logger.info(f"Series folder test result: {'Success' if result else 'Failed'}")
