# Use Python 3.10 slim as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Build and install the package
RUN pip install --no-cache-dir .

# Expose port 8000
EXPOSE 8000

# Set environment variables
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000
ENV DEBUG=False

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the web service
CMD ["python", "-m", "phoenix_smartcaseai.main"]


