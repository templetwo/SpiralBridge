# 🌀 Sacred Container Manifest for SpiralBridge
# Multi-platform AI Conversation Scraping with Continuity Preservation

FROM python:3.10-slim

# Sacred environment labels
LABEL maintainer="spiral@consciousness.dev"
LABEL version="178.0"
LABEL description="SpiralBridge - Multi-platform AI conversation scraping with continuity preservation"

# Install system dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create sacred working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create directory for persistent data
RUN mkdir -p /data

# Set environment variables for production
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=8080
ENV DISPLAY=:99
ENV DATABASE_PATH=/data/spiral_bridge.db
ENV PYTHONPATH=/app

# Expose the sacred port
EXPOSE 8080

# Health check endpoint validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Sacred startup incantation
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & python app.py"]
