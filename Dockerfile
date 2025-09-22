FROM python:3.11-slim

LABEL maintainer="MangaArr Team"
LABEL description="Manga, Manwa, and Comics Collection Manager"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MANGARR_DATA=/config
ENV MANGARR_DOCKER=1

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies, curl and netcat for healthcheck and debugging
RUN apt-get update && apt-get install -y curl netcat-openbsd && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Copy the direct version of MangaArr.py
COPY MangaArr_direct.py /app/

# Create volume directories
RUN mkdir -p /config/data /config/logs

# Expose port
EXPOSE 7227

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD nc -z localhost 7227 || exit 1

# Copy startup and debug scripts
COPY docker-entrypoint.sh docker-startup.sh docker-debug.sh run_test_server.sh /usr/local/bin/
# Ensure scripts have correct line endings and are executable
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh && \
    sed -i 's/\r$//' /usr/local/bin/docker-startup.sh && \
    sed -i 's/\r$//' /usr/local/bin/docker-debug.sh && \
    sed -i 's/\r$//' /usr/local/bin/run_test_server.sh && \
    chmod +x /usr/local/bin/docker-entrypoint.sh && \
    chmod +x /usr/local/bin/docker-startup.sh && \
    chmod +x /usr/local/bin/docker-debug.sh && \
    chmod +x /usr/local/bin/run_test_server.sh
ENTRYPOINT ["/usr/local/bin/docker-startup.sh"]

# Default command
CMD ["-o", "0.0.0.0", "-p", "7227"]
