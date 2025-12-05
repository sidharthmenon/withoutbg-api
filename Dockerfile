# Stage 1: Builder with uv
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy project dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into .venv
RUN uv sync --frozen --no-dev

# Copy source code
COPY app ./app
COPY models ./models

# Stage 2: Runtime
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the virtual environment
COPY --from=builder /app/.venv /app/.venv

# Add .venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY app ./app
COPY models ./models

# Environment variables
ENV PYTHONUNBUFFERED=1

ENV WITHOUTBG_DEPTH_MODEL_PATH=/app/models/checkpoints/depth_anything_v2_vits_slim.onnx
ENV WITHOUTBG_ISNET_MODEL_PATH=/app/models/checkpoints/isnet.onnx
ENV WITHOUTBG_MATTING_MODEL_PATH=/app/models/checkpoints/focus_matting_1.0.0.onnx
ENV WITHOUTBG_REFINER_MODEL_PATH=/app/models/checkpoints/focus_refiner_1.0.0.onnx

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
