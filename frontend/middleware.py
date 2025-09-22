#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import wraps
from flask import redirect, url_for, request, flash, jsonify

from backend.base.logging import LOGGER
from backend.internals.settings import Settings


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
                    "redirect": url_for('ui.root_folders')
                }), 400
            
            # For UI requests, redirect to the root folders page
            flash('Please configure at least one root folder before using this feature', 'warning')
            return redirect(url_for('ui.root_folders'))
        
        return f(*args, **kwargs)
    
    return decorated_function
