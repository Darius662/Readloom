#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import subprocess
from pathlib import Path
from flask import Flask

def setup_dev_environment():
    """Set up development environment."""
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("data/logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create database directory if it doesn't exist
    db_dir = Path("data/db")
    db_dir.mkdir(exist_ok=True)
    
    # Create empty database file if it doesn't exist
    db_file = db_dir / "readloom.db"
    if not db_file.exists():
        try:
            db_file.touch()
            print(f"Created empty database file at {db_file}")
        except Exception as e:
            print(f"Error creating database file: {e}")
            return False
    
    print("Development environment set up successfully!")
    return True

def generate_test_data():
    """Generate test data for development."""
    try:
        print("Generating test data in data\\db\\readloom.db")
        
        # Import necessary modules
        from backend.internals.db import set_db_location, setup_db
        
        # Set database location
        set_db_location("data/db")
        
        # Create database schema
        print("Creating database schema...")
        setup_db()
        print("Database schema created successfully!")
        
        # Initialize settings
        from backend.internals.settings import Settings
        settings = Settings()
        print("Settings initialized successfully!")
        
        # Generate test data
        # This is where you would add code to generate test data
        print("Test data generation complete!")
        
        print("Test data generated successfully!")
        return True
    except Exception as e:
        print(f"Error generating test data: {e}")
        return False

def run_app():
    """Run the Readloom application directly with Flask."""
    try:
        print("Starting Readloom on 127.0.0.1:7227...")
        
        # Set database location first
        from backend.internals.db import set_db_location, setup_db
        set_db_location("data/db")
        
        # Set up logging
        from backend.base.logging import setup_logging, LOGGER
        setup_logging("data/logs", "readloom.log")
        LOGGER.info("Starting Readloom in development mode")
        
        # Initialize settings
        from backend.internals.settings import Settings
        settings = Settings()
        LOGGER.info("Settings initialized")
        
        # Create Flask app
        app = Flask(__name__, 
                   static_folder='frontend/static', 
                   static_url_path='/static',
                   template_folder='frontend/templates')
        app.config["SECRET_KEY"] = os.urandom(24)
        app.config["JSON_SORT_KEYS"] = False
        
        # Initialize metadata service
        from backend.features.metadata_service import init_metadata_service
        init_metadata_service()
        
        # Start periodic task manager
        from backend.features.periodic_tasks import periodic_task_manager
        periodic_task_manager.start()
        LOGGER.info("Periodic task manager started")
        
        # Register blueprints
        from frontend.api import api_bp
        from frontend.api_metadata_fixed import metadata_api_bp
        from frontend.api_ebooks import ebooks_api_bp
        from frontend.api_rootfolders import rootfolders_api_bp
        from frontend.api_collections import collections_api
        from frontend.api_collection import collection_api
        from frontend.api_folders import folders_api
        from frontend.api_authors import authors_api_bp
        from frontend.api_series import api_series_bp
        from frontend.ui_complete import ui_bp
        from frontend.image_proxy import image_proxy_bp
        
        app.register_blueprint(api_bp)
        app.register_blueprint(metadata_api_bp, url_prefix='/api/metadata')
        app.register_blueprint(ebooks_api_bp)
        app.register_blueprint(rootfolders_api_bp)
        app.register_blueprint(collections_api)
        app.register_blueprint(collection_api)
        app.register_blueprint(folders_api)
        app.register_blueprint(authors_api_bp)
        app.register_blueprint(api_series_bp)
        app.register_blueprint(ui_bp)
        app.register_blueprint(image_proxy_bp)
        
        LOGGER.info("Application initialized successfully")
        print("\nOpen your browser and navigate to http://127.0.0.1:7227/ to view the application")
        
        # Run the app
        app.run(host='0.0.0.0', port=7227, debug=True)
        
        return True
    except Exception as e:
        print(f"Error running Readloom: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Readloom development script")
    parser.add_argument("--no-data", action="store_true", help="Skip test data generation")
    args = parser.parse_args()
    
    # Set up development environment
    if not setup_dev_environment():
        return 1
    
    # Generate test data
    if not args.no_data:
        if not generate_test_data():
            return 1
    
    # Run the application
    if not run_app():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())