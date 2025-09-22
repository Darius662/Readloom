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

# Start MangaArr in the background with explicit host and port
echo "Running MangaArr with arguments: -d /config/data -l /config/logs -o 0.0.0.0 -p 7227"
python -u MangaArr.py -d /config/data -l /config/logs -o 0.0.0.0 -p 7227 &
MANGARR_PID=$!

# Log the PID
echo "MangaArr started with PID: $MANGARR_PID"

# Wait for MangaArr to exit
wait $MANGARR_PID || true
EXIT_CODE=$?
echo "MangaArr exited with code: $EXIT_CODE"

# Keep the container running
echo "MangaArr has exited, but keeping container running for inspection..."
echo "You can access the container with: docker exec -it mangarr /bin/bash"
echo "To view logs: docker logs mangarr"

# Sleep indefinitely
while true; do
    sleep 3600 & wait $!
done
