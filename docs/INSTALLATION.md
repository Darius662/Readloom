# Readloom Installation Guide

This guide will help you install and configure Readloom on your system.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Docker Installation (Recommended)](#docker-installation-recommended)
  - [Manual Installation](#manual-installation)
- [Initial Configuration](#initial-configuration)
- [Updating Readloom](#updating-readloom)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing Readloom, make sure you have:

- A system running Windows, macOS, or Linux
- For Docker installation:
  - Docker and Docker Compose installed
- For manual installation:
  - Python 3.8 or higher
  - pip (Python package manager)
  - Git (optional, for cloning the repository)

## Installation Methods

### Docker Installation (Recommended)

Using Docker is the easiest way to get Readloom up and running.

1. **Clone the repository** (or download and extract the ZIP file):
   ```bash
   git clone https://github.com/yourusername/Readloom.git
   cd Readloom
   ```

2. **Start Readloom with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Access Readloom** at http://localhost:7227

#### Docker Compose Configuration

You can customize the Docker Compose configuration by editing the `docker-compose.yml` file:

```yaml
version: '3'

services:
  readloom:
    build: .
    container_name: readloom
    restart: unless-stopped
    ports:
      - "7227:7227"  # Change the first number to use a different port
    volumes:
      - ./data:/config  # Change ./data to a different path if desired
    environment:
      - TZ=UTC  # Set your timezone here
```

### Manual Installation

If you prefer not to use Docker, you can install Readloom manually.

1. **Clone the repository** (or download and extract the ZIP file):
   ```bash
   git clone https://github.com/yourusername/Readloom.git
   cd Readloom
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Readloom**:
   ```bash
   python Readloom.py
   ```

4. **Access Readloom** at http://localhost:7227

#### Command Line Arguments

Readloom supports several command line arguments:

- `-d, --DatabaseFolder`: The folder to store the database in
- `-l, --LogFolder`: The folder to store logs in
- `-f, --LogFile`: The log file name
- `-o, --Host`: The host to bind to (default: 0.0.0.0)
- `-p, --Port`: The port to bind to (default: 7227)
- `-u, --UrlBase`: The URL base (e.g., /readloom)

Example:
```bash
python Readloom.py -d /path/to/data -l /path/to/logs -p 8080
```

## Initial Configuration

After installing Readloom, you'll be guided through a setup wizard to configure the essential components:

### Setup Wizard

When you first access Readloom at http://localhost:7227 (or your custom port), you'll be presented with a setup wizard that will guide you through:

1. **Creating your first collection**:
   - Enter a name for your collection (e.g., "My Manga Collection")
   - Add an optional description
   - Choose whether this should be your default collection

2. **Setting up your first root folder**:
   - Enter a name for your root folder (e.g., "Main Library")
   - Specify the full path where your manga/comics will be stored
   - Select the primary content type for this folder

3. **Linking your collection and root folder**:
   - The wizard will automatically link your new collection to your root folder

After completing the setup wizard, you can proceed with further configuration:

### Additional Configuration

1. **Configure settings**:
   - Go to the Settings page
   - Adjust general settings, calendar settings, and notification settings as needed
   - Save your changes

2. **Add your first series**:
   - Go to the Series page
   - Click "Add Series"
   - Fill in the details and save
   
3. **Manage your collections**:
   - Go to the Collections page
   - Create additional collections if needed
   - Add more root folders and link them to collections
   - Organize your series into different collections
   
4. **Configure notifications**:
   - Go to the Notifications page
   - Set up notification preferences
   - Subscribe to series for release notifications
   
5. **Set up integrations** (optional):
   - Go to the Integrations page
   - Configure Home Assistant integration
   - Configure Homarr integration

## Updating Readloom

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

3. **Restart Readloom**:
   ```bash
   python Readloom.py
   ```

## Troubleshooting

### Common Issues

#### Database Errors

If you encounter database errors:

1. Make sure the database directory is writable
2. Try backing up and recreating the database:
   ```bash
   mv data/readloom.db data/readloom.db.bak
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
4. For Home Assistant:
   - Ensure the correct API endpoint is configured in your configuration.yaml
   - Verify sensor entities are created correctly
5. For Homarr:
   - Ensure the status endpoint is correctly configured
   - Check that the Readloom service is properly added to your Homarr dashboard

#### Folder Structure Issues

If you encounter issues with folder creation or e-book management:

1. Verify the root folder exists and is writable
2. Check that series are properly added to the database
3. Run the helper scripts to create missing folders:
   ```bash
   python create_missing_folders.py
   ```
4. Check the logs for any errors during folder creation
5. Verify that the folder names match the series titles (with invalid characters replaced)
6. If folder names contain unexpected characters, check the sanitization rules in `helpers.py`

#### Collection Tracking Issues

If you encounter issues with collection tracking:

1. Verify the database is properly initialized
2. Check that series, volumes, and chapters are correctly added
3. Try importing a small collection first to test functionality

#### Notification Issues

If notifications aren't working correctly:

1. Check that you've subscribed to the appropriate series
2. Verify notification settings are configured correctly
3. For external notifications (email, Discord, Telegram):
   - Check that credentials and tokens are correctly entered
   - Verify network connectivity to external services

### Getting Help

If you encounter issues not covered here:

1. Check the logs in the data/logs directory
2. Search for similar issues in the GitHub repository
3. Open a new issue with detailed information about your problem

For more information, visit the [Readloom GitHub repository](https://github.com/yourusername/Readloom).
