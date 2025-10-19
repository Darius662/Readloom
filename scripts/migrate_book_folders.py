#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to migrate book folders to author-based structure.
"""

import os
import sys
import shutil
from pathlib import Path

# Add parent directory to path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.base.logging import setup_logging, LOGGER
from backend.internals.db import set_db_location, execute_query
from backend.base.helpers import get_safe_folder_name


def migrate_book_folders():
    """Migrate book folders to author-based structure."""
    # Set up logging
    setup_logging("data/logs", "migrate_book_folders.log")
    LOGGER.info("Starting book folder migration")
    
    # Set database location
    set_db_location("data/db")
    
    # Get all books with their authors
    books = execute_query("""
        SELECT s.id, s.title, a.id as author_id, a.name as author_name
        FROM series s
        JOIN book_authors ba ON s.id = ba.book_id
        JOIN authors a ON ba.author_id = a.id
        WHERE s.is_book = 1 AND ba.is_primary = 1
    """)
    
    LOGGER.info(f"Found {len(books)} books to migrate")
    
    # Get root folders from settings
    from backend.internals.settings import Settings
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    if not root_folders:
        LOGGER.error("No root folders found.")
        return
    
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    for book in books:
        book_id = book['id']
        book_title = book['title']
        author_name = book['author_name']
        
        LOGGER.info(f"Processing book: {book_title} by {author_name} (ID: {book_id})")
        
        # Create safe folder names
        safe_book_title = get_safe_folder_name(book_title)
        safe_author_name = get_safe_folder_name(author_name)
        
        # Find the current book folder
        current_folder = None
        for root_folder in root_folders:
            root_path = Path(root_folder['path'])
            potential_book_dir = root_path / safe_book_title
            
            if potential_book_dir.exists() and potential_book_dir.is_dir():
                current_folder = potential_book_dir
                LOGGER.info(f"Found existing book folder: {current_folder}")
                break
        
        if not current_folder:
            LOGGER.warning(f"Could not find folder for book: {book_title}")
            skipped_count += 1
            continue
        
        # Create author folder if it doesn't exist
        author_folder = current_folder.parent / safe_author_name
        if not author_folder.exists():
            try:
                author_folder.mkdir(exist_ok=True)
                LOGGER.info(f"Created author folder: {author_folder}")
            except Exception as e:
                LOGGER.error(f"Error creating author folder: {e}")
                error_count += 1
                continue
        
        # Move book folder into author folder
        new_book_folder = author_folder / safe_book_title
        if new_book_folder.exists():
            LOGGER.warning(f"Destination already exists: {new_book_folder}")
            skipped_count += 1
            continue
        
        try:
            # Copy the folder first
            shutil.copytree(str(current_folder), str(new_book_folder))
            LOGGER.info(f"Copied {current_folder} to {new_book_folder}")
            
            # Update the custom_path in the database
            execute_query(
                "UPDATE series SET custom_path = ? WHERE id = ?",
                (str(new_book_folder), book_id),
                commit=True
            )
            LOGGER.info(f"Updated custom_path for book {book_id} to {new_book_folder}")
            
            # Delete the original folder
            shutil.rmtree(str(current_folder))
            LOGGER.info(f"Removed original folder: {current_folder}")
            
            migrated_count += 1
        except Exception as e:
            LOGGER.error(f"Error migrating folder: {e}")
            error_count += 1
    
    LOGGER.info(f"Migration completed: {migrated_count} migrated, {skipped_count} skipped, {error_count} errors")
    print(f"Migration completed: {migrated_count} migrated, {skipped_count} skipped, {error_count} errors")


if __name__ == "__main__":
    migrate_book_folders()
