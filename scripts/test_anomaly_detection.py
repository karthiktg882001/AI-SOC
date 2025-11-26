#!/usr/bin/env python3
"""
Test Anomaly Detection Script
Generates various types of security threats to test the AI SOC Assistant
"""
import requests
import json
import time
from datetime import datetime
import random

API_URL = "http://localhost:8080/api/logs/ingest"

def send_log(log_data):
    """Send a log to the ingestion service"""
    try:
        response = requests.post(API_URL, json=log_data)
        if response.status_code in [200, 201]:
            print(f"✅ Sent: {log_data.get('message', '')[:50]}...")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_malware_detection():
    """Test malware detection"""
    print("\n🦠 Testing Malware Detection...")
    logs = [
        {
            "source": "antivirus",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "CRITICAL",
            "message": "Malware detected: Trojan.Win32.Backdoor detected in C:\\Windows\\System32\\suspicious.exe",
            "metadata": {
                "ip": "192.168.1.50",
                "file_path": "C:\\Windows\\System32\\suspicious.exe",
                "process_id": "1234",
                "threat_name": "Trojan.Win32.Backdoor"
            }
        },
        {
            "source": "antivirus",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "ERROR",
            "message": "Virus infection detected: W32.Blaster.Worm found in network share",
            "metadata": {
                "ip": "10.0.0.25",
                "file_path": "\\\\server\\share\\infected.exe",
                "threat_name": "W32.Blaster.Worm"
            }
        }
    ]
    for log in logs:
        send_log(log)
        time.sleep(1)

def test_port_intrusion():
    """Test port intrusion detection"""
    print("\n🔍 Testing Port Intrusion Detection...")
    logs = [
        {
            "source": "firewall",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "WARN",
            "message": "Port scan detected from 203.0.113.45 - scanning ports 22, 80, 443, 3389",
            "metadata": {
                "ip": "203.0.113.45",
                "source_ip": "203.0.113.45",
                "port": "22",
                "protocol": "TCP",
                "scan_type": "stealth_scan"
            }
        },
        {
            "source": "firewall",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "ERROR",
            "message": "Unauthorized port access attempt on port 3389 (RDP) from external IP 198.51.100.10",
            "metadata": {
                "ip": "198.51.100.10",
                "source_ip": "198.51.100.10",
                "port": "3389",
                "protocol": "TCP",
                "service": "RDP"
            }
        },
        {
            "source": "ids",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "WARN",
            "message": "Network reconnaissance detected: Host discovery and port enumeration from 192.0.2.100",
            "metadata": {
                "ip": "192.0.2.100",
                "source_ip": "192.0.2.100",
                "scan_type": "network_scanning",
                "ports_scanned": "100+"
            }
        }
    ]
    for log in logs:
        send_log(log)
        time.sleep(1)

def test_brute_force():
    """Test brute force attack detection"""
    print("\n🔨 Testing Brute Force Attack Detection...")
    logs = [
        {
            "source": "application",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "ERROR",
            "message": "Multiple failed login attempts detected for user admin from IP 172.16.0.50 - 15 failed attempts in 5 minutes",
            "metadata": {
                "ip": "172.16.0.50",
                "source_ip": "172.16.0.50",
                "username": "admin",
                "failed_attempts": 15,
                "time_window": "5 minutes"
            }
        },
        {
            "source": "application",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "CRITICAL",
            "message": "Brute force attack in progress: 50+ failed authentication attempts from 10.0.0.100",
            "metadata": {
                "ip": "10.0.0.100",
                "source_ip": "10.0.0.100",
                "attack_type": "brute_force",
                "attempts": 50
            }
        }
    ]
    for log in logs:
        send_log(log)
        time.sleep(1)

def test_ddos():
    """Test DDoS attack detection"""
    print("\n💥 Testing DDoS Attack Detection...")
    logs = [
        {
            "source": "firewall",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "CRITICAL",
            "message": "DDoS attack detected: SYN flood from multiple IPs targeting port 80 - 10,000+ requests/second",
            "metadata": {
                "ip": "203.0.113.0/24",
                "source_ip": "203.0.113.1",
                "port": "80",
                "attack_type": "syn_flood",
                "requests_per_second": 10000
            }
        },
        {
            "source": "ids",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "ERROR",
            "message": "Distributed Denial of Service attack: HTTP flood from botnet - traffic spike 500% above normal",
            "metadata": {
                "ip": "multiple",
                "attack_type": "http_flood",
                "traffic_spike": "500%"
            }
        }
    ]
    for log in logs:
        send_log(log)
        time.sleep(1)

def test_sql_injection():
    """Test SQL injection detection"""
    print("\n💉 Testing SQL Injection Detection...")
    logs = [
        {
            "source": "application",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "ERROR",
            "message": "SQL injection attempt detected: UNION SELECT attack from 192.168.1.200 on endpoint /api/users",
            "metadata": {
                "ip": "192.168.1.200",
                "source_ip": "192.168.1.200",
                "endpoint": "/api/users",
                "attack_pattern": "UNION SELECT",
                "query": "SELECT * FROM users UNION SELECT * FROM passwords"
            }
        },
        {
            "source": "waf",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "WARN",
            "message": "SQL injection pattern detected: DROP TABLE command in user input from 10.0.0.75",
            "metadata": {
                "ip": "10.0.0.75",
                "source_ip": "10.0.0.75",
                "attack_pattern": "DROP TABLE",
                "endpoint": "/api/data"
            }
        }
    ]
    for log in logs:
        send_log(log)
        time.sleep(1)

def test_ransomware():
    """Test ransomware detection"""
    print("\n🔒 Testing Ransomware Detection...")
    logs = [
        {
            "source": "file_system",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "CRITICAL",
            "message": "Ransomware activity detected: Multiple files encrypted with .locky extension - ransom note found",
            "metadata": {
                "ip": "192.168.1.150",
                "file_path": "C:\\Users\\Documents\\",
                "encrypted_files": 500,
                "extension": ".locky",
                "ransom_amount": "0.5 BTC"
            }
        },
        {
            "source": "antivirus",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "CRITICAL",
            "message": "Crypto-ransomware detected: WannaCry variant encrypting files - payment demanded in Bitcoin",
            "metadata": {
                "ip": "192.168.1.150",
                "threat_name": "WannaCry",
                "encryption_type": "AES-256",
                "payment_method": "Bitcoin"
            }
        }
    ]
    for log in logs:
        send_log(log)
        time.sleep(1)

def test_data_exfiltration():
    """Test data exfiltration detection"""
    print("\n📤 Testing Data Exfiltration Detection...")
    logs = [
        {
            "source": "network",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "ERROR",
            "message": "Large data transfer detected: 50GB of sensitive data uploaded to external server 198.51.100.50",
            "metadata": {
                "ip": "198.51.100.50",
                "source_ip": "192.168.1.100",
                "data_size": "50GB",
                "data_type": "sensitive",
                "destination": "external_server"
            }
        },
        {
            "source": "ids",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "WARN",
            "message": "Unauthorized bulk download detected: Database export to unknown external IP 203.0.113.200",
            "metadata": {
                "ip": "203.0.113.200",
                "source_ip": "10.0.0.50",
                "data_type": "database_export",
                "size": "100GB"
            }
        }
    ]
    for log in logs:
        send_log(log)
        time.sleep(1)

def test_zero_day():
    """Test zero-day threat detection"""
    print("\n🆕 Testing Zero-Day Threat Detection...")
    logs = [
        {
            "source": "ids",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "CRITICAL",
            "message": "Unknown attack pattern detected: Novel exploit targeting zero-day vulnerability in web server",
            "metadata": {
                "ip": "192.0.2.50",
                "source_ip": "192.0.2.50",
                "attack_type": "unknown",
                "signature": "unidentified",
                "anomaly_score": 0.95
            }
        },
        {
            "source": "application",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "ERROR",
            "message": "Unusual process behavior detected: Unknown executable with suspicious network activity",
            "metadata": {
                "ip": "10.0.0.25",
                "process_name": "unknown_process.exe",
                "behavior": "suspicious_network_activity",
                "signature": "unidentified"
            }
        }
    ]
    for log in logs:
        send_log(log)
        time.sleep(1)

def test_advanced_persistent_threat():
    """Test APT detection"""
    print("\n🕵️ Testing Advanced Persistent Threat Detection...")
    logs = [
        {
            "source": "ids",
            "timestamp": datetime.now().isoformat(),
            "logLevel": "WARN",
            "message": "Advanced persistent threat detected: Covert lateral movement and privilege escalation activity",
            "metadata": {
                "ip": "192.168.1.75",
                "source_ip": "192.168.1.75",
                "attack_type": "lateral_movement",
                "duration": "30+ days",
                "stealth": "high"
            }
        }
    ]
    for log in logs:
        send_log(log)
        time.sleep(1)

def main():
    """Run all anomaly detection tests"""
    print("=" * 60)
    print("🧪 AI SOC Assistant - Anomaly Detection Test Suite")
    print("=" * 60)
    print("\nThis script will generate various security threats to test")
    print("the AI-powered anomaly detection system.")
    print("\nMake sure the application is running:")
    print("  docker-compose up")
    print("\nStarting tests in 3 seconds...\n")
    time.sleep(3)
    
    # Run all tests
    test_malware_detection()
    time.sleep(2)
    
    test_port_intrusion()
    time.sleep(2)
    
    test_brute_force()
    time.sleep(2)
    
    test_ddos()
    time.sleep(2)
    
    test_sql_injection()
    time.sleep(2)
    
    test_ransomware()
    time.sleep(2)
    
    test_data_exfiltration()
    time.sleep(2)
    
    test_zero_day()
    time.sleep(2)
    
    test_advanced_persistent_threat()
    
    print("\n" + "=" * 60)
    print("✅ Test Suite Complete!")
    print("=" * 60)
    print("\n📊 View Results:")
    print("  1. Open Dashboard: http://localhost:3000")
    print("  2. Check 'Live Threat Detection' section")
    print("  3. View 'Incidents' page for detailed analysis")
    print("  4. Check 'Protection' dashboard for blocked threats")
    print("\nThe AI system should have:")
    print("  • Detected all threats automatically")
    print("  • Created incident reports")
    print("  • Generated AI-powered analysis")
    print("  • Blocked malicious IPs in real-time")
    print("\n")

if __name__ == "__main__":
    main()

