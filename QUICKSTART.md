# Quick Start Guide

Get the AI-Driven SOC Assistant up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB of free RAM
- Ports 3000, 8000, 8080, 9092, 27017, 5432 available

## Step 1: Start All Services

```bash
# Using Docker Compose
docker-compose up --build

# Or using Make (if available)
make build
make up
```

This will start:
- ✅ Kafka & Zookeeper (message streaming)
- ✅ MongoDB (log storage)
- ✅ PostgreSQL (incident storage)
- ✅ Log Ingestion Service (port 8080)
- ✅ ML Service (port 8000)
- ✅ Frontend Dashboard (port 3000)

## Step 2: Access the Dashboard

Open your browser and navigate to:
**http://localhost:3000**

You should see the Security Operations Dashboard!

## Step 3: Generate Sample Data

In a new terminal window:

```bash
# Install Python requests if needed
pip install requests

# Generate sample security logs
python scripts/generate_sample_logs.py
```

Watch as incidents appear in real-time on the dashboard!

## Step 4: Explore Features

### View Dashboard
- Navigate to http://localhost:3000
- See real-time statistics and threat visualizations

### View Incidents
- Click on "Incidents" in the navigation
- Filter by status or severity
- Click any incident to see details

### Generate AI Report
- Open an incident detail page
- Click "Generate AI Report"
- View AI-generated summary, analysis, and mitigation steps

## API Testing

Test the APIs directly:

```bash
# Health check
curl http://localhost:8000/health

# Dashboard stats
curl http://localhost:8000/api/dashboard/stats

# Ingest a log
curl -X POST http://localhost:8080/api/logs/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source": "firewall",
    "timestamp": "2024-01-15T10:30:00",
    "logLevel": "WARN",
    "message": "Suspicious connection attempt",
    "metadata": {"ip": "192.168.1.100"}
  }'
```

## Troubleshooting

### Services won't start
```bash
# Check if ports are in use
netstat -an | grep -E '3000|8000|8080|9092'

# Check Docker logs
docker-compose logs
```

### Frontend not loading
- Ensure ML service is running: `curl http://localhost:8000/health`
- Check browser console for errors
- Verify API URL in frontend configuration

### No incidents appearing
- Check if logs are being ingested: `curl http://localhost:8080/api/logs/stats`
- Verify Kafka is running: `docker-compose ps kafka`
- Check ML service logs: `docker-compose logs ml-service`

## Next Steps

- Read [SETUP.md](SETUP.md) for detailed configuration
- Read [README.md](README.md) for full documentation
- Check [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture details

## Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v
```

Enjoy your AI-Driven SOC Assistant! 🛡️

