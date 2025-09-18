# MangaArr Installation Guide

This guide will help you install and configure MangaArr on your system.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Docker Installation (Recommended)](#docker-installation-recommended)
  - [Manual Installation](#manual-installation)
- [Initial Configuration](#initial-configuration)
- [Updating MangaArr](#updating-mangarr)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing MangaArr, make sure you have:

- A system running Windows, macOS, or Linux
- For Docker installation:
  - Docker and Docker Compose installed
- For manual installation:
  - Python 3.8 or higher
  - pip (Python package manager)
  - Git (optional, for cloning the repository)

## Installation Methods

### Docker Installation (Recommended)

Using Docker is the easiest way to get MangaArr up and running.

1. **Clone the repository** (or download and extract the ZIP file):
   ```bash
   git clone https://github.com/yourusername/MangaArr.git
   cd MangaArr
   ```

2. **Start MangaArr with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Access MangaArr** at http://localhost:7227

#### Docker Compose Configuration

You can customize the Docker Compose configuration by editing the `docker-compose.yml` file:

```yaml
version: '3'

services:
  mangarr:
    build: .
    container_name: mangarr
    restart: unless-stopped
    ports:
      - "7227:7227"  # Change the first number to use a different port
    volumes:
      - ./data:/config  # Change ./data to a different path if desired
    environment:
      - TZ=UTC  # Set your timezone here
```

### Manual Installation

If you prefer not to use Docker, you can install MangaArr manually.

1. **Clone the repository** (or download and extract the ZIP file):
   ```bash
   git clone https://github.com/yourusername/MangaArr.git
   cd MangaArr
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run MangaArr**:
   ```bash
   python MangaArr.py
   ```

4. **Access MangaArr** at http://localhost:7227

#### Command Line Arguments

MangaArr supports several command line arguments:

- `-d, --DatabaseFolder`: The folder to store the database in
- `-l, --LogFolder`: The folder to store logs in
- `-f, --LogFile`: The log file name
- `-o, --Host`: The host to bind to (default: 0.0.0.0)
- `-p, --Port`: The port to bind to (default: 7227)
- `-u, --UrlBase`: The URL base (e.g., /mangarr)

Example:
```bash
python MangaArr.py -d /path/to/data -l /path/to/logs -p 8080
```

## Initial Configuration

After installing MangaArr, follow these steps to configure it:

1. **Access the web interface** at http://localhost:7227 (or your custom port)

2. **Configure settings**:
   - Go to the Settings page
   - Adjust general settings, calendar settings, and logging settings as needed
   - Save your changes

3. **Add your first series**:
   - Go to the Series page
   - Click "Add Series"
   - Fill in the details and save

## Updating MangaArr

### Docker Update

1. **Pull the latest changes**:
   ```bash
   git pull
   ```

2. **Rebuild and restart the container**:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

### Manual Update

1. **Pull the latest changes**:
   ```bash
   git pull
   ```

2. **Update dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Restart MangaArr**:
   ```bash
   python MangaArr.py
   ```

## Troubleshooting

### Common Issues

#### Database Errors

If you encounter database errors:

1. Make sure the database directory is writable
2. Try backing up and recreating the database:
   ```bash
   mv data/mangarr.db data/mangarr.db.bak
   ```

#### Port Already in Use

If port 7227 is already in use:

1. Change the port using the `-p` command line argument
2. Or modify the `docker-compose.yml` file to use a different port

#### Integration Issues

If integrations with Home Assistant or Homarr aren't working:

1. Check network connectivity between the systems
2. Verify API endpoints are accessible
3. Check the logs for error messages

### Getting Help

If you encounter issues not covered here:

1. Check the logs in the data/logs directory
2. Search for similar issues in the GitHub repository
3. Open a new issue with detailed information about your problem

For more information, visit the [MangaArr GitHub repository](https://github.com/yourusername/MangaArr).
