-- Create incidents table
CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(255) UNIQUE,
    log_id VARCHAR(255),
    severity VARCHAR(50),
    status VARCHAR(50) DEFAULT 'OPEN',
    threat_type VARCHAR(100),
    source_ip VARCHAR(50),
    destination_ip VARCHAR(50),
    timestamp TIMESTAMP,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    anomaly_score FLOAT,
    description TEXT,
    raw_log_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create incident_reports table
CREATE TABLE IF NOT EXISTS incident_reports (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(255),
    summary TEXT,
    detailed_analysis TEXT,
    mitigation_steps JSONB,
    mitigation_script TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create threat_intelligence table
CREATE TABLE IF NOT EXISTS threat_intelligence (
    id SERIAL PRIMARY KEY,
    threat_hash VARCHAR(255) UNIQUE,
    threat_type VARCHAR(100),
    ioc_type VARCHAR(50),
    ioc_value TEXT,
    severity VARCHAR(50),
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    detection_count INTEGER DEFAULT 1,
    additional_info JSONB
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255)
);

-- Create password_reset_tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    token VARCHAR(255) UNIQUE,
    expires_at TIMESTAMP,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create system_info table
CREATE TABLE IF NOT EXISTS system_info (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    device_id VARCHAR(255),
    platform VARCHAR(50),
    os_version VARCHAR(100),
    cpu_info JSONB,
    memory_info JSONB,
    network_info JSONB,
    disk_info JSONB,
    processes JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_incidents_incident_id ON incidents(incident_id);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_detected_at ON incidents(detected_at);
CREATE INDEX IF NOT EXISTS idx_incident_reports_incident_id ON incident_reports(incident_id);
CREATE INDEX IF NOT EXISTS idx_threat_intelligence_hash ON threat_intelligence(threat_hash);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_email ON password_reset_tokens(email);
CREATE INDEX IF NOT EXISTS idx_system_info_user_id ON system_info(user_id);
CREATE INDEX IF NOT EXISTS idx_system_info_device_id ON system_info(device_id);
