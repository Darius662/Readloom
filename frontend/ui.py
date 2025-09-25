#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from flask import (Blueprint, Response, jsonify, redirect, render_template,
                  request, send_from_directory, url_for, flash)

from backend.base.logging import LOGGER
from backend.features.calendar import get_calendar_events
from backend.internals.db import execute_query
from backend.internals.settings import Settings
from frontend.middleware import root_folders_required, collections_required, setup_required

# Create UI blueprint
ui_bp = Blueprint(
    'ui', 
    __name__, 
    url_prefix='',
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)


@ui_bp.route('/')
def index():
    """Render the dashboard page.

    Returns:
        Response: The rendered dashboard page.
    """
    # Check if setup is complete
    try:
        # Check if collections table exists and has at least one collection
        collections = execute_query("SELECT COUNT(*) as count FROM collections")
        if not collections or collections[0]['count'] == 0:
            return redirect(url_for('ui.setup_wizard'))
            
        # Check if root folders are configured
        settings = Settings().get_settings()
        root_folders = settings.root_folders
        if not root_folders:
            return redirect(url_for('ui.setup_wizard'))
    except Exception as e:
        LOGGER.error(f"Error checking setup status: {e}")
        return redirect(url_for('ui.setup_wizard'))
    
    return render_template('dashboard.html', root_folders=root_folders)


@ui_bp.route('/calendar')
@setup_required
def calendar():
    """Render the calendar page.

    Returns:
        Response: The rendered calendar page.
    """
    return render_template('calendar.html')


@ui_bp.route('/series')
@setup_required
def series_list():
    """Render the series list page.

    Returns:
        Response: The rendered series list page.
    """
    # Get root folders for the template
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    return render_template('series_list.html', root_folders=root_folders)


@ui_bp.route('/collection')
@setup_required
def collection():
    """Render the collection page.

    Returns:
        Response: The rendered collection page.
    """
    return render_template('collection.html')


@ui_bp.route('/collections')
@setup_required
def collections_manager():
    """Render the collections manager page.

    Returns:
        Response: The rendered collections manager page.
    """
    return render_template('collections_manager.html')


@ui_bp.route('/series/<int:series_id>')
@setup_required
def series_detail(series_id: int):
    """Render the series detail page.

    Args:
        series_id (int): The series ID.

    Returns:
        Response: The rendered series detail page.
    """
    # Get root folders for the template
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    return render_template('series_detail.html', series_id=series_id, root_folders=root_folders)


@ui_bp.route('/settings')
def settings():
    """Render the settings page.

    Returns:
        Response: The rendered settings page.
    """
    return render_template('settings.html')


@ui_bp.route('/root-folders')
@collections_required
def root_folders():
    """Render the root folders page.
    
    Note: This route is still needed even though the tab is hidden in the UI.
    The functionality has been integrated into the Collections Manager page,
    but this route is kept for backward compatibility and direct access.

    Returns:
        Response: The rendered root folders page.
    """
    return render_template('root_folders.html')


@ui_bp.route('/setup-wizard')
def setup_wizard():
    """Render the setup wizard page.

    Returns:
        Response: The rendered setup wizard page.
    """
    return render_template('setup_wizard.html')


@ui_bp.route('/collections')
def collections():
    """Render the collections management page.

    Returns:
        Response: The rendered collections page.
    """
    return render_template('collections.html')


@ui_bp.route('/integrations')
def integrations():
    """Render the integrations page.

    Returns:
        Response: The rendered integrations page.
    """
    return render_template('integrations.html')


@ui_bp.route('/integrations/home-assistant')
def home_assistant():
    """Render the Home Assistant integration page.

    Returns:
        Response: The rendered Home Assistant integration page.
    """
    return render_template('home_assistant.html')


@ui_bp.route('/integrations/homarr')
def homarr():
    """Render the Homarr integration page.

    Returns:
        Response: The rendered Homarr integration page.
    """
    return render_template('homarr.html')


@ui_bp.route('/integrations/providers')
def provider_config():
    """Render the metadata provider configuration page.

    Returns:
        Response: The rendered provider configuration page.
    """
    return render_template('provider_config.html')


@ui_bp.route('/notifications')
def notifications():
    """Render the notifications page.

    Returns:
        Response: The rendered notifications page.
    """
    return render_template('notifications.html')


@ui_bp.route('/search')
@setup_required
def search():
    """Render the search page for external manga sources.

    Returns:
        Response: The rendered search page.
    """
    # Get root folders for the template
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    return render_template('search.html', root_folders=root_folders)


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
        'app_name': 'Readloom',
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
