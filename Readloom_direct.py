#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from os import environ, name, path, urandom
import os
from typing import NoReturn, Union

from backend.base.definitions import Constants, StartType
from backend.base.helpers import check_min_python_version
from backend.base.logging import LOGGER, setup_logging
from backend.features.tasks import TaskHandler
from backend.internals.db import set_db_location, setup_db
from backend.internals.server import SERVER
from backend.internals.settings import Settings

def _is_running_in_docker() -> bool:
    """Check if the application is running inside a Docker container.
    
    Returns:
        bool: True if running in Docker, False otherwise.
    """
    # Check for .dockerenv file
    if path.exists('/.dockerenv'):
        return True
    
    # Check for cgroup
    try:
        with open('/proc/1/cgroup', 'r') as f:
            if 'docker' in f.read():
                return True
    except (IOError, FileNotFoundError):
        pass
    
    # Check for environment variable that we set in our Dockerfile
    if environ.get('READLOOM_DOCKER') == '1':
        return True
    
    return False

def main(
    db_folder: Union[str, None] = None,
    log_folder: Union[str, None] = None,
    log_file: Union[str, None] = None,
    host: Union[str, None] = None,
    port: Union[int, None] = None,
    url_base: Union[str, None] = None
) -> NoReturn:
    """The main function of Readloom.
    
    Args:
        db_folder: The folder for the database
        log_folder: The folder for logs
        log_file: The log file name
        host: The host to bind to
        port: The port to bind to
        url_base: The URL base
    """
    print(f"Starting Readloom on {host or '0.0.0.0'}:{port or 7227}...")
    
    setup_logging(log_folder, log_file)
    LOGGER.info('Starting up Readloom')
    
    if not check_min_python_version(*Constants.MIN_PYTHON_VERSION):
        print(f"Error: Python version {Constants.MIN_PYTHON_VERSION[0]}.{Constants.MIN_PYTHON_VERSION[1]} or higher is required")
        exit(1)
    
    set_db_location(db_folder)
    
    # Create Flask app with correct static folder path
    from flask import Flask
    app = Flask(__name__, static_folder='frontend/static', static_url_path='/static')
    app.config["SECRET_KEY"] = os.urandom(24)
    app.config["JSON_SORT_KEYS"] = False
    
    # Set the app on the server
    SERVER.app = app
    
    # Register blueprints
    from frontend.api import api_bp
    from frontend.api_metadata_fixed import metadata_api_bp
    from frontend.api_ebooks import ebooks_api_bp
    from frontend.api_collections import collections_api
    from frontend.api_folders import folders_api
    from frontend.api_rootfolders import rootfolders_api_bp
    from frontend.ui import ui_bp
    from frontend.image_proxy import image_proxy_bp
    
    app.register_blueprint(api_bp)
    app.register_blueprint(metadata_api_bp, url_prefix='/api/metadata')
    app.register_blueprint(ebooks_api_bp)
    app.register_blueprint(collections_api)
    app.register_blueprint(folders_api)
    app.register_blueprint(rootfolders_api_bp)
    app.register_blueprint(ui_bp)
    app.register_blueprint(image_proxy_bp)
    
    with SERVER.app.app_context():
        setup_db()
        
        s = Settings()
        s.restart_on_hosting_changes = False
        
        if host:
            try:
                s.update({"host": host})
            except ValueError:
                print("Error: Invalid host value")
                exit(1)
        
        if port:
            try:
                s.update({"port": port})
            except ValueError:
                print("Error: Invalid port value")
                exit(1)
        
        if url_base is not None:
            try:
                s.update({"url_base": url_base})
            except ValueError:
                print("Error: Invalid url base value")
                exit(1)
        
        s.restart_on_hosting_changes = True
        settings = s.get_settings()
        SERVER.set_url_base(settings.url_base)
        
        # Initialize metadata service
        from backend.features.metadata_service import init_metadata_service
        init_metadata_service()
        
        # Run setup check
        from backend.features.setup_check import check_setup_on_startup
        check_setup_on_startup()
        
        task_handler = TaskHandler()
        task_handler.handle_intervals()
    
    try:
        print(f"\nReadloom is now running!")
        print(f"Open your browser and navigate to http://{host or '0.0.0.0'}:{port or 7227}/ to view the application")
        
        # Run the server directly (no subprocess)
        SERVER.run(settings.host, settings.port)
    except KeyboardInterrupt:
        print("\nShutting down Readloom...")
    finally:
        task_handler.stop_handle()
        print("Readloom has been shut down")

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Readloom is a manga, manwa, and comics collection manager with a focus on release tracking and calendar functionality.")
    
    fs = parser.add_argument_group(title="Folders and files")
    fs.add_argument(
        '-d', '--DatabaseFolder',
        type=str,
        help="The folder in which the database will be stored or in which a database is for Readloom to use"
    )
    fs.add_argument(
        '-l', '--LogFolder',
        type=str,
        help="The folder in which the logs from Readloom will be stored"
    )
    fs.add_argument(
        '-f', '--LogFile',
        type=str,
        help="The filename of the file in which the logs from Readloom will be stored"
    )
    
    hs = parser.add_argument_group(title="Hosting settings")
    hs.add_argument(
        '-o', '--Host',
        type=str,
        help="The host to bind the server to"
    )
    hs.add_argument(
        '-p', '--Port',
        type=int,
        help="The port to bind the server to"
    )
    hs.add_argument(
        '-u', '--UrlBase',
        type=str,
        help="The URL base to use for the server"
    )
    
    args = parser.parse_args()
    
    main(
        db_folder=args.DatabaseFolder,
        log_folder=args.LogFolder,
        log_file=args.LogFile,
        host=args.Host,
        port=args.Port,
        url_base=args.UrlBase
    )
