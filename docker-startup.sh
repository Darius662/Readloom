#!/bin/bash
set -e

echo "Starting Readloom Docker container..."

# Function to handle signals
cleanup() {
    echo "Received signal to shut down..."
    if [ -n "$READLOOM_PID" ] && kill -0 $READLOOM_PID 2>/dev/null; then
        echo "Stopping Readloom process (PID: $READLOOM_PID)..."
        kill -TERM $READLOOM_PID
        wait $READLOOM_PID
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

# Start Readloom directly (no background)
echo "Running Readloom_direct.py with arguments: -d /config/data -l /config/logs -o 0.0.0.0 -p 7227"
# Using exec replaces the current process, so nothing after this will run
exec python -u Readloom_direct.py -d /config/data -l /config/logs -o 0.0.0.0 -p 7227
