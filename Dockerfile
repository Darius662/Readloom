FROM python:3.11-slim

LABEL maintainer="MangaArr Team"
LABEL description="Manga, Manwa, and Comics Collection Manager"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MANGARR_DATA=/config

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    if [ "$(uname -m)" = "x86_64" ]; then \
        pip install --no-cache-dir pywin32; \
    fi

# Copy application code
COPY . .

# Create volume directories
RUN mkdir -p /config/data /config/logs

# Expose port
EXPOSE 7227

# Set entrypoint
ENTRYPOINT ["python", "MangaArr.py", "-d", "/config/data", "-l", "/config/logs"]

# Default command
CMD ["-o", "0.0.0.0", "-p", "7227"]
