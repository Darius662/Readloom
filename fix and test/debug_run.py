#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from flask import Flask

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.base.logging import LOGGER
from backend.features.metadata_service import init_metadata_service
from frontend.api import api_bp
from frontend.api_metadata import metadata_api_bp
from frontend.ui import ui_bp

def main():
    try:
        print("Creating Flask app...")
        app = Flask(__name__)
        app.config["SECRET_KEY"] = os.urandom(24)
        app.config["JSON_SORT_KEYS"] = False
        
        print("Initializing metadata service...")
        init_metadata_service()
        
        print("Registering blueprints...")
        app.register_blueprint(api_bp)
        app.register_blueprint(metadata_api_bp, url_prefix='/api/metadata')
        app.register_blueprint(ui_bp)
        
        print("Starting server...")
        app.run(host='127.0.0.1', port=7227, debug=True)
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
