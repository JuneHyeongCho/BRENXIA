# Use astral-sh uv official image with Python 3.12
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project files
COPY pyproject.toml uv.lock README.md ./

# Install project dependencies using uv
RUN uv sync --frozen --no-dev --no-install-project

# Copy source code and other workspace files
COPY src/ ./src/
COPY google_credentials.json google_chat_user_client_secret.json .env ./

# Install project
RUN uv sync --frozen --no-dev

# Expose port
EXPOSE 8000

# Create data directory for local JSON database
RUN mkdir -p /app/data

# Run API server
CMD ["uv", "run", "vibe-cording-dashboard"]
