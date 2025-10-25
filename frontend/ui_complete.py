#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Complete UI routes for Readloom.
Includes all routes from the original UI blueprint and the content-specific routes.
"""

from flask import Blueprint, render_template, redirect, url_for, request, abort

from backend.base.logging import LOGGER
from backend.features.content_service_factory import ContentType, get_content_service
from backend.internals.db import execute_query
from frontend.middleware import setup_required, collections_required


# Create Blueprint for UI routes
ui_bp = Blueprint('ui', __name__)


# Helper functions
def get_user_preference():
    """Get the user's content type preference."""
    # This could be stored in a cookie or user settings
    # For now, default to books
    return request.cookies.get('content_preference', 'book')


def get_book_collections():
    """Get book collections."""
    try:
        collections = execute_query("""
            SELECT c.*, COUNT(sc.series_id) as book_count
            FROM collections c
            LEFT JOIN series_collections sc ON c.id = sc.collection_id
            LEFT JOIN series s ON sc.series_id = s.id AND UPPER(s.content_type) IN ('BOOK', 'NOVEL')
            WHERE UPPER(c.content_type) IN ('BOOK', 'NOVEL')
            GROUP BY c.id
            ORDER BY c.name
        """)
        return collections
    except Exception as e:
        LOGGER.error(f"Error getting book collections: {e}")
        return []


def get_manga_collections():
    """Get manga collections."""
    try:
        collections = execute_query("""
            SELECT c.*, COUNT(sc.series_id) as manga_count
            FROM collections c
            LEFT JOIN series_collections sc ON c.id = sc.collection_id
            LEFT JOIN series s ON sc.series_id = s.id AND UPPER(s.content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')
            WHERE UPPER(c.content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')
            GROUP BY c.id
            ORDER BY c.name
        """)
        return collections
    except Exception as e:
        LOGGER.error(f"Error getting manga collections: {e}")
        return []


def get_popular_authors(limit=10):
    """Get popular authors."""
    try:
        authors = execute_query("""
            SELECT a.*, COUNT(ab.series_id) as book_count
            FROM authors a
            LEFT JOIN author_books ab ON a.id = ab.author_id
            GROUP BY a.id
            ORDER BY book_count DESC, a.name
            LIMIT ?
        """, (limit,))
        return authors
    except Exception as e:
        LOGGER.error(f"Error getting popular authors: {e}")
        return []


def get_recent_books(limit=10):
    """Get recent books."""
    try:
        # Use content_type to filter books
        books = execute_query("""
            SELECT s.*
            FROM series s
            WHERE UPPER(s.content_type) IN ('BOOK', 'NOVEL')
            ORDER BY s.created_at DESC
            LIMIT ?
        """, (limit,))
        return books
    except Exception as e:
        LOGGER.error(f"Error getting recent books: {e}")
        return []


def get_recent_series(limit=10):
    """Get recent manga series."""
    try:
        # Use content_type to filter manga
        series = execute_query("""
            SELECT s.*
            FROM series s
            WHERE UPPER(s.content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')
            ORDER BY s.created_at DESC
            LIMIT ?
        """, (limit,))
        return series
    except Exception as e:
        LOGGER.error(f"Error getting recent series: {e}")
        return []


# Setup wizard route
@ui_bp.route('/setup')
@ui_bp.route('/setup-wizard')
def setup_wizard():
    """Setup wizard page."""
    # Check if setup is already complete
    from backend.features.setup_check import is_setup_complete
    if is_setup_complete():
        return redirect(url_for('ui.home'))
    
    # Get root folders for the setup wizard
    from backend.internals.settings import Settings
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    return render_template('setup_wizard.html', root_folders=root_folders)


# Settings route
@ui_bp.route('/settings')
def settings():
    """Settings page."""
    return render_template('settings.html')


# Root folders route
@ui_bp.route('/root-folders')
@setup_required
def root_folders():
    """Root folders page."""
    return render_template('root_folders.html')


# Collections route
@ui_bp.route('/collections')
@setup_required
def collections_manager():
    """Collections management page."""
    return render_template('collections_manager.html')


# Collection route
@ui_bp.route('/collection')
@setup_required
def collection():
    """Collection page."""
    return render_template('collection.html')


# Collection view route
@ui_bp.route('/collection/<int:collection_id>')
@setup_required
def collection_view(collection_id):
    """Collection detail page."""
    return render_template('collection_view.html', collection_id=collection_id)


# About route
@ui_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')


# Calendar route
@ui_bp.route('/calendar')
@setup_required
def calendar():
    """Calendar page."""
    return render_template('calendar.html')


# Series list route
@ui_bp.route('/series')
@setup_required
def series_list():
    """Series list page."""
    # Get root folders from settings
    from backend.internals.settings import Settings
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    return render_template('series_list.html', root_folders=root_folders)


# Series detail route (for backward compatibility)
@ui_bp.route('/series/<int:series_id>')
@setup_required
def series_detail(series_id: int):
    """Series detail page.
    
    This route is for backward compatibility. It will redirect to the appropriate
    book or manga detail page based on the series type.
    """
    # Check if the series is a book or manga
    from backend.internals.db import execute_query
    series = execute_query("SELECT content_type FROM series WHERE id = ?", (series_id,))
    
    if not series:
        abort(404)
    
    content_type = series[0]['content_type']
    
    if content_type == 'BOOK':
        return redirect(url_for('ui.book_view', book_id=series_id))
    else:
        return redirect(url_for('ui.series_view', series_id=series_id))


# Search route (for backward compatibility)
@ui_bp.route('/search')
@setup_required
def search():
    """Search page.
    
    This route is for backward compatibility. It will redirect to the books search page.
    """
    return redirect(url_for('ui.books_search'))


# Notifications route
@ui_bp.route('/notifications')
@setup_required
def notifications():
    """Notifications page."""
    return render_template('notifications.html')


# Integrations routes
@ui_bp.route('/integrations')
def integrations():
    """Integrations page."""
    return render_template('integrations.html')


@ui_bp.route('/integrations/home-assistant')
def home_assistant():
    """Home Assistant integration page."""
    return render_template('home_assistant.html')


@ui_bp.route('/integrations/homarr')
def homarr():
    """Homarr integration page."""
    return render_template('homarr.html')


@ui_bp.route('/integrations/providers')
def provider_config():
    """Provider configuration page."""
    return render_template('provider_config.html')


# Favicon route
@ui_bp.route('/favicon.ico')
def favicon():
    """Serve the favicon."""
    from flask import send_from_directory
    return send_from_directory('static/img', 'favicon.ico')


# Authors routes
@ui_bp.route('/authors')
def authors_home():
    """Authors home page."""
    return render_template('authors/authors.html')


@ui_bp.route('/authors/<int:author_id>')
def author_detail(author_id):
    """Author detail page."""
    # Get author details
    author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
    
    if not author:
        abort(404)
    
    # Get author's books
    books = execute_query("""
        SELECT s.* 
        FROM series s
        JOIN author_books ab ON s.id = ab.series_id
        WHERE ab.author_id = ?
        ORDER BY s.title ASC
    """, (author_id,))
    
    return render_template(
        'authors/author_detail.html',
        author=author[0],
        books=books
    )


@ui_bp.route('/authors/<int:author_id>/books')
def author_books(author_id):
    """Author's books page."""
    # Get author details
    author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
    
    if not author:
        abort(404)
    
    # Get author's books
    books = execute_query("""
        SELECT s.* 
        FROM series s
        JOIN author_books ab ON s.id = ab.series_id
        WHERE ab.author_id = ?
        ORDER BY s.title ASC
    """, (author_id,))
    
    return render_template(
        'authors/author_books.html',
        author=author[0],
        books=books
    )


# Books routes
@ui_bp.route('/books')
@setup_required
def books_home():
    """Books home page."""
    # Get book collections
    book_collections = get_book_collections()
    
    # Get popular authors
    popular_authors = get_popular_authors(5)
    
    # Get recent books
    recent_books = get_recent_books(6)
    
    return render_template(
        'books/home.html',
        book_collections=book_collections,
        popular_authors=popular_authors,
        recent_books=recent_books
    )


@ui_bp.route('/books/search')
@setup_required
def books_search():
    """Book search page."""
    return render_template('books/search.html')


@ui_bp.route('/books/authors')
def authors_view():
    """Authors list page."""
    # Get all authors
    authors = execute_query("""
        SELECT a.*, COUNT(ba.book_id) as book_count
        FROM authors a
        LEFT JOIN book_authors ba ON a.id = ba.author_id
        GROUP BY a.id
        ORDER BY a.name
    """)
    
    return render_template('books/authors.html', authors=authors)


@ui_bp.route('/books/authors/<int:author_id>')
def author_view(author_id):
    """Author detail page."""
    # Get author details
    book_service = get_content_service(ContentType.BOOK)
    author = book_service.get_author_details(author_id)
    
    if "error" in author:
        abort(404)
    
    # Get books by author
    books = book_service.get_books_by_author(author_id)
    
    return render_template('books/author.html', author=author, books=books)


@ui_bp.route('/books/<int:book_id>')
@setup_required
def book_view(book_id):
    """Book detail page."""
    # Get book details
    book = execute_query("SELECT * FROM series WHERE id = ? AND content_type = 'BOOK'", (book_id,))
    
    if not book:
        abort(404)
    
    book = book[0]
    
    # Get author
    author = execute_query("""
        SELECT a.* FROM authors a
        JOIN author_books ab ON a.id = ab.author_id
        WHERE ab.series_id = ?
    """, (book_id,))
    
    author = author[0] if author else None
    
    # Get collection
    collection = execute_query("""
        SELECT c.* FROM collections c
        JOIN series_collections sc ON c.id = sc.collection_id
        WHERE sc.series_id = ?
    """, (book_id,))
    
    collection = collection[0] if collection else None
    
    # Get e-book files
    from backend.features.ebook_files import get_ebook_files_for_series
    ebook_files = get_ebook_files_for_series(book_id)
    
    # Get all book collections for the edit form
    book_collections = get_book_collections()
    
    return render_template(
        'books/book.html',
        book=book,
        author=author,
        collection=collection,
        ebook_files=ebook_files,
        book_collections=book_collections
    )


# Manga routes
@ui_bp.route('/manga')
@setup_required
def manga_home():
    """Manga home page."""
    # Get manga collections
    manga_collections = get_manga_collections()
    
    # Get recent series
    recent_series = get_recent_series(10)
    
    return render_template(
        'manga/home.html',
        manga_collections=manga_collections,
        recent_series=recent_series
    )


@ui_bp.route('/manga/search')
@setup_required
def manga_search():
    """Manga search page."""
    return render_template('manga/search.html')


@ui_bp.route('/manga/series/<int:series_id>')
@setup_required
def series_view(series_id):
    """Series detail page."""
    # Get series details
    series = execute_query("SELECT * FROM series WHERE id = ? AND content_type IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')", (series_id,))
    
    if not series:
        abort(404)
    
    series = series[0]
    
    # Get volumes
    volumes = execute_query("""
        SELECT v.*, COUNT(c.id) as chapter_count
        FROM volumes v
        LEFT JOIN chapters c ON v.id = c.volume_id
        WHERE v.series_id = ?
        GROUP BY v.id
        ORDER BY CAST(v.volume_number AS INTEGER)
    """, (series_id,))
    
    # Get collection
    collection = execute_query("""
        SELECT c.* FROM collections c
        JOIN series_collections sc ON c.id = sc.collection_id
        WHERE sc.series_id = ?
    """, (series_id,))
    
    collection = collection[0] if collection else None
    
    # Get e-book files
    from backend.features.ebook_files import get_ebook_files_for_series
    ebook_files = get_ebook_files_for_series(series_id)
    
    return render_template(
        'manga/series.html',
        series=series,
        volumes=volumes,
        collection=collection,
        ebook_files=ebook_files
    )


# Home route - renders the dashboard
@ui_bp.route('/')
@setup_required
def home():
    """Dashboard page."""
    # Get root folders from settings
    from backend.internals.settings import Settings
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    # Get book collections
    book_collections = get_book_collections()
    
    # Get manga collections
    manga_collections = get_manga_collections()
    
    # Get popular authors
    popular_authors = get_popular_authors(5)
    
    # Get recent books
    recent_books = get_recent_books(6)
    
    # Get recent manga series
    recent_series = get_recent_series(6)
    
    return render_template(
        'dashboard.html',
        root_folders=root_folders,
        book_collections=book_collections,
        manga_collections=manga_collections,
        popular_authors=popular_authors,
        recent_books=recent_books,
        recent_series=recent_series,
        title="Dashboard"
    )


# Legacy index route for backward compatibility
@ui_bp.route('/index')
@setup_required
def index():
    """Dashboard page (legacy)."""
    return redirect(url_for('ui.home'))
