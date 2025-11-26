# Project Structure

```
AISOC/
├── docker-compose.yml              # Docker orchestration for all services
├── README.md                       # Main project documentation
├── SETUP.md                        # Detailed setup instructions
├── .gitignore                      # Git ignore rules
│
├── database/                       # Database initialization
│   └── init.sql                    # PostgreSQL schema initialization
│
├── log-ingestion-service/          # Spring Boot Log Ingestion Service
│   ├── pom.xml                     # Maven dependencies
│   ├── Dockerfile                  # Docker build configuration
│   ├── .dockerignore              # Docker ignore rules
│   └── src/
│       └── main/
│           ├── java/com/soc/ingestion/
│           │   ├── LogIngestionServiceApplication.java
│           │   ├── controller/
│           │   │   └── LogIngestionController.java
│           │   ├── service/
│           │   │   └── LogIngestionService.java
│           │   ├── repository/
│           │   │   └── LogRepository.java
│           │   ├── model/
│           │   │   └── SecurityLog.java
│           │   └── dto/
│           │       └── LogIngestionRequest.java
│           └── resources/
│               └── application.yml
│
├── ml-service/                      # Python ML/AI Service
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Docker build configuration
│   ├── .dockerignore              # Docker ignore rules
│   ├── main.py                     # FastAPI application entry point
│   ├── database.py                 # Database connection and setup
│   ├── models.py                   # SQLAlchemy models
│   ├── routers/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── incidents.py           # Incident management endpoints
│   │   ├── dashboard.py           # Dashboard statistics endpoints
│   │   └── detection.py           # Anomaly detection endpoints
│   └── services/                   # Core business logic
│       ├── __init__.py
│       ├── anomaly_detector.py    # Deep learning anomaly detection
│       ├── generative_ai.py      # AI report generation
│       └── kafka_consumer.py      # Real-time log processing
│
├── frontend/                        # React Frontend Dashboard
│   ├── package.json               # Node.js dependencies
│   ├── Dockerfile                 # Docker build configuration
│   ├── .dockerignore             # Docker ignore rules
│   ├── nginx.conf                # Nginx configuration
│   ├── public/
│   │   └── index.html            # HTML template
│   └── src/
│       ├── index.js              # React entry point
│       ├── index.css             # Global styles
│       ├── App.js                # Main app component
│       ├── App.css               # App styles
│       └── components/           # React components
│           ├── Navbar.js         # Navigation bar
│           ├── Navbar.css
│           ├── Dashboard.js      # Main dashboard
│           ├── Dashboard.css
│           ├── Incidents.js      # Incidents list
│           ├── Incidents.css
│           ├── IncidentDetail.js # Incident details view
│           └── IncidentDetail.css
│
└── scripts/                        # Utility scripts
    ├── generate_sample_logs.py    # Sample log generator
    └── test_api.sh                # API testing script
```

## Service Architecture

### 1. Log Ingestion Service (Java/Spring Boot)
- **Port**: 8080
- **Technology**: Spring Boot, Kafka, MongoDB
- **Purpose**: High-throughput log ingestion and storage
- **Key Features**:
  - REST API for log ingestion
  - Kafka producer for real-time streaming
  - MongoDB for log storage
  - Log retrieval and statistics

### 2. ML Service (Python/FastAPI)
- **Port**: 8000
- **Technology**: FastAPI, PyTorch, PostgreSQL, Kafka
- **Purpose**: AI-powered threat detection and analysis
- **Key Features**:
  - Anomaly detection using deep learning
  - Generative AI for incident reports
  - Kafka consumer for real-time processing
  - PostgreSQL for incident storage
  - REST API for all ML operations

### 3. Frontend (React)
- **Port**: 3000
- **Technology**: React, Recharts, Axios
- **Purpose**: Interactive security dashboard
- **Key Features**:
  - Real-time dashboard with statistics
  - Incident management interface
  - Threat visualization
  - AI-generated report viewing

### 4. Infrastructure Services
- **Kafka**: Message streaming (Port 9092)
- **Zookeeper**: Kafka coordination (Port 2181)
- **MongoDB**: Log storage (Port 27017)
- **PostgreSQL**: Incident storage (Port 5432)

## Data Flow

```
Security Logs
    ↓
Log Ingestion Service (Spring Boot)
    ↓
Kafka Topic: security-logs
    ↓
ML Service Kafka Consumer
    ↓
Anomaly Detection Engine
    ↓
PostgreSQL (Incidents)
    ↓
Frontend Dashboard
```

## API Endpoints

### Log Ingestion Service
- `POST /api/logs/ingest` - Ingest security logs
- `GET /api/logs` - Retrieve logs
- `GET /api/logs/stats` - Get statistics

### ML Service
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/threats/recent` - Recent threats
- `GET /api/incidents` - List incidents
- `GET /api/incidents/{id}` - Get incident details
- `POST /api/incidents/{id}/generate-report` - Generate AI report
- `POST /api/detect/anomaly` - Detect anomalies

## Key Technologies

- **Backend**: Spring Boot, FastAPI
- **Frontend**: React, Recharts
- **Databases**: MongoDB, PostgreSQL
- **Message Queue**: Apache Kafka
- **ML/AI**: PyTorch, Transformers
- **Containerization**: Docker, Docker Compose

