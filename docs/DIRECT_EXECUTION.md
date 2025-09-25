# Direct Execution Mode

This document explains how to run Readloom in direct execution mode using `Readloom_direct.py` and details the fixes implemented to ensure proper functionality.

## Overview

Readloom can be run in two primary modes:

1. **Development Mode** (`run_dev.py`): Used for development and testing
2. **Direct Execution Mode** (`Readloom_direct.py`): Used for production or standalone usage

The direct execution mode is designed to run Readloom without additional setup or development environment requirements.

## Recent Fixes

In version 0.0.9, several critical issues in `Readloom_direct.py` were fixed:

### Metadata Service Initialization

Added proper initialization of the metadata service to ensure database tables are created:

```python
# Initialize metadata service
from backend.features.metadata_service import init_metadata_service
init_metadata_service()
```

### Setup Check

Added setup check to ensure the application is properly initialized:

```python
# Run setup check
from backend.features.setup_check import check_setup_on_startup
check_setup_on_startup()
```

### Flask App Creation

Fixed Flask app creation with correct static folder path configuration:

```python
# Create Flask app with correct static folder path
from flask import Flask
app = Flask(__name__, static_folder='frontend/static', static_url_path='/static')
app.config["SECRET_KEY"] = os.urandom(24)
app.config["JSON_SORT_KEYS"] = False

# Set the app on the server
SERVER.app = app
```

### Blueprint Registration

Added proper registration of all required blueprints:

```python
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
```

### Fixed Imports

Added missing OS imports:

```python
from argparse import ArgumentParser
from os import environ, name, path, urandom
import os
from typing import NoReturn, Union
```

## Running in Direct Mode

To run Readloom in direct execution mode:

1. Ensure all dependencies are installed:
   ```
   pip install flask waitress requests
   ```

2. Run the application:
   ```
   python Readloom_direct.py
   ```

3. Access the application in your browser:
   ```
   http://localhost:7227
   ```

## Troubleshooting

If you encounter issues with the direct execution mode:

1. **Static Files Not Loading**: Check that the Flask app is configured with the correct static folder path.

2. **API Errors**: Ensure all blueprints are properly registered.

3. **Database Errors**: Verify that the metadata service is initialized and the setup check is run.

4. **Setup Wizard Not Working**: Make sure the static files are being served correctly and API endpoints are accessible.

## Differences from Development Mode

The main differences between direct execution mode and development mode are:

1. **Server Configuration**: Direct mode uses Waitress for production, while development mode uses Flask's built-in server.

2. **Static File Serving**: Direct mode requires explicit configuration of static file paths.

3. **Initialization**: Direct mode requires explicit initialization of services that are automatically initialized in development mode.

4. **Environment**: Direct mode is designed to run in any environment without additional setup, while development mode assumes a development environment.
