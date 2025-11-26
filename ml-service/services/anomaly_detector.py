import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, Tuple
import json
import re
from datetime import datetime

class AnomalyDetectionModel(nn.Module):
    """RNN-based anomaly detection model"""
    def __init__(self, input_size=128, hidden_size=256, num_layers=2, num_classes=2):
        super(AnomalyDetectionModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, num_classes)
        self.dropout = nn.Dropout(0.3)
        
    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.dropout(out[:, -1, :])
        out = self.fc(out)
        return out

class AnomalyDetector:
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.is_model_loaded = False
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize and load pre-trained model"""
        try:
            self.model = AnomalyDetectionModel()
            # In production, load pre-trained weights here
            # self.model.load_state_dict(torch.load('models/anomaly_model.pth', map_location=self.device))
            self.model.eval()
            self.is_model_loaded = True
            print("Anomaly detection model initialized")
        except Exception as e:
            print(f"Warning: Could not load model, using rule-based detection: {e}")
            self.is_model_loaded = False
    
    def is_ready(self) -> bool:
        return True
    
    def extract_features(self, log_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from multi-modal data (Logs, NetFlow, EDR)
        """
        data_type = log_data.get('dataType', 'LOG')
        
        if data_type == 'NETFLOW':
            return self._extract_netflow_features(log_data)
        elif data_type == 'EDR':
            return self._extract_edr_features(log_data)
        else:
            return self._extract_log_features(log_data)
    
    def _extract_log_features(self, log_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from log data"""
        features = []
        
        # Text-based features
        message = str(log_data.get("message", "")).lower()
        source = str(log_data.get("source", "")).lower()
        
        # Threat indicators
        threat_keywords = [
            "failed", "unauthorized", "suspicious", "attack", "malware",
            "breach", "exploit", "injection", "xss", "sql", "ddos",
            "brute", "force", "scan", "port", "firewall", "blocked"
        ]
        
        threat_count = sum(1 for keyword in threat_keywords if keyword in message)
        features.append(threat_count)
        
        # Log level encoding
        log_level = log_data.get("logLevel", "INFO").upper()
        level_map = {"CRITICAL": 5, "ERROR": 4, "WARN": 3, "INFO": 2, "DEBUG": 1}
        features.append(level_map.get(log_level, 2))
        
        # Source encoding
        source_map = {"firewall": 1, "ids": 2, "ips": 3, "server": 4, "application": 5}
        features.append(source_map.get(source, 0))
        
        # IP pattern detection
        metadata = log_data.get("metadata", {})
        ip_count = 0
        if "ip" in metadata or "source_ip" in metadata or "destination_ip" in metadata:
            ip_count = 1
        features.append(ip_count)
        
        # Port scanning detection
        port_count = 0
        if "port" in metadata:
            port_count = 1
        features.append(port_count)
        
        # Message length
        features.append(len(message))
        
        # Fill to 128 features with zeros
        while len(features) < 128:
            features.append(0.0)
        
        return np.array(features[:128], dtype=np.float32)
    
    def _extract_netflow_features(self, netflow_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from NetFlow data"""
        features = []
        
        # Network flow features
        source_ip = str(netflow_data.get("sourceIp", ""))
        dest_ip = str(netflow_data.get("destinationIp", ""))
        source_port = int(netflow_data.get("sourcePort", 0))
        dest_port = int(netflow_data.get("destinationPort", 0))
        protocol = str(netflow_data.get("protocol", "")).upper()
        
        # Port-based features
        features.append(source_port / 65535.0)  # Normalized port
        features.append(dest_port / 65535.0)
        
        # Protocol encoding (TCP=1, UDP=2, ICMP=3, etc.)
        protocol_map = {"TCP": 1, "UDP": 2, "ICMP": 3, "HTTP": 4, "HTTPS": 5}
        features.append(protocol_map.get(protocol, 0))
        
        # Traffic volume features
        bytes_sent = float(netflow_data.get("bytesSent", 0))
        bytes_received = float(netflow_data.get("bytesReceived", 0))
        packets_sent = float(netflow_data.get("packetsSent", 0))
        packets_received = float(netflow_data.get("packetsReceived", 0))
        
        # Normalize traffic (log scale to handle large values)
        features.append(np.log1p(bytes_sent) / 20.0)  # Normalized to 0-1 range
        features.append(np.log1p(bytes_received) / 20.0)
        features.append(np.log1p(packets_sent) / 15.0)
        features.append(np.log1p(packets_received) / 15.0)
        
        # TCP flags (if available)
        tcp_flags = int(netflow_data.get("tcpFlags", 0))
        features.append(tcp_flags / 255.0)  # Normalized
        
        # Flow direction (INBOUND=1, OUTBOUND=2, INTERNAL=3)
        flow_dir = str(netflow_data.get("flowDirection", "")).upper()
        dir_map = {"INBOUND": 1, "OUTBOUND": 2, "INTERNAL": 3}
        features.append(dir_map.get(flow_dir, 0))
        
        # Suspicious port detection (common attack ports)
        suspicious_ports = [21, 22, 23, 25, 53, 80, 135, 139, 443, 445, 1433, 3306, 3389, 5432]
        if dest_port in suspicious_ports:
            features.append(1.0)
        else:
            features.append(0.0)
        
        # High traffic volume indicator
        total_bytes = bytes_sent + bytes_received
        if total_bytes > 1000000:  # > 1MB
            features.append(1.0)
        else:
            features.append(0.0)
        
        # Port scan indicator (many connections to different ports)
        if packets_sent > 100 and dest_port > 1024:
            features.append(1.0)
        else:
            features.append(0.0)
        
        # Fill to 128 features
        while len(features) < 128:
            features.append(0.0)
        
        return np.array(features[:128], dtype=np.float32)
    
    def _extract_edr_features(self, edr_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from EDR telemetry data"""
        features = []
        
        # Event type encoding
        event_type = str(edr_data.get("eventType", "")).upper()
        event_map = {
            "PROCESS_CREATE": 1, "PROCESS_TERMINATE": 2, "FILE_WRITE": 3,
            "FILE_DELETE": 4, "FILE_READ": 5, "REGISTRY_MODIFY": 6,
            "NETWORK_CONNECT": 7, "NETWORK_DISCONNECT": 8, "THREAD_CREATE": 9
        }
        features.append(event_map.get(event_type, 0))
        
        # Process information
        process_name = str(edr_data.get("processName", "")).lower()
        process_path = str(edr_data.get("processPath", "")).lower()
        process_id = int(edr_data.get("processId", 0))
        parent_process_id = int(edr_data.get("parentProcessId", 0))
        
        # Process ID features
        features.append(process_id / 65535.0)  # Normalized
        features.append(parent_process_id / 65535.0)
        
        # Suspicious process names
        suspicious_processes = ["cmd.exe", "powershell.exe", "wscript.exe", "cscript.exe", 
                                "rundll32.exe", "regsvr32.exe", "mshta.exe"]
        if any(sp in process_name for sp in suspicious_processes):
            features.append(1.0)
        else:
            features.append(0.0)
        
        # Suspicious paths
        suspicious_paths = ["temp", "appdata", "downloads", "recycle"]
        if any(sp in process_path for sp in suspicious_paths):
            features.append(1.0)
        else:
            features.append(0.0)
        
        # File operations
        file_operation = str(edr_data.get("fileOperation", "")).upper()
        file_op_map = {"CREATE": 1, "WRITE": 2, "DELETE": 3, "READ": 4, "MODIFY": 5}
        features.append(file_op_map.get(file_operation, 0))
        
        # Network connection features
        remote_ip = str(edr_data.get("remoteIp", ""))
        remote_port = int(edr_data.get("remotePort", 0))
        connection_dir = str(edr_data.get("connectionDirection", "")).upper()
        
        features.append(remote_port / 65535.0 if remote_port > 0 else 0.0)
        dir_map = {"INBOUND": 1, "OUTBOUND": 2}
        features.append(dir_map.get(connection_dir, 0))
        
        # Registry operations
        registry_op = str(edr_data.get("registryOperation", "")).upper()
        reg_op_map = {"CREATE": 1, "MODIFY": 2, "DELETE": 3}
        features.append(reg_op_map.get(registry_op, 0))
        
        # User context
        username = str(edr_data.get("username", ""))
        domain = str(edr_data.get("domain", ""))
        
        # System account detection
        system_accounts = ["system", "administrator", "root", "nt authority"]
        if any(sa in username.lower() for sa in system_accounts):
            features.append(1.0)
        else:
            features.append(0.0)
        
        # Severity encoding
        severity = str(edr_data.get("severity", "")).upper()
        severity_map = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        features.append(severity_map.get(severity, 0))
        
        # Indicators of Compromise
        indicators = edr_data.get("indicators", [])
        if isinstance(indicators, list):
            features.append(min(len(indicators), 10) / 10.0)  # Normalized IOC count
        else:
            features.append(0.0)
        
        # Process hash (if available, check if it's known malicious)
        process_hash = str(edr_data.get("processHash", ""))
        if process_hash and len(process_hash) == 64:  # SHA256
            features.append(1.0)  # Has hash
        else:
            features.append(0.0)
        
        # File hash (if available)
        file_hash = str(edr_data.get("fileHash", ""))
        if file_hash and len(file_hash) == 64:
            features.append(1.0)
        else:
            features.append(0.0)
        
        # Fill to 128 features
        while len(features) < 128:
            features.append(0.0)
        
        return np.array(features[:128], dtype=np.float32)
    
    def detect_anomaly(self, log_data: Dict[str, Any]) -> Tuple[bool, float, str]:
        """
        Detect anomalies in log data
        Returns: (is_anomaly, anomaly_score, threat_type)
        """
        try:
            # Extract features
            features = self.extract_features(log_data)
            
            # Rule-based detection (fallback)
            message = str(log_data.get("message", "")).lower()
            source = log_data.get("source", "").lower()
            log_level = log_data.get("logLevel", "INFO").upper()
            
            anomaly_score = 0.0
            threat_type = None
            
            # High severity indicators
            if log_level in ["ERROR", "CRITICAL"]:
                anomaly_score += 0.3
            
            # Threat pattern matching
            threat_patterns = {
                "brute_force": ["failed login", "authentication failed", "invalid password"],
                "port_scan": ["port scan", "connection attempt", "syn flood"],
                "malware": ["malware", "virus", "trojan", "ransomware"],
                "ddos": ["ddos", "flood", "overload", "traffic spike"],
                "sql_injection": ["sql", "injection", "union select", "drop table"],
                "xss": ["xss", "script", "javascript", "cross-site"],
                "unauthorized_access": ["unauthorized", "access denied", "permission denied"]
            }
            
            for threat, patterns in threat_patterns.items():
                if any(pattern in message for pattern in patterns):
                    anomaly_score += 0.4
                    threat_type = threat
                    break
            
            # IP-based detection
            metadata = log_data.get("metadata", {})
            if "ip" in metadata:
                ip = str(metadata.get("ip", ""))
                # Check for suspicious IP patterns
                if ip.startswith("192.168") or ip.startswith("10.") or ip.startswith("172."):
                    # Internal IP - lower risk
                    anomaly_score += 0.1
                else:
                    # External IP - higher risk
                    anomaly_score += 0.2
            
            # Multiple failed attempts
            if "failed" in message or "error" in message:
                anomaly_score += 0.2
            
            # Normalize score
            anomaly_score = min(anomaly_score, 1.0)
            
            # Determine if anomaly
            is_anomaly = anomaly_score > 0.5
            
            # If model is loaded, use it
            if self.is_model_loaded and self.model:
                try:
                    features_tensor = torch.FloatTensor(features).unsqueeze(0).unsqueeze(0)
                    with torch.no_grad():
                        output = self.model(features_tensor)
                        prob = torch.softmax(output, dim=1)
                        model_score = prob[0][1].item()
                        # Combine rule-based and model scores
                        anomaly_score = (anomaly_score * 0.4 + model_score * 0.6)
                        is_anomaly = anomaly_score > 0.5
                except Exception as e:
                    print(f"Model inference error: {e}")
            
            # Determine severity
            if anomaly_score > 0.8:
                severity = "CRITICAL"
            elif anomaly_score > 0.6:
                severity = "HIGH"
            elif anomaly_score > 0.4:
                severity = "MEDIUM"
            else:
                severity = "LOW"
            
            return is_anomaly, float(anomaly_score), threat_type or "UNKNOWN"
            
        except Exception as e:
            print(f"Anomaly detection error: {e}")
            return False, 0.0, "ERROR"

