#!/bin/bash

# This script will fix the collections table constraint issue in the Docker container

echo "Starting database fix..."

# Stop the container if it's running
docker-compose down

# Create a temporary Dockerfile for the fix
cat > Dockerfile.fix << EOF
FROM python:3.11-slim
WORKDIR /app
COPY fix_database.py /app/
CMD ["python", "fix_database.py"]
EOF

# Build the fix image
docker build -t readloom-db-fix -f Dockerfile.fix .

# Run the fix container with the data volume mounted
docker run --rm -v ./data:/config readloom-db-fix

# Remove the temporary Dockerfile
rm Dockerfile.fix

# Rebuild the main image
docker-compose build --no-cache

# Start the container
docker-compose up -d

echo "Fix completed. Check the logs for any errors."
