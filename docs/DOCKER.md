# Docker Guide for Readloom

This document provides detailed information about running Readloom using Docker.

## Quick Start

To run Readloom using Docker:

```bash
# Clone the repository
git clone https://github.com/yourusername/Readloom.git
cd Readloom

# Build and start the container
docker compose up -d
```

Readloom will be available at http://localhost:7227

## Docker Compose Configuration

The default `docker-compose.yml` file includes the following configuration:

```yaml
services:
  readloom:
    build: .
    container_name: readloom
    restart: unless-stopped
    ports:
      - "7227:7227"
    volumes:
      - ./data:/config
    environment:
      - TZ=UTC
      - PYTHONUNBUFFERED=1
    command:
      - "-o"
      - "0.0.0.0"
      - "-p"
      - "7227"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Docker Volumes

The Docker container uses the following volume:

- `./data:/config`: Stores all Readloom data, including the database, logs, and e-books

## Docker Environment Variables

- `TZ`: Set your timezone (default: UTC)
- `PYTHONUNBUFFERED`: Ensures Python output is not buffered (set to 1)

## Building the Docker Image

If you want to build the Docker image manually:

```bash
docker build -t readloom .
```

## Running the Docker Container Manually

If you prefer to run the container without Docker Compose:

```bash
docker run -d \
  --name readloom \
  -p 7227:7227 \
  -v ./data:/config \
  -e TZ=UTC \
  readloom
```

## Troubleshooting

### Common Issues

1. **Container exits with code 127**

   This usually indicates a missing command or dependency. The Dockerfile has been updated to include all required dependencies:
   - `iproute2` for the `ip` command
   - `net-tools` for the `netstat` command

   If you encounter this issue, rebuild your Docker image:
   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

2. **Permission Issues**

   If you encounter permission issues with the volume mount:
   ```bash
   # Check the permissions on your data directory
   ls -la ./data
   
   # Fix permissions if needed
   sudo chown -R 1000:1000 ./data
   ```

3. **Network Issues**

   If Readloom is not accessible:
   ```bash
   # Check if the container is running
   docker ps
   
   # Check the container logs
   docker logs readloom
   
   # Check if the port is exposed correctly
   docker port readloom
   ```

## Advanced Configuration

### Custom Port

To use a different port:

```yaml
services:
  readloom:
    ports:
      - "8080:7227"  # Map host port 8080 to container port 7227
```

### Persistent Storage

For more complex storage needs:

```yaml
services:
  readloom:
    volumes:
      - ./data/config:/config
      - ./data/manga:/manga  # Additional volume for manga storage
```

### Health Checks

The Docker container includes a health check that verifies the application is running correctly. You can view the health status with:

```bash
docker inspect --format='{{.State.Health.Status}}' readloom
```

## Updating Readloom

To update to the latest version:

```bash
# Pull the latest code
git pull

# Rebuild and restart the container
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Docker Compose Commands

- Start the container: `docker compose up -d`
- Stop the container: `docker compose down`
- View logs: `docker compose logs`
- Restart the container: `docker compose restart`
- Rebuild the container: `docker compose build`
