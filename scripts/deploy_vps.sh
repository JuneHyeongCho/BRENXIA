#!/bin/bash
# BRENXIA Agent VPS Deployment helper script.
# This script installs uv, configures environment, syncs packages, and triggers background startup.

echo "=================================================="
echo "Starting BRENXIA Agent VPS Deployment..."
echo "=================================================="

# 1. Install uv if not found
if ! command -v uv &> /dev/null; then
    echo "[INFO] uv is not installed. Installing Astral uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Apply environment path changes
    export PATH="$HOME/.local/bin:$PATH"
    if [ -f "$HOME/.local/bin/env" ]; then
        source "$HOME/.local/bin/env"
    fi
else
    echo "[INFO] uv is already installed."
fi

# 2. Check for .env file
if [ ! -f ".env" ]; then
    echo "[INFO] Creating default .env file..."
    cat <<EOT > .env
# Default dashboard binding
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8000

# Company default info
COMPANY_MASTER_EMAIL=brenxia@brenxia.com
CEO_EMAIL=psyche@brenxia.com
GOOGLE_CREDENTIALS_FILE=config/credentials.json
EOT
    echo "[SUCCESS] Created default .env file."
fi

# 3. Synchronize package dependencies and Python versions
echo "[INFO] Syncing packages and virtual environment..."
uv sync

# 4. Check for credentials file warning
if [ ! -f "config/credentials.json" ]; then
    echo "[WARNING] config/credentials.json is not found."
    echo "[WARNING] The server will run in MOCK fallback simulation mode."
    echo "[WARNING] Please upload your Google Workspace Service Account JSON credentials to config/credentials.json for production."
fi

# 5. Make sure data folder exists
mkdir -p data

# 6. Launch dashboard in background
echo "[INFO] Starting dashboard server in background..."
nohup uv run python run_dashboard.py > data/dashboard.log 2>&1 &

echo "=================================================="
echo "[SUCCESS] BRENXIA Agent Dashboard started."
echo "[INFO] Check logs in: data/dashboard.log"
echo "[INFO] URL: http://72.62.65.177:8000"
echo "=================================================="
