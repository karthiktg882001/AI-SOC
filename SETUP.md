# Setup Guide

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker** (version 20.10+) and **Docker Compose** (version 2.0+)
- **Java 17+** (for local development of log ingestion service)
- **Python 3.9+** (for local development of ML service)
- **Node.js 18+** and **npm** (for local development of frontend)

## Quick Start with Docker

### 1. Start All Services

```bash
docker-compose up --build
```

This will start:
- Zookeeper and Kafka (message streaming)
- MongoDB (log storage)
- PostgreSQL (incident storage)
- Log Ingestion Service (Spring Boot)
- ML Service (FastAPI)
- Frontend (React)

### 2. Access the Application

- **Frontend Dashboard**: http://localhost:3000
- **ML Service API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Log Ingestion API**: http://localhost:8080

### 3. Generate Sample Data

In a new terminal:

```bash
# Install Python dependencies
pip install requests

# Run sample log generator
python scripts/generate_sample_logs.py
```

## Manual Setup (Without Docker)

### 1. Start Infrastructure Services

```bash
# Start Kafka and Zookeeper
docker-compose up -d zookeeper kafka

# Start Databases
docker-compose up -d mongodb postgres
```

### 2. Start Log Ingestion Service

```bash
cd log-ingestion-service
./mvnw spring-boot:run
```

Or with Maven:
```bash
mvn clean install
mvn spring-boot:run
```

### 3. Start ML Service

```bash
cd ml-service
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### 4. Start Frontend

```bash
cd frontend
npm install
npm start
```

## Configuration

### Environment Variables

Create `.env` files in respective service directories if needed:

**log-ingestion-service/.env:**
```
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
MONGODB_URI=mongodb://localhost:27017/soc_logs
```

**ml-service/.env:**
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=soc_user
POSTGRES_PASSWORD=soc_password
POSTGRES_DB=soc_db
MONGODB_URI=mongodb://localhost:27017/soc_logs
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

## Testing

### Test API Endpoints

```bash
chmod +x scripts/test_api.sh
./scripts/test_api.sh
```

### Manual API Testing

**Ingest a log:**
```bash
curl -X POST http://localhost:8080/api/logs/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source": "firewall",
    "timestamp": "2024-01-15T10:30:00",
    "logLevel": "WARN",
    "message": "Suspicious connection attempt",
    "metadata": {
      "ip": "192.168.1.100",
      "port": 443
    }
  }'
```

**Detect anomaly:**
```bash
curl -X POST http://localhost:8000/api/detect/anomaly \
  -H "Content-Type: application/json" \
  -d '{
    "logData": {
      "source": "firewall",
      "logLevel": "ERROR",
      "message": "Multiple failed login attempts"
    }
  }'
```

**Get dashboard stats:**
```bash
curl http://localhost:8000/api/dashboard/stats
```

## Troubleshooting

### Kafka Connection Issues

If Kafka is not available, the ML service will continue to work but won't process real-time logs from Kafka. Check Kafka status:

```bash
docker-compose ps kafka
```

### Database Connection Issues

Ensure databases are running:
```bash
docker-compose ps mongodb postgres
```

Check connection strings in environment variables.

### Port Conflicts

If ports are already in use, modify `docker-compose.yml` to use different ports.

### Frontend Not Loading

Ensure the ML service is running and accessible at the configured API URL.

## Development

### Adding New Threat Types

Edit `ml-service/services/anomaly_detector.py` to add new threat detection patterns.

### Customizing AI Reports

Modify `ml-service/services/generative_ai.py` to customize report generation.

### Frontend Customization

Edit React components in `frontend/src/components/` to customize the UI.

## Production Deployment

For production deployment:

1. Use environment-specific configuration files
2. Enable SSL/TLS for all services
3. Set up proper authentication and authorization
4. Configure monitoring and logging
5. Use managed database services
6. Set up CI/CD pipelines
7. Configure auto-scaling for services

## Support

For issues or questions, please refer to the main README.md or create an issue in the repository.

