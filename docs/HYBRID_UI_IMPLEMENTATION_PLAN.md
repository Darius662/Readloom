# Readloom Hybrid UI Implementation Plan

This document outlines the plan for implementing a hybrid UI approach that maintains a unified user interface while separating the backend handling for different content types (books and manga).

## Table of Contents

1. [Overview](#overview)
2. [Architecture Changes](#architecture-changes)
3. [Backend Implementation](#backend-implementation)
4. [Frontend Implementation](#frontend-implementation)
5. [Database Changes](#database-changes)
6. [Migration Strategy](#migration-strategy)
7. [Implementation Phases](#implementation-phases)
8. [Testing Strategy](#testing-strategy)

## Overview

The hybrid approach aims to:

- Maintain a unified UI experience
- Provide specialized handling for books vs. manga in the backend
- Organize books by author rather than series
- Create a different folder structure for books vs. manga
- Allow users to easily switch between content types

## Architecture Changes

### Current Architecture

```
Frontend (unified) → API Layer → Service Layer → Database
                                              → File System
```

### New Architecture

```
Frontend (unified with content-specific views)
       ↓
API Layer (with content type routing)
       ↓
┌─────────────────┬─────────────────┐
│ Book Services   │ Manga Services  │
└─────────────────┴─────────────────┘
       ↓                   ↓
┌─────────────────┬─────────────────┐
│ Book Storage    │ Manga Storage   │
│ (Author-based)  │ (Series-based)  │
└─────────────────┴─────────────────┘
```

## Backend Implementation

### 1. Content Service Factory

Create a factory pattern to route requests to the appropriate service:

```python
# backend/features/content_service_factory.py

from enum import Enum
from typing import Union

class ContentType(Enum):
    BOOK = "BOOK"
    NOVEL = "NOVEL"
    MANGA = "MANGA"
    MANHWA = "MANHWA"
    MANHUA = "MANHUA"
    COMIC = "COMIC"

def get_content_service(content_type: Union[str, ContentType]):
    """Get the appropriate content service based on content type."""
    if isinstance(content_type, str):
        content_type = content_type.upper()
    
    if content_type in [ContentType.BOOK, ContentType.NOVEL, "BOOK", "NOVEL"]:
        from backend.features.book_service import BookService
        return BookService()
    else:
        from backend.features.manga_service import MangaService
        return MangaService()
```

### 2. Service Interfaces

Create base interfaces for content services:

```python
# backend/features/content_service_base.py

from abc import ABC, abstractmethod

class ContentServiceBase(ABC):
    """Base interface for content services."""
    
    @abstractmethod
    def search(self, query, search_type="title"):
        """Search for content."""
        pass
    
    @abstractmethod
    def get_details(self, content_id):
        """Get content details."""
        pass
    
    @abstractmethod
    def import_to_collection(self, content_id, provider):
        """Import content to collection."""
        pass
    
    @abstractmethod
    def create_folder_structure(self, content_id, title, author=None):
        """Create appropriate folder structure."""
        pass
```

### 3. Book-Specific Service

Implement book-specific handling:

```python
# backend/features/book_service.py

from backend.features.content_service_base import ContentServiceBase

class BookService(ContentServiceBase):
    """Service for handling book-specific operations."""
    
    def search(self, query, search_type="title"):
        # Implement book-specific search
        pass
    
    def get_details(self, book_id):
        # Implement book-specific details retrieval
        pass
    
    def import_to_collection(self, book_id, provider):
        # Implement book-specific import logic
        # - Create author-based folder structure
        # - Group books by author
        pass
    
    def create_folder_structure(self, book_id, title, author):
        """Create author/book folder structure."""
        # Create author folder if it doesn't exist
        # Create book folder inside author folder
        pass
```

### 4. Manga-Specific Service

Maintain existing manga handling:

```python
# backend/features/manga_service.py

from backend.features.content_service_base import ContentServiceBase

class MangaService(ContentServiceBase):
    """Service for handling manga-specific operations."""
    
    def search(self, query, search_type="title"):
        # Use existing manga search logic
        pass
    
    def get_details(self, manga_id):
        # Use existing manga details logic
        pass
    
    def import_to_collection(self, manga_id, provider):
        # Use existing manga import logic
        pass
    
    def create_folder_structure(self, manga_id, title, author=None):
        """Create series-based folder structure."""
        # Use existing folder creation logic
        pass
```

### 5. Folder Structure Helper

Update the folder creation helper:

```python
# backend/base/helpers.py

def create_content_folder_structure(content_id, title, content_type, author=None):
    """Create the appropriate folder structure based on content type."""
    from backend.features.content_service_factory import get_content_service
    
    service = get_content_service(content_type)
    return service.create_folder_structure(content_id, title, author)
```

## Frontend Implementation

### 1. Base Template Updates

Update the base template to include content type navigation:

```html
<!-- frontend/templates/base.html -->

<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <!-- Existing navigation -->
    
    <!-- Content Type Selector -->
    <div class="content-type-selector ms-auto me-3">
        <a href="{{ url_for('ui.books_home') }}" 
           class="btn btn-sm {{ 'btn-light' if content_type == 'book' else 'btn-outline-light' }}">
            <i class="fas fa-book me-1"></i> Books
        </a>
        <a href="{{ url_for('ui.manga_home') }}" 
           class="btn btn-sm {{ 'btn-light' if content_type == 'manga' else 'btn-outline-light' }}">
            <i class="fas fa-book-open me-1"></i> Manga
        </a>
    </div>
    
    <!-- User menu -->
</nav>
```

### 2. Content-Specific Layouts

Create content-specific layout templates:

```html
<!-- frontend/templates/books_layout.html -->

{% extends "base.html" %}
{% set content_type = 'book' %}

{% block content %}
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-3">
                <!-- Book-specific sidebar -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h5 class="card-title">Book Collections</h5>
                    </div>
                    <div class="list-group list-group-flush">
                        {% for collection in book_collections %}
                            <a href="{{ url_for('ui.collection_view', collection_id=collection.id) }}" 
                               class="list-group-item list-group-item-action">
                                {{ collection.name }}
                            </a>
                        {% endfor %}
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title">Authors</h5>
                    </div>
                    <div class="list-group list-group-flush">
                        {% for author in authors %}
                            <a href="{{ url_for('ui.author_view', author_id=author.id) }}" 
                               class="list-group-item list-group-item-action">
                                {{ author.name }}
                            </a>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <div class="col-md-9">
                {% block book_content %}{% endblock %}
            </div>
        </div>
    </div>
{% endblock %}
```

```html
<!-- frontend/templates/manga_layout.html -->

{% extends "base.html" %}
{% set content_type = 'manga' %}

{% block content %}
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-3">
                <!-- Manga-specific sidebar -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h5 class="card-title">Manga Collections</h5>
                    </div>
                    <div class="list-group list-group-flush">
                        {% for collection in manga_collections %}
                            <a href="{{ url_for('ui.collection_view', collection_id=collection.id) }}" 
                               class="list-group-item list-group-item-action">
                                {{ collection.name }}
                            </a>
                        {% endfor %}
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title">Series</h5>
                    </div>
                    <div class="list-group list-group-flush">
                        {% for series in series_list %}
                            <a href="{{ url_for('ui.series_view', series_id=series.id) }}" 
                               class="list-group-item list-group-item-action">
                                {{ series.title }}
                            </a>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <div class="col-md-9">
                {% block manga_content %}{% endblock %}
            </div>
        </div>
    </div>
{% endblock %}
```

### 3. Content-Specific Views

Create content-specific view templates:

```html
<!-- frontend/templates/books/search.html -->

{% extends "books_layout.html" %}

{% block book_content %}
    <div class="card">
        <div class="card-header">
            <h5 class="card-title">Search Books</h5>
        </div>
        <div class="card-body">
            <!-- Book search form -->
            <form id="bookSearchForm" class="mb-4">
                <div class="row g-3 align-items-center">
                    <div class="col-md-6">
                        <input type="text" class="form-control" id="searchQuery" 
                               placeholder="Enter book title or author..." required>
                    </div>
                    <div class="col-md-3">
                        <select class="form-select" id="searchType">
                            <option value="title">Title</option>
                            <option value="author">Author</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="fas fa-search me-2"></i> Search
                        </button>
                    </div>
                </div>
            </form>
            
            <!-- Search results -->
            <div id="searchResults" class="row row-cols-1 row-cols-md-3 g-4">
                <!-- Results will be populated here -->
            </div>
        </div>
    </div>
{% endblock %}
```

```html
<!-- frontend/templates/manga/search.html -->

{% extends "manga_layout.html" %}

{% block manga_content %}
    <div class="card">
        <div class="card-header">
            <h5 class="card-title">Search Manga</h5>
        </div>
        <div class="card-body">
            <!-- Manga search form -->
            <form id="mangaSearchForm" class="mb-4">
                <div class="row g-3 align-items-center">
                    <div class="col-md-6">
                        <input type="text" class="form-control" id="searchQuery" 
                               placeholder="Enter manga title..." required>
                    </div>
                    <div class="col-md-3">
                        <select class="form-select" id="searchProvider">
                            <option value="">All Providers</option>
                            <!-- Providers will be populated dynamically -->
                        </select>
                    </div>
                    <div class="col-md-3">
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="fas fa-search me-2"></i> Search
                        </button>
                    </div>
                </div>
            </form>
            
            <!-- Search results -->
            <div id="searchResults" class="row row-cols-1 row-cols-md-3 g-4">
                <!-- Results will be populated here -->
            </div>
        </div>
    </div>
{% endblock %}
```

### 4. Route Updates

Update the UI routes to handle content type:

```python
# frontend/ui.py

from flask import Blueprint, render_template, redirect, url_for

ui_bp = Blueprint('ui', __name__)

# Home route - redirects to books or manga based on user preference
@ui_bp.route('/')
def home():
    # Check user preference or default to books
    # This could be stored in a cookie or user settings
    user_preference = get_user_preference()
    if user_preference == 'manga':
        return redirect(url_for('ui.manga_home'))
    else:
        return redirect(url_for('ui.books_home'))

# Books routes
@ui_bp.route('/books')
def books_home():
    # Get book collections
    book_collections = get_book_collections()
    # Get popular authors
    authors = get_popular_authors()
    return render_template('books/home.html', book_collections=book_collections, authors=authors)

@ui_bp.route('/books/search')
def books_search():
    return render_template('books/search.html')

@ui_bp.route('/books/authors/<int:author_id>')
def author_view(author_id):
    # Get author details
    author = get_author_details(author_id)
    # Get books by author
    books = get_books_by_author(author_id)
    return render_template('books/author.html', author=author, books=books)

@ui_bp.route('/books/<int:book_id>')
def book_view(book_id):
    # Get book details
    book = get_book_details(book_id)
    return render_template('books/book.html', book=book)

# Manga routes
@ui_bp.route('/manga')
def manga_home():
    # Get manga collections
    manga_collections = get_manga_collections()
    # Get popular series
    series_list = get_popular_series()
    return render_template('manga/home.html', manga_collections=manga_collections, series_list=series_list)

@ui_bp.route('/manga/search')
def manga_search():
    return render_template('manga/search.html')

@ui_bp.route('/manga/series/<int:series_id>')
def series_view(series_id):
    # Get series details
    series = get_series_details(series_id)
    return render_template('manga/series.html', series=series)
```

## Database Changes

### 1. Authors Table

Create a dedicated table for authors:

```sql
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    metadata_source TEXT,
    metadata_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Book-Author Relationship

Create a relationship between books and authors:

```sql
CREATE TABLE book_authors (
    book_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    is_primary BOOLEAN DEFAULT 0,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);
```

### 3. Update Series Table

Add a field to distinguish between series and books:

```sql
ALTER TABLE series ADD COLUMN is_book BOOLEAN DEFAULT 0;
```

## Migration Strategy

### 1. Database Migration

Create a migration script to:

1. Create the new tables
2. Extract author information from existing books
3. Populate the authors table
4. Create book-author relationships

```python
# backend/migrations/0007_add_authors_table.py

def migrate():
    """Add authors table and migrate existing book data."""
    from backend.internals.db import execute_query
    
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
    
    # Add is_book column to series table
    execute_query("""
        ALTER TABLE series ADD COLUMN is_book BOOLEAN DEFAULT 0
    """, commit=True)
    
    # Update existing books
    books = execute_query("""
        SELECT id, title, author, content_type FROM series 
        WHERE content_type IN ('BOOK', 'NOVEL')
    """)
    
    for book in books:
        # Mark as book
        execute_query("""
            UPDATE series SET is_book = 1 WHERE id = ?
        """, (book['id'],), commit=True)
        
        # Extract author
        author_name = book['author']
        
        # Check if author exists
        existing_author = execute_query("""
            SELECT id FROM authors WHERE name = ?
        """, (author_name,))
        
        if existing_author:
            author_id = existing_author[0]['id']
        else:
            # Create new author
            execute_query("""
                INSERT INTO authors (name) VALUES (?)
            """, (author_name,), commit=True)
            
            # Get the new author ID
            author_id = execute_query("""
                SELECT last_insert_rowid() as id
            """)[0]['id']
        
        # Create book-author relationship
        execute_query("""
            INSERT INTO book_authors (book_id, author_id, is_primary)
            VALUES (?, ?, 1)
        """, (book['id'], author_id), commit=True)
```

### 2. Folder Structure Migration

Create a script to reorganize the folder structure for books:

```python
# scripts/migrate_book_folders.py

import os
import shutil
from pathlib import Path
from backend.internals.db import execute_query
from backend.base.helpers import get_safe_folder_name

def migrate_book_folders():
    """Migrate book folders to author-based structure."""
    # Get all books with their authors
    books = execute_query("""
        SELECT s.id, s.title, a.id as author_id, a.name as author_name
        FROM series s
        JOIN book_authors ba ON s.id = ba.book_id
        JOIN authors a ON ba.author_id = a.id
        WHERE s.is_book = 1 AND ba.is_primary = 1
    """)
    
    # Get root folders
    from backend.internals.settings import Settings
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    if not root_folders:
        print("No root folders found.")
        return
    
    for book in books:
        book_title = book['title']
        author_name = book['author_name']
        
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
                break
        
        if not current_folder:
            print(f"Could not find folder for book: {book_title}")
            continue
        
        # Create author folder if it doesn't exist
        author_folder = current_folder.parent / safe_author_name
        if not author_folder.exists():
            author_folder.mkdir(exist_ok=True)
            print(f"Created author folder: {author_folder}")
        
        # Move book folder into author folder
        new_book_folder = author_folder / safe_book_title
        if new_book_folder.exists():
            print(f"Destination already exists: {new_book_folder}")
            continue
        
        try:
            shutil.move(str(current_folder), str(new_book_folder))
            print(f"Moved {current_folder} to {new_book_folder}")
        except Exception as e:
            print(f"Error moving folder: {e}")
```

## Implementation Phases

### Phase 1: Backend Preparation

1. Create content type enums and service interfaces
2. Implement the service factory
3. Create database migrations for author support
4. Implement book-specific and manga-specific services

### Phase 2: Frontend Updates

1. Update base template with content type selector
2. Create content-specific layouts
3. Create content-specific view templates
4. Update routes to handle content types

### Phase 3: Data Migration

1. Run database migrations to add author support
2. Migrate existing book data to use authors
3. Reorganize folder structure for books

### Phase 4: UI Refinement

1. Enhance book-specific views to focus on authors
2. Improve manga-specific views to focus on series
3. Add content type preferences for users

## Testing Strategy

### 1. Unit Tests

- Test content service factory
- Test book-specific and manga-specific services
- Test folder structure creation

### 2. Integration Tests

- Test database migrations
- Test folder structure migration
- Test API endpoints with different content types

### 3. UI Tests

- Test content type switching
- Test book search and browsing
- Test manga search and browsing
- Test folder structure access

### 4. Migration Tests

- Test migration of existing data
- Test backward compatibility
- Test performance with large libraries

## Conclusion

This hybrid approach allows Readloom to maintain a unified UI while providing specialized handling for different content types. By organizing books by author and manga by series, the application can better serve the needs of different types of readers while keeping a consistent user experience.

The implementation can be done incrementally, starting with the backend changes and gradually updating the UI to reflect the content type differences. This approach minimizes disruption to existing users while providing a better organization system for books.
