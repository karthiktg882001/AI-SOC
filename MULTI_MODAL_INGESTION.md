# Multi-Modal Data Ingestion Implementation

## Overview
The AI-Driven SOC Assistant now supports multi-modal data ingestion, allowing the system to process three different types of security data:
1. **Security Logs** (existing)
2. **NetFlow Records** (network flow data)
3. **EDR Telemetry** (endpoint detection and response data)

## Architecture

### Data Types

#### 1. Security Logs
- **Source**: Firewalls, IDS/IPS, servers, applications
- **Data**: Log messages, log levels, metadata
- **Endpoint**: `POST /api/ingestion/log`

#### 2. NetFlow Records
- **Source**: Network devices, routers, switches
- **Data**: Source/destination IPs, ports, protocols, traffic statistics
- **Endpoint**: `POST /api/ingestion/netflow`
- **Features**:
  - Source and destination IP addresses
  - Port numbers and protocol (TCP, UDP, ICMP)
  - Traffic volume (bytes, packets)
  - TCP flags
  - Flow direction (INBOUND, OUTBOUND, INTERNAL)

#### 3. EDR Telemetry
- **Source**: Endpoint agents, EDR solutions
- **Data**: Process activity, file operations, registry changes, network connections
- **Endpoint**: `POST /api/ingestion/edr`
- **Features**:
  - Process creation/termination
  - File operations (create, write, delete, read)
  - Registry modifications
  - Network connections
  - User context
  - Indicators of Compromise (IOCs)

## Implementation Details

### Backend Components

#### 1. DTOs (Data Transfer Objects)
- `LogIngestionRequest.java` - Security log ingestion
- `NetFlowRequest.java` - NetFlow record ingestion
- `EDRTelemetryRequest.java` - EDR telemetry ingestion

#### 2. MongoDB Models
- `SecurityLog.java` - Stores security logs
- `NetFlowRecord.java` - Stores NetFlow records
- `EDRTelemetry.java` - Stores EDR telemetry

#### 3. Repositories
- `LogRepository.java` - MongoDB repository for logs
- `NetFlowRepository.java` - MongoDB repository for NetFlow
- `EDRTelemetryRepository.java` - MongoDB repository for EDR

#### 4. Services
- `MultiModalIngestionService.java` - Unified ingestion service handling all data types
  - Routes data to appropriate repository
  - Publishes to Kafka topics (security-logs, netflow-records, edr-telemetry)
  - Triggers ML detection with data type identifier

#### 5. Controller
- `MultiModalIngestionController.java` - REST API endpoints
  - `POST /api/ingestion/log` - Ingest security log
  - `POST /api/ingestion/netflow` - Ingest NetFlow record
  - `POST /api/ingestion/edr` - Ingest EDR telemetry
  - `GET /api/ingestion/stats` - Get ingestion statistics

### ML Service Enhancements

#### Feature Extraction
The `AnomalyDetector` class now includes multi-modal feature extraction:

1. **`_extract_log_features()`** - Extracts features from security logs
   - Threat keywords
   - Log levels
   - Source types
   - IP and port patterns

2. **`_extract_netflow_features()`** - Extracts features from NetFlow data
   - Port numbers (normalized)
   - Protocol encoding
   - Traffic volume (bytes, packets)
   - TCP flags
   - Flow direction
   - Suspicious port detection
   - High traffic indicators

3. **`_extract_edr_features()`** - Extracts features from EDR telemetry
   - Event type encoding
   - Process information
   - File operations
   - Network connections
   - Registry operations
   - User context
   - Severity levels
   - Indicators of Compromise

All feature vectors are normalized to 128 dimensions for consistent ML model input.

## Usage Examples

### Ingest Security Log
```bash
curl -X POST http://localhost:8080/api/ingestion/log \
  -H "Content-Type: application/json" \
  -d '{
    "source": "firewall",
    "timestamp": "2024-01-15T10:30:00",
    "logLevel": "WARN",
    "message": "Unauthorized access attempt detected",
    "metadata": {
      "source_ip": "192.168.1.100",
      "destination_ip": "10.0.0.1"
    }
  }'
```

### Ingest NetFlow Record
```bash
curl -X POST http://localhost:8080/api/ingestion/netflow \
  -H "Content-Type: application/json" \
  -d '{
    "sourceIp": "192.168.1.100",
    "destinationIp": "10.0.0.1",
    "sourcePort": 54321,
    "destinationPort": 443,
    "protocol": "TCP",
    "timestamp": "2024-01-15T10:30:00",
    "bytesSent": 1024,
    "bytesReceived": 2048,
    "packetsSent": 10,
    "packetsReceived": 15,
    "flowDirection": "OUTBOUND"
  }'
```

### Ingest EDR Telemetry
```bash
curl -X POST http://localhost:8080/api/ingestion/edr \
  -H "Content-Type: application/json" \
  -d '{
    "endpointId": "endpoint-001",
    "hostname": "workstation-01",
    "timestamp": "2024-01-15T10:30:00",
    "eventType": "PROCESS_CREATE",
    "processName": "powershell.exe",
    "processPath": "C:\\Windows\\System32\\powershell.exe",
    "processId": 1234,
    "parentProcessId": 5678,
    "username": "user1",
    "domain": "CORP",
    "severity": "HIGH"
  }'
```

## Benefits

1. **Comprehensive Threat Detection**: By combining log, network, and endpoint data, the system can detect multi-stage attacks that span different layers.

2. **Richer Context**: Each data type provides unique insights:
   - Logs: High-level security events
   - NetFlow: Network traffic patterns
   - EDR: Endpoint-level activity

3. **Unified Processing**: All data types flow through the same ML pipeline, enabling cross-modal anomaly detection.

4. **Scalable Architecture**: Each data type has its own Kafka topic and MongoDB collection, allowing independent scaling.

## Database Schema

### MongoDB Collections
- `security_logs` - Security log entries
- `netflow_records` - NetFlow records
- `edr_telemetry` - EDR telemetry entries

### Kafka Topics
- `security-logs` - Security log messages
- `netflow-records` - NetFlow records
- `edr-telemetry` - EDR telemetry messages

## Future Enhancements

1. **Correlation Engine**: Cross-reference events across data types to identify attack chains
2. **Time-Window Analysis**: Analyze patterns across multiple data types within time windows
3. **Graph Relationships**: Use Neo4j to map relationships between entities across data types
4. **Real-time Dashboards**: Visualize multi-modal data in unified dashboards
5. **Advanced ML Models**: Train specialized models for each data type while maintaining cross-modal capabilities

