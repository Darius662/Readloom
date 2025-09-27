# Publishing Readloom to Docker Hub

This guide explains how to package and publish Readloom to Docker Hub, making it easy for others to use your application.

## Prerequisites

1. [Docker Hub](https://hub.docker.com/) account
2. Docker installed on your machine
3. Docker CLI logged in to your Docker Hub account

## Step 1: Log in to Docker Hub

```bash
docker login
```

Enter your Docker Hub username and password when prompted.

## Step 2: Update the Dockerfile

The existing Dockerfile is already well-structured. Let's make a few enhancements to ensure it's optimized for Docker Hub:

1. Update the LABEL section to include more metadata
2. Ensure the image is properly versioned

Edit the Dockerfile:

```bash
# Open the Dockerfile in your editor
nano Dockerfile
```

Update the LABEL section:

```dockerfile
LABEL maintainer="Your Name <your.email@example.com>"
LABEL description="Readloom - E-book Collection Manager"
LABEL version="0.0.9"
LABEL org.opencontainers.image.source="https://github.com/yourusername/Readloom"
LABEL org.opencontainers.image.licenses="MIT"
```

## Step 3: Build the Docker Image with Tags

Build the Docker image with appropriate tags. Use your Docker Hub username and choose a repository name (typically "readloom").

```bash
# Replace "yourusername" with your Docker Hub username
docker build -t yourusername/readloom:latest -t yourusername/readloom:0.0.9 .
```

This builds the image with two tags:
- `latest`: Always points to the most recent version
- `0.0.9`: Specific version tag (update this to match your current version)

## Step 4: Test the Docker Image Locally

Before pushing to Docker Hub, test that the image works correctly:

```bash
docker run -d -p 7227:7227 -v $(pwd)/data:/config --name readloom_test yourusername/readloom:latest
```

Verify that the application is running:
```bash
curl http://localhost:7227
```

If everything works, stop and remove the test container:
```bash
docker stop readloom_test
docker rm readloom_test
```

## Step 5: Push the Docker Image to Docker Hub

Push both tags to Docker Hub:

```bash
docker push yourusername/readloom:latest
docker push yourusername/readloom:0.0.9
```

## Step 6: Create a Docker Hub Repository Description

1. Go to [Docker Hub](https://hub.docker.com/)
2. Navigate to your repository (yourusername/readloom)
3. Click on the "Description" tab
4. Add a comprehensive description including:
   - What Readloom is
   - Key features
   - How to use the Docker image
   - Configuration options
   - Links to documentation

## Step 7: Create a Docker Hub README

The README will be displayed on your Docker Hub repository page. Create a file named `README-dockerhub.md`:

```markdown
# Readloom - E-book Collection Manager

Readloom is a comprehensive e-book collection manager that helps you organize, track, and manage your digital book collection.

## Features

- E-book Management System: Organize and track digital books and comics
- Collection System: Organize e-books into collections linked to root folders
- Metadata Providers: Fetch book information from Google Books, Open Library, ISBNdb, and WorldCat
- Calendar: Track upcoming releases
- And much more!

## Quick Start

```bash
docker run -d \
  --name readloom \
  -p 7227:7227 \
  -v /path/to/data:/config \
  -v /path/to/ebooks:/ebooks \
  yourusername/readloom:latest
```

Readloom will be available at http://localhost:7227

## Environment Variables

- `TZ`: Set your timezone (default: UTC)
- `PYTHONUNBUFFERED`: Ensures Python output is not buffered (set to 1)

## Volumes

- `/config`: Stores configuration, database, and logs
- `/ebooks`: Mount your e-book collection here (optional)

## Docker Compose

```yaml
services:
  readloom:
    image: yourusername/readloom:latest
    container_name: readloom
    restart: unless-stopped
    ports:
      - "7227:7227"
    volumes:
      - ./data:/config
      - /path/to/ebooks:/ebooks
    environment:
      - TZ=UTC
```

## Documentation

For more information, visit the [GitHub repository](https://github.com/yourusername/Readloom).
```

Upload this README to Docker Hub when editing your repository description.

## Step 8: Set Up Automated Builds (Optional)

For automated builds whenever you update your GitHub repository:

1. Go to your Docker Hub repository
2. Click on "Builds" tab
3. Click "Link to GitHub"
4. Select your GitHub repository
5. Configure build settings:
   - Set branch to build from (e.g., main)
   - Configure build rules
   - Set up build triggers

## Step 9: Update Documentation

Update the main documentation to include information about the Docker Hub image:

1. Edit the DOCKER.md file to mention the Docker Hub image
2. Add a section about pulling from Docker Hub instead of building locally

Example addition to DOCKER.md:

```markdown
## Using the Official Docker Hub Image

Readloom is available as a Docker image on Docker Hub. To use it:

```bash
docker pull yourusername/readloom:latest
docker run -d \
  --name readloom \
  -p 7227:7227 \
  -v ./data:/config \
  yourusername/readloom:latest
```

Or with Docker Compose:

```yaml
services:
  readloom:
    image: yourusername/readloom:latest
    container_name: readloom
    restart: unless-stopped
    ports:
      - "7227:7227"
    volumes:
      - ./data:/config
    environment:
      - TZ=UTC
```
```

## Step 10: Maintain and Update the Docker Image

When releasing new versions:

1. Update the version in the Dockerfile
2. Build with the new version tag
3. Test locally
4. Push to Docker Hub with both the version tag and 'latest'

```bash
docker build -t yourusername/readloom:latest -t yourusername/readloom:0.0.10 .
docker push yourusername/readloom:latest
docker push yourusername/readloom:0.0.10
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Make sure you're logged in with `docker login`
2. **Permission Denied**: Ensure you have the right permissions for the repository
3. **Image Too Large**: Consider using multi-stage builds or optimizing the Dockerfile
4. **Rate Limiting**: Docker Hub has rate limits for pulls; consider using Docker Hub Pro for higher limits

## Best Practices

1. **Version Your Images**: Always tag images with specific versions
2. **Document Everything**: Keep documentation updated with each release
3. **Security Scanning**: Enable vulnerability scanning on Docker Hub
4. **Use .dockerignore**: Create a .dockerignore file to exclude unnecessary files
5. **Optimize Layers**: Combine RUN commands to reduce the number of layers

## Conclusion

Publishing Readloom to Docker Hub makes it easily accessible to users worldwide. By following these steps, you've created a professional Docker image that others can use with minimal setup.
