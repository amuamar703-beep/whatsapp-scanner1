#!/bin/bash

set -e

echo "Starting WhatsApp Link Scanner..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please create one from .env.example"
    exit 1
fi

# Start services
echo "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "Waiting for services to be healthy..."
sleep 10

# Check health
echo "Running health check..."
python scripts/health_check.py

echo "System started successfully!"
echo ""
echo "Bot is running. Check logs with: docker-compose -f docker-compose.prod.yml logs -f"