#!/bin/bash
set -e

echo "Starting MangaArr Docker container..."

# Function to handle signals
cleanup() {
    echo "Received signal to shut down..."
    if [ -n "$MANGARR_PID" ] && kill -0 $MANGARR_PID 2>/dev/null; then
        echo "Stopping MangaArr process (PID: $MANGARR_PID)..."
        kill -TERM $MANGARR_PID
        wait $MANGARR_PID
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Print network information for debugging
echo "Network interfaces:"
ip addr

echo "Listening ports:"
netstat -tulpn

# Start MangaArr directly (no background)
echo "Running MangaArr_direct.py with arguments: -d /config/data -l /config/logs -o 0.0.0.0 -p 7227"
# Using exec replaces the current process, so nothing after this will run
exec python -u MangaArr_direct.py -d /config/data -l /config/logs -o 0.0.0.0 -p 7227
