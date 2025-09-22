#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Optional, Union

from flask import Flask
from waitress import serve

from backend.base.definitions import Constants, StartType
from backend.base.logging import LOGGER


class Server:
    """Server class for MangaArr."""
    
    def __init__(self):
        """Initialize the server."""
        self.app: Optional[Flask] = None
        self.start_type: Optional[StartType] = None
        self.url_base: str = Constants.DEFAULT_URL_BASE
    
    def create_app(self) -> Flask:
        """Create the Flask application.

        Returns:
            Flask: The Flask application.
        """
        if self.app is not None:
            return self.app
        
        self.app = Flask(__name__)
        
        # Configure the application
        self.app.config["SECRET_KEY"] = os.urandom(24)
        self.app.config["JSON_SORT_KEYS"] = False
        
        # Register blueprints
        from frontend.api import api_bp
        from frontend.api_metadata_fixed import metadata_api_bp
        from frontend.api_ebooks import ebooks_api_bp
        from frontend.ui import ui_bp
        from frontend.image_proxy import image_proxy_bp
        
        self.app.register_blueprint(api_bp)
        self.app.register_blueprint(metadata_api_bp, url_prefix='/api/metadata')
        self.app.register_blueprint(ebooks_api_bp)
        self.app.register_blueprint(ui_bp)
        self.app.register_blueprint(image_proxy_bp)
        
        return self.app
    
    def set_url_base(self, url_base: str) -> None:
        """Set the URL base for the server.

        Args:
            url_base (str): The URL base.
        """
        self.url_base = url_base
    
    def run(self, host: str, port: int) -> None:
        """Run the server.

        Args:
            host (str): The host to bind to.
            port (int): The port to bind to.
        """
        if self.app is None:
            self.create_app()
        
        LOGGER.info(f"Starting server on {host}:{port} with URL base '{self.url_base}'")
        
        try:
            serve(
                self.app,
                host=host,
                port=port,
                url_scheme="http",
                threads=8
            )
        except Exception as e:
            LOGGER.error(f"Server error: {e}")
            raise


# Create a global server instance
SERVER = Server()


def handle_start_type(start_type: StartType) -> None:
    """Handle the start type.

    Args:
        start_type (StartType): The start type.
    """
    SERVER.start_type = None
    
    if start_type == StartType.STARTUP:
        LOGGER.info("Starting up MangaArr")
    elif start_type == StartType.RESTART:
        LOGGER.info("Restarting MangaArr")
    elif start_type == StartType.UPDATE:
        LOGGER.info("Updating MangaArr")
