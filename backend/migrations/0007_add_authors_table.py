#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration to add authors table and related schema changes.
"""

from backend.base.logging import LOGGER


def migrate():
    """Add authors table and migrate existing book data."""
    from backend.internals.db import execute_query
    
    LOGGER.info("Starting migration: Adding authors table and related schema")
    
    try:
        # Create authors table
        execute_query("""
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                metadata_source TEXT,
                metadata_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """, commit=True)
        LOGGER.info("Created authors table")
        
        # Create book_authors table
        execute_query("""
            CREATE TABLE IF NOT EXISTS book_authors (
                book_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                is_primary BOOLEAN DEFAULT 0,
                PRIMARY KEY (book_id, author_id),
                FOREIGN KEY (book_id) REFERENCES series(id) ON DELETE CASCADE,
                FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
            )
        """, commit=True)
        LOGGER.info("Created book_authors table")
        
        # Add is_book column to series table if it doesn't exist
        # Check if column exists first
        columns = execute_query("PRAGMA table_info(series)")
        column_names = [col["name"] for col in columns]
        
        if "is_book" not in column_names:
            execute_query("""
                ALTER TABLE series ADD COLUMN is_book BOOLEAN DEFAULT 0
            """, commit=True)
            LOGGER.info("Added is_book column to series table")
        else:
            LOGGER.info("is_book column already exists in series table")
        
        # Update existing books
        books = execute_query("""
            SELECT id, title, author, content_type FROM series 
            WHERE content_type IN ('BOOK', 'NOVEL')
        """)
        
        LOGGER.info(f"Found {len(books)} books to update")
        
        for book in books:
            # Mark as book
            execute_query("""
                UPDATE series SET is_book = 1 WHERE id = ?
            """, (book['id'],), commit=True)
            
            # Extract author
            author_name = book['author']
            
            # Skip if no author
            if not author_name or author_name == "Unknown":
                LOGGER.warning(f"Book {book['id']} ({book['title']}) has no author, skipping")
                continue
            
            # Check if author exists
            existing_author = execute_query("""
                SELECT id FROM authors WHERE name = ?
            """, (author_name,))
            
            if existing_author:
                author_id = existing_author[0]['id']
                LOGGER.info(f"Found existing author: {author_name} (ID: {author_id})")
            else:
                # Create new author
                execute_query("""
                    INSERT INTO authors (name) VALUES (?)
                """, (author_name,), commit=True)
                
                # Get the new author ID
                author_id = execute_query("""
                    SELECT last_insert_rowid() as id
                """)[0]['id']
                LOGGER.info(f"Created new author: {author_name} (ID: {author_id})")
            
            # Check if relationship already exists
            existing_relationship = execute_query("""
                SELECT * FROM book_authors WHERE book_id = ? AND author_id = ?
            """, (book['id'], author_id))
            
            if not existing_relationship:
                # Create book-author relationship
                execute_query("""
                    INSERT INTO book_authors (book_id, author_id, is_primary)
                    VALUES (?, ?, 1)
                """, (book['id'], author_id), commit=True)
                LOGGER.info(f"Created book-author relationship for book {book['id']} and author {author_id}")
            else:
                LOGGER.info(f"Book-author relationship already exists for book {book['id']} and author {author_id}")
        
        LOGGER.info("Migration completed successfully")
        return True
    except Exception as e:
        LOGGER.error(f"Error during migration: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    # This allows running the migration directly for testing
    migrate()
