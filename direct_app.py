#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
from pathlib import Path

from flask import Flask

# Create data directories
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

logs_dir = Path("data/logs")
logs_dir.mkdir(exist_ok=True)

db_dir = Path("data/db")
db_dir.mkdir(exist_ok=True)

# Set environment variables for database and logs
os.environ["READLOOM_DB_PATH"] = str(db_dir / "readloom.db")
os.environ["READLOOM_LOG_PATH"] = str(logs_dir)

# Create Flask app
app = Flask(__name__)

# Register blueprints
from frontend.api import api_bp
from frontend.ui import ui_bp
from frontend.api_metadata_fixed import metadata_api_bp
from frontend.image_proxy import image_proxy_bp

app.register_blueprint(api_bp)
app.register_blueprint(ui_bp)
app.register_blueprint(metadata_api_bp)
app.register_blueprint(image_proxy_bp)

# Setup database
from backend.internals.db import setup_db
with app.app_context():
    setup_db()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Readloom directly")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=7227, help="Port to bind to (default: 7227)")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    print(f"Starting Readloom on {args.host}:{args.port}...")
    print(f"Open your browser and navigate to http://{args.host}:{args.port}/ to view the application")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
