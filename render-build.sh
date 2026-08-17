#!/bin/bash

set -e

echo "Starting Render build process..."

# Clean pip cache
echo "Cleaning pip cache..."
pip cache purge || true

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Verify critical packages are installed
echo "Verifying installations..."
python -c "import pydantic; print('Pydantic installed')"
python -c "import aiogram; print('Aiogram installed')"
python -c "import telethon; print('Telethon installed')"
python -c "import sqlalchemy; print('SQLAlchemy installed')"
python -c "import redis; print('Redis installed')"
python -c "import dotenv; print('python-dotenv installed')"

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p storage/exports

# Run database migrations
echo "Running database migrations..."
python -c "from app.database.database import init_db; init_db(); print('Database initialized')" 2>/dev/null || echo "Migration skipped"

echo "Build completed successfully!"
