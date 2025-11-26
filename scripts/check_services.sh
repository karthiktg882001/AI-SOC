#!/bin/bash

echo "🔍 Checking SOC Services Status..."
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    local name=$1
    local url=$2
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $name is running"
        return 0
    else
        echo -e "${RED}❌${NC} $name is not responding"
        return 1
    fi
}

check_port() {
    local name=$1
    local port=$2
    
    if nc -z localhost $port 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $name (port $port) is listening"
        return 0
    else
        echo -e "${RED}❌${NC} $name (port $port) is not listening"
        return 1
    fi
}

echo "Checking Infrastructure Services..."
check_port "MongoDB" 27017
check_port "PostgreSQL" 5432
check_port "Kafka" 9092
check_port "Zookeeper" 2181

echo ""
echo "Checking Application Services..."
check_service "ML Service" "http://localhost:8000/health"
check_service "Log Ingestion Service" "http://localhost:8080/api/logs/stats"
check_port "Frontend" 3000

echo ""
echo "Checking Docker Containers..."
if command -v docker &> /dev/null; then
    if docker ps | grep -q "soc"; then
        echo -e "${GREEN}✅${NC} Docker containers are running"
        docker ps --filter "name=soc" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        echo -e "${YELLOW}⚠️${NC}  No SOC containers found. Run 'docker-compose up' to start services."
    fi
else
    echo -e "${YELLOW}⚠️${NC}  Docker command not found"
fi

echo ""
echo "=================================="
echo "Check complete!"

