#!/bin/bash

echo "Testing SOC API Endpoints"
echo "========================="
echo ""

API_URL="http://localhost:8000"
INGESTION_URL="http://localhost:8080"

echo "1. Testing ML Service Health..."
curl -s "$API_URL/health" | jq .
echo ""

echo "2. Testing Dashboard Stats..."
curl -s "$API_URL/api/dashboard/stats" | jq .
echo ""

echo "3. Testing Recent Threats..."
curl -s "$API_URL/api/threats/recent?limit=5" | jq .
echo ""

echo "4. Testing Log Ingestion..."
curl -X POST "$INGESTION_URL/api/logs/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "firewall",
    "timestamp": "2024-01-15T10:30:00",
    "logLevel": "WARN",
    "message": "Suspicious connection attempt from 192.168.1.100",
    "metadata": {
      "ip": "192.168.1.100",
      "port": 443,
      "protocol": "HTTPS"
    }
  }' | jq .
echo ""

echo "5. Testing Anomaly Detection..."
curl -X POST "$API_URL/api/detect/anomaly" \
  -H "Content-Type: application/json" \
  -d '{
    "logId": "test-123",
    "logData": {
      "source": "firewall",
      "timestamp": "2024-01-15T10:30:00",
      "logLevel": "ERROR",
      "message": "Multiple failed login attempts detected",
      "metadata": {
        "ip": "192.168.1.100"
      }
    }
  }' | jq .
echo ""

echo "6. Getting All Incidents..."
curl -s "$API_URL/api/incidents?limit=5" | jq .
echo ""

echo "Tests completed!"

