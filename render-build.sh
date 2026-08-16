#!/bin/bash

echo "Starting Render build process..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright
echo "Installing Playwright..."
playwright install chromium
playwright install-deps

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p storage/exports

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "Build completed successfully!"