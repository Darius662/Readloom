#!/bin/bash

echo "Stopping any running MangaArr processes..."
pkill -f "python.*MangaArr.py" || true

echo "Starting test server on port 7227..."
python test_server.py
