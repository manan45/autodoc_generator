# Auto Documentation Generation System Docker Image
FROM python:3.9-slim

LABEL maintainer="Auto Documentation System"
LABEL description="Automatic code documentation generation system"

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    graphviz \
    graphviz-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY config/ config/
COPY templates/ templates/

# Create necessary directories
RUN mkdir -p docs diagrams

# Set proper permissions
RUN chmod +x src/main.py

# Create non-root user for security
RUN groupadd -r docgen && useradd -r -g docgen docgen
RUN chown -R docgen:docgen /app
USER docgen

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python src/main.py --help > /dev/null || exit 1

# Default command
ENTRYPOINT ["python", "src/main.py"]
CMD ["--analyze", "--generate", "--build"]

# Expose port for serving documentation (if needed)
EXPOSE 8000

# Volume for output
VOLUME ["/app/docs"]
