FROM python:3.12-slim AS base

# Security: run as non-root user
RUN groupadd --gid 1001 carbonpilot && \
    useradd --uid 1001 --gid 1001 --no-create-home carbonpilot

WORKDIR /app

# Install system dependencies for OCR and PDF parsing
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv==0.4.18

# Copy dependency spec first (layer caching)
COPY pyproject.toml .
COPY README.md .

# Install production dependencies only
RUN uv pip install --system --no-cache-dir .


# Copy application source
COPY app/ ./app/

# Switch to non-root
USER carbonpilot

# Cloud Run expects PORT env var (default 8080)
ENV PORT=8080
EXPOSE 8080

# Health check for Cloud Run readiness probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:${PORT}/health', timeout=4)"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1 --log-level warning"]
