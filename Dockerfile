# Multi-stage Dockerfile for FVOAS
# Federal Voice Anonymization and Analysis System

FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Create app directory
WORKDIR /app

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 fvoas && \
    chown -R fvoas:fvoas /app

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs /app/api_results && \
    chown -R fvoas:fvoas /app/data /app/logs /app/api_results

USER fvoas

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (can be overridden)
ENTRYPOINT ["python"]
CMD ["run_api_server.py", "--host", "0.0.0.0"]
