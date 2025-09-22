#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import wraps
from flask import redirect, url_for, request, flash, jsonify

from backend.base.logging import LOGGER
from backend.internals.settings import Settings
from backend.internals.db import execute_query


def root_folders_required(f):
    """Decorator to check if root folders are configured.
    
    If no root folders are configured, redirect to the root folders page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get settings
        settings = Settings().get_settings()
        root_folders = settings.root_folders
        
        # Check if root folders are configured
        if not root_folders:
            # If this is an API request, return a JSON response
            if request.path.startswith('/api/'):
                return jsonify({
                    "error": "No root folders configured",
                    "message": "Please configure at least one root folder before using this feature",
                    "redirect": url_for('ui.setup_wizard')
                }), 400
            
            # For UI requests, redirect to the setup wizard
            flash('Please configure at least one root folder before using this feature', 'warning')
            return redirect(url_for('ui.setup_wizard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def collections_required(f):
    """Decorator to check if collections are configured.
    
    If no collections are configured, redirect to the setup wizard.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if collections table exists and has at least one collection
        try:
            collections = execute_query("SELECT COUNT(*) as count FROM collections")
            if not collections or collections[0]['count'] == 0:
                # If this is an API request, return a JSON response
                if request.path.startswith('/api/'):
                    return jsonify({
                        "error": "No collections configured",
                        "message": "Please set up at least one collection before using this feature",
                        "redirect": url_for('ui.setup_wizard')
                    }), 400
                
                # For UI requests, redirect to the setup wizard
                flash('Please set up at least one collection before using this feature', 'warning')
                return redirect(url_for('ui.setup_wizard'))
        except Exception as e:
            LOGGER.error(f"Error checking collections: {e}")
            # If there's an error (e.g., table doesn't exist), redirect to setup
            if request.path.startswith('/api/'):
                return jsonify({
                    "error": "Database not properly set up",
                    "message": "Please complete the initial setup before using this feature",
                    "redirect": url_for('ui.setup_wizard')
                }), 400
            
            flash('Please complete the initial setup before using this feature', 'warning')
            return redirect(url_for('ui.setup_wizard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def setup_required(f):
    """Decorator to check if both collections and root folders are configured.
    
    This combines both collections_required and root_folders_required checks.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check collections
        collections_check = collections_required(lambda *a, **kw: None)(*args, **kwargs)
        if collections_check is not None:
            return collections_check
        
        # Then check root folders
        root_folders_check = root_folders_required(lambda *a, **kw: None)(*args, **kwargs)
        if root_folders_check is not None:
            return root_folders_check
        
        # If both checks pass, proceed with the original function
        return f(*args, **kwargs)
    
    return decorated_function
