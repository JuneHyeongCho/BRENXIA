# Use the official Astral uv image as a builder
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies (exclude dev dependencies and project itself first for caching)
RUN uv sync --frozen --no-dev --no-install-project

# Final minimal runner stage
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy all project files
COPY . /app

# Set PATH to use the virtual environment binaries directly
ENV PATH="/app/.venv/bin:$PATH"

# Ensure Python outputs immediately to terminal without buffering
ENV PYTHONUNBUFFERED=1

# Expose the default dashboard port
EXPOSE 8000

# Start dashboard server
CMD ["python", "run_dashboard.py"]
