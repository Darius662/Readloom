#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Book-specific service implementation.
Handles books differently from manga, focusing on author-based organization.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from backend.base.logging import LOGGER
from backend.features.content_service_base import ContentServiceBase
from backend.features.content_service_factory import ContentType
from backend.internals.db import execute_query, get_db_connection


class BookService(ContentServiceBase):
    """Service for handling book-specific operations."""
    
    def __init__(self):
        """Initialize the book service."""
        super().__init__()
        self.logger = LOGGER
    
    def search(self, query: str, search_type: str = "title", provider: Optional[str] = None, page: int = 1) -> Dict[str, Any]:
        """Search for books.
        
        Args:
            query: The search query.
            search_type: The type of search (title or author).
            provider: The provider to search with (optional).
            page: The page number.
            
        Returns:
            A dictionary containing search results.
        """
        from backend.features.metadata_service.facade import search_manga
        
        try:
            # Use the existing search function but pass the search_type
            results = search_manga(query, provider, page, search_type)
            
            # Add book-specific processing here if needed
            if "results" in results:
                # Filter results to only include book providers if no specific provider
                if not provider:
                    book_providers = ["GoogleBooks", "OpenLibrary", "ISBNdb", "WorldCat"]
                    results["results"] = {k: v for k, v in results["results"].items() if k in book_providers}
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching for books: {e}")
            return {
                "query": query,
                "search_type": search_type,
                "page": page,
                "results": {},
                "error": str(e)
            }
    
    def get_details(self, content_id: str, provider: str) -> Dict[str, Any]:
        """Get book details.
        
        Args:
            content_id: The book ID.
            provider: The provider name.
            
        Returns:
            A dictionary containing book details.
        """
        from backend.features.metadata_service.facade import get_manga_details
        
        try:
            # Use the existing details function
            details = get_manga_details(content_id, provider)
            
            # Add book-specific processing here if needed
            if "author" in details:
                # Split multiple authors if comma-separated
                authors = [author.strip() for author in details["author"].split(",")]
                details["authors"] = authors
            
            return details
        except Exception as e:
            self.logger.error(f"Error getting book details: {e}")
            return {"error": str(e)}
    
    def import_to_collection(self, content_id: str, provider: str, 
                            collection_id: Optional[int] = None,
                            content_type: Optional[str] = None,
                            root_folder_id: Optional[int] = None) -> Dict[str, Any]:
        """Import a book to the collection.
        
        Args:
            content_id: The book ID.
            provider: The provider name.
            collection_id: The collection ID (optional).
            content_type: The content type (optional).
            root_folder_id: The root folder ID (optional).
            
        Returns:
            A dictionary containing the result.
        """
        from backend.features.metadata_service.facade import import_manga_to_collection
        
        try:
            # Get book details first to extract author
            book_details = self.get_details(content_id, provider)
            
            if "error" in book_details:
                return {"success": False, "message": book_details["error"]}
            
            # Force content type to BOOK if not specified
            if not content_type:
                content_type = "BOOK"
            
            # Use the existing import function
            result = import_manga_to_collection(
                content_id,
                provider,
                collection_id=collection_id,
                content_type=content_type,
                root_folder_id=root_folder_id
            )
            
            # If import was successful, handle author information
            if result.get("success") and "series_id" in result:
                series_id = result["series_id"]
                
                # Mark as book
                execute_query("""
                    UPDATE series SET is_book = 1 WHERE id = ?
                """, (series_id,), commit=True)
                
                # Handle author information
                if "author" in book_details:
                    author_name = book_details["author"]
                    
                    # Check if author exists
                    existing_author = execute_query("""
                        SELECT id FROM authors WHERE name = ?
                    """, (author_name,))
                    
                    if existing_author:
                        author_id = existing_author[0]["id"]
                    else:
                        # Create new author
                        execute_query("""
                            INSERT INTO authors (name, description)
                            VALUES (?, ?)
                        """, (author_name, book_details.get("author_description", "")), commit=True)
                        
                        # Get the new author ID
                        author_id = execute_query("""
                            SELECT last_insert_rowid() as id
                        """)[0]["id"]
                    
                    # Create book-author relationship
                    execute_query("""
                        INSERT INTO author_books (series_id, author_id)
                        VALUES (?, ?)
                    """, (series_id, author_id), commit=True)
                    
                    # Update the folder structure to be author-based
                    self.create_folder_structure(
                        series_id,
                        book_details["title"],
                        content_type,
                        collection_id,
                        root_folder_id,
                        author_name
                    )
            
            return result
        except Exception as e:
            self.logger.error(f"Error importing book to collection: {e}")
            return {"success": False, "message": str(e)}
    
    def create_folder_structure(self, content_id: Union[int, str], title: str, 
                               content_type: str, collection_id: Optional[int] = None,
                               root_folder_id: Optional[int] = None,
                               author: Optional[str] = None) -> str:
        """Create author-based folder structure.
        
        Args:
            content_id: The book ID.
            title: The book title.
            content_type: The content type.
            collection_id: The collection ID (optional).
            root_folder_id: The root folder ID (optional).
            author: The author name (optional).
            
        Returns:
            The path to the created folder.
        """
        from backend.base.helpers import get_safe_folder_name, get_root_folder_path
        
        try:
            # Get author if not provided
            if not author:
                # Try to get author from database
                book_author = execute_query("""
                    SELECT a.name FROM authors a
                    JOIN book_authors ba ON a.id = ba.author_id
                    WHERE ba.book_id = ? AND ba.is_primary = 1
                """, (content_id,))
                
                if book_author:
                    author = book_author[0]["name"]
                else:
                    # Fallback to series author field
                    series_info = execute_query("""
                        SELECT author FROM series WHERE id = ?
                    """, (content_id,))
                    
                    if series_info:
                        author = series_info[0]["author"]
            
            # If still no author, use "Unknown Author"
            if not author:
                author = "Unknown Author"
            
            # Get root folder path
            root_path = get_root_folder_path(content_type, collection_id, root_folder_id)
            
            if not root_path:
                self.logger.error(f"No root folder found for content type {content_type}")
                return ""
            
            # Create safe folder names
            safe_author = get_safe_folder_name(author)
            safe_title = get_safe_folder_name(title)
            
            # Create author folder
            author_path = Path(root_path) / safe_author
            author_path.mkdir(exist_ok=True)
            
            # Create book folder inside author folder
            book_path = author_path / safe_title
            book_path.mkdir(exist_ok=True)
            
            self.logger.info(f"Created book folder structure: {book_path}")
            
            return str(book_path)
        except Exception as e:
            self.logger.error(f"Error creating folder structure: {e}")
            return ""
    
    def get_books_by_author(self, author_id: int) -> List[Dict[str, Any]]:
        """Get books by author.
        
        Args:
            author_id: The author ID.
            
        Returns:
            A list of books by the author.
        """
        try:
            books = execute_query("""
                SELECT s.* FROM series s
                JOIN author_books ab ON s.id = ab.series_id
                WHERE ab.author_id = ? AND UPPER(s.content_type) IN ('BOOK', 'NOVEL')
                ORDER BY s.title
            """, (author_id,))
            
            return books
        except Exception as e:
            self.logger.error(f"Error getting books by author: {e}")
            return []
    
    def get_author_details(self, author_id: int) -> Dict[str, Any]:
        """Get author details.
        
        Args:
            author_id: The author ID.
            
        Returns:
            A dictionary containing author details.
        """
        try:
            author = execute_query("""
                SELECT * FROM authors WHERE id = ?
            """, (author_id,))
            
            if not author:
                return {"error": "Author not found"}
            
            # Get book count
            book_count = execute_query("""
                SELECT COUNT(*) as count FROM author_books WHERE author_id = ?
            """, (author_id,))
            
            author_data = author[0]
            author_data["book_count"] = book_count[0]["count"] if book_count else 0
            
            return author_data
        except Exception as e:
            self.logger.error(f"Error getting author details: {e}")
            return {"error": str(e)}
    
    def get_all_authors(self) -> List[Dict[str, Any]]:
        """Get all authors.
        
        Returns:
            A list of all authors.
        """
        try:
            # First check if the authors table exists and has data
            author_count = execute_query("SELECT COUNT(*) as count FROM authors")
            if not author_count or author_count[0]['count'] == 0:
                # Return empty list if no authors
                return []
            
            # Get the column names from the authors table
            columns_query = execute_query("PRAGMA table_info(authors)")
            column_names = [col['name'] for col in columns_query]
            
            # Build the query dynamically based on available columns
            select_columns = "a.id, a.name"
            for col in column_names:
                if col not in ['id', 'name']:
                    select_columns += f", a.{col}"
            
            # Check if author_books table exists
            try:
                execute_query("SELECT 1 FROM author_books LIMIT 1")
                has_author_books = True
            except Exception:
                has_author_books = False
            
            # Execute the query with the available columns
            if has_author_books:
                authors = execute_query(f"""
                    SELECT {select_columns}, COUNT(ab.series_id) as book_count
                    FROM authors a
                    LEFT JOIN author_books ab ON a.id = ab.author_id
                    GROUP BY a.id
                    ORDER BY a.name
                """)
            else:
                authors = execute_query(f"""
                    SELECT {select_columns}, 0 as book_count
                    FROM authors a
                    ORDER BY a.name
                """)
            
            return authors
        except Exception as e:
            self.logger.error(f"Error getting all authors: {e}")
            return []
