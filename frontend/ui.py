#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from flask import (Blueprint, Response, jsonify, redirect, render_template,
                  request, send_from_directory, url_for)

from backend.base.logging import LOGGER
from backend.features.calendar import get_calendar_events
from backend.internals.db import execute_query
from backend.internals.settings import Settings

# Create UI blueprint
ui_bp = Blueprint(
    'ui', 
    __name__, 
    url_prefix='',
    template_folder='templates',
    static_folder='static'
)


@ui_bp.route('/')
def index():
    """Render the index page.

    Returns:
        Response: The rendered index page.
    """
    return render_template('index.html')


@ui_bp.route('/calendar')
def calendar():
    """Render the calendar page.

    Returns:
        Response: The rendered calendar page.
    """
    return render_template('calendar.html')


@ui_bp.route('/series')
def series_list():
    """Render the series list page.

    Returns:
        Response: The rendered series list page.
    """
    return render_template('series_list.html')


@ui_bp.route('/series/<int:series_id>')
def series_detail(series_id: int):
    """Render the series detail page.

    Args:
        series_id (int): The series ID.

    Returns:
        Response: The rendered series detail page.
    """
    return render_template('series_detail.html', series_id=series_id)


@ui_bp.route('/settings')
def settings():
    """Render the settings page.

    Returns:
        Response: The rendered settings page.
    """
    return render_template('settings.html')


@ui_bp.route('/integrations')
def integrations():
    """Render the integrations page.

    Returns:
        Response: The rendered integrations page.
    """
    return render_template('integrations.html')


@ui_bp.route('/about')
def about():
    """Render the about page.

    Returns:
        Response: The rendered about page.
    """
    return render_template('about.html')


@ui_bp.route('/favicon.ico')
def favicon():
    """Serve the favicon.

    Returns:
        Response: The favicon.
    """
    return send_from_directory(
        os.path.join(ui_bp.static_folder, 'img'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


@ui_bp.context_processor
def inject_globals():
    """Inject global variables into templates.

    Returns:
        Dict: The global variables.
    """
    settings = Settings().get_settings()
    
    return {
        'app_name': 'MangaArr',
        'app_version': '1.0.0',
        'current_year': datetime.now().year,
        'url_base': settings.url_base
    }


@ui_bp.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors.

    Args:
        e: The error.

    Returns:
        Response: The rendered 404 page.
    """
    return render_template('errors/404.html'), 404


@ui_bp.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors.

    Args:
        e: The error.

    Returns:
        Response: The rendered 500 page.
    """
    return render_template('errors/500.html'), 500
