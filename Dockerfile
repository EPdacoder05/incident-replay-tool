# Multi-stage build for Incident Predictor ML
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 predictor && \
    chown -R predictor:predictor /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=predictor:predictor src/ ./src/
COPY --chown=predictor:predictor pyproject.toml ./

# Switch to non-root user
USER predictor

# Environment variables with defaults
ENV DETECTION_INTERVAL_SECONDS=60
ENV MOCK_MODE=true
ENV SDF_ENDPOINT=https://sdf-gold.internal/api/events
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Expose port (if adding HTTP API in future)
EXPOSE 8080

# Run the prediction engine
CMD ["python", "-m", "src.main"]
