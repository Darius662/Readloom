#!/bin/sh

# Print debug info
echo "Starting docker-entrypoint.sh"
echo "Current directory: $(pwd)"
echo "Command arguments: $@"

# Run MangaArr but trap its exit code
echo "Running MangaArr with arguments: -d /config/data -l /config/logs $@"
python -u MangaArr.py -d /config/data -l /config/logs "$@"

# Get the exit code
EXIT_CODE=$?
echo "MangaArr exited with code: $EXIT_CODE"

# Always exit with code 0 to prevent Docker from restarting the container
echo "Forcing exit with code 0 to prevent Docker restart loop"
exit 0
