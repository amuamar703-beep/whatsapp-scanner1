#!/bin/bash

echo "=== WhatsApp Scanner Monitor ==="
echo ""

echo "📊 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "whatsapp_scanner|NAMES"

echo ""
echo "📈 Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep -E "whatsapp_scanner|NAME"

echo ""
echo "📝 Last 10 Log Lines (App):"
docker logs --tail 10 whatsapp_scanner_app

echo ""
echo "📝 Last 10 Log Lines (Worker):"
docker logs --tail 10 whatsapp_scanner_worker

echo ""
echo "📊 Queue Length:"
docker exec -it whatsapp_scanner_redis redis-cli LLEN whatsapp_scanner_jobs