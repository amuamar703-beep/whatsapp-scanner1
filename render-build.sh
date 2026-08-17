#!/bin/bash

set -e

echo "Starting Render build process..."

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Verify critical packages are installed
echo "Verifying installations..."
python -c "import pydantic; print(f'Pydantic version: {pydantic.__version__}')"
python -c "import dotenv; print('python-dotenv installed')"
python -c "import aiogram; print('aiogram installed')"
python -c "import telethon; print('telethon installed')"
python -c "import sqlalchemy; print('sqlalchemy installed')"
python -c "import redis; print('redis installed')"

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p storage/exports

# Run database migrations
echo "Running database migrations..."
python -c "from app.database.database import init_db; init_db(); print('Database initialized')"

echo "Build completed successfully!"
