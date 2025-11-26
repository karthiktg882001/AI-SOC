#!/bin/bash
# Bash script to test all SOC services
# Run: chmod +x scripts/test_all_services.sh && ./scripts/test_all_services.sh

echo "========================================"
echo "SOC Assistant - Service Health Check"
echo "========================================"
echo ""

BASE_URL="http://localhost"
ALL_OK=true

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test Frontend
echo -e "${YELLOW}Testing Frontend (Port 3000)...${NC}"
if curl -s -f "$BASE_URL:3000" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend is not accessible${NC}"
    ALL_OK=false
fi

# Test ML Service
echo -e "${YELLOW}Testing ML Service (Port 8000)...${NC}"
if curl -s -f "$BASE_URL:8000/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ ML Service is running${NC}"
    STATUS=$(curl -s "$BASE_URL:8000/health" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "unknown")
    echo "  Status: $STATUS"
else
    echo -e "${RED}✗ ML Service is not accessible${NC}"
    ALL_OK=false
fi

# Test Log Ingestion Service
echo -e "${YELLOW}Testing Log Ingestion Service (Port 8080)...${NC}"
if curl -s -f "$BASE_URL:8080/api/logs/stats" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Log Ingestion Service is running${NC}"
else
    echo -e "${RED}✗ Log Ingestion Service is not accessible${NC}"
    ALL_OK=false
fi

# Test ML Service API Endpoints
echo -e "${YELLOW}Testing ML Service API Endpoints...${NC}"
if curl -s -f "$BASE_URL:8000/api/dashboard/stats" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Dashboard API is working${NC}"
else
    echo -e "${RED}✗ Dashboard API failed${NC}"
    ALL_OK=false
fi

# Get Docker Container Status
echo ""
echo -e "${YELLOW}Checking Docker Containers...${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Get Network IP (for mobile testing)
echo ""
echo -e "${YELLOW}Network Information for Mobile Testing:${NC}"
if command -v ip &> /dev/null; then
    IP=$(ip route get 1.1.1.1 | awk '{print $7; exit}' 2>/dev/null)
elif command -v ifconfig &> /dev/null; then
    IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -1)
fi

if [ ! -z "$IP" ]; then
    echo -e "${GREEN}Your IP Address: $IP${NC}"
    echo -e "${GREEN}Access from mobile: http://$IP:3000${NC}"
else
    echo "Could not determine IP address"
fi

echo ""
echo "========================================"
if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}✓ All services are running correctly!${NC}"
else
    echo -e "${RED}✗ Some services have issues. Check logs above.${NC}"
fi
echo "========================================"

