# AI-Driven Security Operations Center (SOC) Assistant

A comprehensive AI-powered Security Operations Center platform that leverages Deep Learning and Generative AI to automate security log analysis, detect zero-day threat patterns, and generate instant mitigation responses.

## Features

- **Automated Multi-Source Log Ingestion**: High-throughput log collection using Kafka and Spring Boot
- **AI-Powered Anomaly Detection**: Deep Learning models (RNN/Transformer) for zero-day attack detection
- **Generative Incident Reports**: AI-generated summaries and actionable mitigation scripts
- **Interactive Security Dashboard**: Real-time visualization and monitoring
- **Real-time Processing**: Kafka-based event streaming for low-latency threat detection

## Architecture

```
┌─────────────────┐
│   Frontend      │  React Dashboard (Port 3000)
│   (React)       │
└────────┬────────┘
         │
┌────────▼────────┐
│   ML Service    │  FastAPI + PyTorch (Port 8000)
│   (Python)      │
└────────┬────────┘
         │
┌────────▼────────┐
│ Log Ingestion   │  Spring Boot (Port 8080)
│   (Java)        │
└────────┬────────┘
         │
    ┌────┴────┐
    │  Kafka  │
    └────┬────┘
         │
    ┌────┴────┬──────────┐
    │         │          │
┌───▼───┐ ┌──▼───┐ ┌────▼────┐
│MongoDB│ │PostgreSQL│ │  Zookeeper│
└───────┘ └─────────┘ └──────────┘
```

## Prerequisites

- Docker and Docker Compose
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for initial setup)

## Quick Start

**🚀 For the fastest setup, see [QUICKSTART.md](QUICKSTART.md)**

### Using Docker Compose (Recommended)

1. Navigate to the project directory:
```bash
cd AISOC
```

2. Start all services:
```bash
docker-compose up --build
```

Or use Make:
```bash
make build
make up
```

3. Access the application:
   - **Web Application**: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   
   The application is accessible from any device on your network:
   - Desktop computers
   - Mobile phones (iOS, Android)
   - Tablets
   - Any device with a web browser
   
   To access from other devices, use: `http://YOUR_IP_ADDRESS:3000`

### Access from Mobile/Other Devices

1. Find your computer's IP address:
   - Windows: Run `ipconfig` and look for IPv4 Address
   - Linux/Mac: Run `ifconfig` or `ip addr`

2. Access from any device:
   - Open web browser
   - Navigate to: `http://YOUR_IP_ADDRESS:3000`
   - Example: `http://192.168.1.100:3000`

The application is fully responsive and works on all devices!

## API Endpoints

### Log Ingestion Service (Port 8080)
- `POST /api/logs/ingest` - Ingest security logs
- `GET /api/logs` - Retrieve logs
- `GET /api/logs/stats` - Get ingestion statistics

### ML Service (Port 8000)
- `POST /api/detect/anomaly` - Detect anomalies in logs
- `GET /api/incidents` - Get all security incidents
- `GET /api/incidents/{id}` - Get incident details
- `POST /api/incidents/{id}/generate-report` - Generate AI report
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/threats/recent` - Get recent threats

## Project Structure

```
AISOC/
├── log-ingestion-service/    # Spring Boot service for log ingestion
├── ml-service/               # Python FastAPI service for ML/AI
├── frontend/                 # React dashboard
├── database/                 # Database initialization scripts
└── docker-compose.yml        # Docker orchestration
```

## Configuration

### Environment Variables

**Log Ingestion Service:**
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address
- `MONGODB_URI`: MongoDB connection string

**ML Service:**
- `POSTGRES_HOST`: PostgreSQL host
- `POSTGRES_DB`: Database name
- `MONGODB_URI`: MongoDB connection string
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address

## Model Training

The anomaly detection models are pre-trained and included. To retrain:

```bash
cd ml-service
python train_models.py
```

## Testing

### Test Log Ingestion
```bash
curl -X POST http://localhost:8080/api/logs/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source": "firewall",
    "timestamp": "2024-01-15T10:30:00Z",
    "logLevel": "WARN",
    "message": "Suspicious connection attempt from 192.168.1.100",
    "metadata": {
      "ip": "192.168.1.100",
      "port": 443,
      "protocol": "HTTPS"
    }
  }'
```

### Test Anomaly Detection
```bash
curl -X POST http://localhost:8000/api/detect/anomaly \
  -H "Content-Type: application/json" \
  -d '{
    "logId": "12345",
    "logData": {
      "source": "firewall",
      "message": "Multiple failed login attempts detected"
    }
  }'
```

## Future Enhancements

- Integration with SIEM tools (Splunk/Elastic Stack)
- Reinforcement learning for adaptive threat response
- Multilingual reporting via expanded LLM
- Cloud-native SaaS deployment
- Real-time alerting and notification system

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

