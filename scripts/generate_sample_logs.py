#!/usr/bin/env python3
"""
Sample log generator for testing the SOC system
"""
import requests
import json
import random
from datetime import datetime, timedelta
import time

INGESTION_URL = "http://localhost:8080/api/logs/ingest"

THREAT_TYPES = [
    "brute_force",
    "port_scan",
    "sql_injection",
    "xss",
    "ddos",
    "malware",
    "unauthorized_access"
]

SOURCES = ["firewall", "ids", "ips", "server", "application"]
LOG_LEVELS = ["INFO", "WARN", "ERROR", "CRITICAL"]

THREAT_MESSAGES = {
    "brute_force": [
        "Multiple failed login attempts detected from IP",
        "Authentication failed: Invalid credentials",
        "Brute force attack detected on user account",
        "Repeated login failures from source"
    ],
    "port_scan": [
        "Port scan detected from source IP",
        "Multiple connection attempts to closed ports",
        "Suspicious port scanning activity",
        "Network scan detected on multiple ports"
    ],
    "sql_injection": [
        "Potential SQL injection attempt detected",
        "Malicious SQL query pattern identified",
        "SQL injection attack blocked",
        "Suspicious database query detected"
    ],
    "xss": [
        "Cross-site scripting (XSS) attempt detected",
        "Malicious script injection blocked",
        "XSS attack pattern identified in request",
        "Suspicious JavaScript code detected"
    ],
    "ddos": [
        "DDoS attack detected - high traffic volume",
        "Traffic spike detected from multiple sources",
        "Distributed denial of service attack in progress",
        "Network overload - potential DDoS"
    ],
    "malware": [
        "Malware signature detected in file",
        "Suspicious file download blocked",
        "Malicious code execution attempt",
        "Virus detected in uploaded file"
    ],
    "unauthorized_access": [
        "Unauthorized access attempt detected",
        "Access denied: Insufficient permissions",
        "Privilege escalation attempt blocked",
        "Unauthorized file access attempt"
    ]
}

def generate_ip():
    """Generate a random IP address"""
    if random.random() < 0.3:  # 30% chance of internal IP
        return f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
    else:
        return f"{random.randint(1, 223)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

def generate_log(threat_type=None):
    """Generate a sample security log"""
    if threat_type is None:
        threat_type = random.choice(THREAT_TYPES) if random.random() < 0.4 else None
    
    source = random.choice(SOURCES)
    log_level = random.choice(LOG_LEVELS)
    
    if threat_type:
        message = random.choice(THREAT_MESSAGES[threat_type])
        source_ip = generate_ip()
        metadata = {
            "ip": source_ip,
            "port": random.randint(1024, 65535) if threat_type == "port_scan" else None,
            "protocol": random.choice(["TCP", "UDP", "HTTPS", "HTTP"])
        }
    else:
        message = f"Normal {source} activity"
        metadata = {}
    
    log = {
        "source": source,
        "timestamp": (datetime.now() - timedelta(seconds=random.randint(0, 3600))).isoformat(),
        "logLevel": log_level,
        "message": message,
        "metadata": {k: v for k, v in metadata.items() if v is not None},
        "rawLog": json.dumps({
            "source": source,
            "level": log_level,
            "message": message,
            "metadata": metadata
        })
    }
    
    return log

def send_log(log):
    """Send log to ingestion service"""
    try:
        response = requests.post(INGESTION_URL, json=log, timeout=5)
        if response.status_code == 201:
            print(f"✓ Sent log: {log['message'][:50]}...")
            return True
        else:
            print(f"✗ Failed to send log: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error sending log: {e}")
        return False

def main():
    """Main function to generate and send sample logs"""
    print("=" * 60)
    print("SOC Sample Log Generator")
    print("=" * 60)
    print(f"Sending logs to: {INGESTION_URL}")
    print("Press Ctrl+C to stop\n")
    
    count = 0
    try:
        while True:
            # Generate 1-3 logs per iteration
            num_logs = random.randint(1, 3)
            for _ in range(num_logs):
                log = generate_log()
                if send_log(log):
                    count += 1
                time.sleep(0.5)  # Small delay between logs
            
            # Wait before next batch
            wait_time = random.randint(2, 5)
            print(f"Total logs sent: {count}. Waiting {wait_time}s...\n")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print(f"\n\nStopped. Total logs sent: {count}")

if __name__ == "__main__":
    main()

