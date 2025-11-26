# 🧪 Manual Threat Testing Guide

## How to Manually Test Threat Detection

This guide shows you how to manually send security threats to test the AI SOC Assistant system.

---

## 🚀 Quick Start

### Option 1: Use PowerShell (Windows)

```powershell
# Test Malware Detection
$body = @{
    source = "antivirus"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "CRITICAL"
    message = "Malware detected: Trojan.Win32.Backdoor in C:\Windows\System32\suspicious.exe"
    metadata = @{
        ip = "192.168.1.100"
        file_path = "C:\Windows\System32\suspicious.exe"
        threat_name = "Trojan.Win32.Backdoor"
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/api/logs/ingest" -Method POST -Body $body -ContentType "application/json"
```

### Option 2: Use curl (Windows/Linux/Mac)

```bash
curl -X POST http://localhost:8080/api/logs/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source": "antivirus",
    "timestamp": "2024-01-15T10:30:00Z",
    "logLevel": "CRITICAL",
    "message": "Malware detected: Trojan.Win32.Backdoor",
    "metadata": {
      "ip": "192.168.1.100",
      "file_path": "C:\\Windows\\System32\\suspicious.exe",
      "threat_name": "Trojan.Win32.Backdoor"
    }
  }'
```

### Option 3: Use Python

```python
import requests
import json
from datetime import datetime

url = "http://localhost:8080/api/logs/ingest"
data = {
    "source": "antivirus",
    "timestamp": datetime.now().isoformat(),
    "logLevel": "CRITICAL",
    "message": "Malware detected: Trojan.Win32.Backdoor",
    "metadata": {
        "ip": "192.168.1.100",
        "file_path": "C:\\Windows\\System32\\suspicious.exe",
        "threat_name": "Trojan.Win32.Backdoor"
    }
}

response = requests.post(url, json=data)
print(response.json())
```

---

## 🎯 Threat Test Scenarios

### 1. Malware Detection

**PowerShell:**

```````powershell
$body = @{
    source = "antivirus"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "CRITICAL"
    message = "Malware detected: Trojan.Win32.Backdoor detected in C:\Windows\System32\suspicious.exe"
    metadata = @{
        ip = "192.168.1.50"
        file_path = "C:\Windows\System32\suspicious.exe"
        process_id = "1234"
        threat_name = "Trojan.Win32.Backdoor"
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/api/logs/ingest" -Method POST -Body $body -ContentType "application/json"
``````powershell
$body = @{
    source = "antivirus"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "CRITICAL"
    message = "Malware detected: Trojan.Win32.Backdoor detected in C:\Windows\System32\suspicious.exe"
    metadata = @{
        ip = "192.168.1.50"
        file_path = "C:\Windows\System32\suspicious.exe"
        process_id = "1234"
        threat_name = "Trojan.Win32.Backdoor"
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/api/logs/ingest" -Method POST -Body $body -ContentType "application/json"
```````

**Expected Result:**

- ✅ Threat appears in dashboard
- ✅ Incident created with severity CRITICAL
- ✅ IP address blocked
- ✅ AI-generated analysis available

---

### 2. Port Intrusion / Port Scanning

**PowerShell:**

```powershell
$body = @{
    source = "firewall"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "HIGH"
    message = "Port scan detected: Multiple connection attempts from 203.0.113.45 on ports 22, 80, 443, 3389"
    metadata = @{
        source_ip = "203.0.113.45"
        destination_ip = "192.168.1.1"
        ports = @(22, 80, 443, 3389)
        connection_count = 150
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/api/logs/ingest" -Method POST -Body $body -ContentType "application/json"
```

---

### 3. Brute Force Attack

**PowerShell:**

```powershell
$body = @{
    source = "auth"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "HIGH"
    message = "Brute force attack detected: 50 failed login attempts from 198.51.100.10 for user 'admin'"
    metadata = @{
        source_ip = "198.51.100.10"
        username = "admin"
        failed_attempts = 50
        time_window = "5 minutes"
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/api/logs/ingest" -Method POST -Body $body -ContentType "application/json"
```

---

### 4. DDoS Attack

**PowerShell:**

```powershell
$body = @{
    source = "network"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "CRITICAL"
    message = "DDoS attack detected: SYN flood from multiple IPs targeting port 80, 50000 requests/second"
    metadata = @{
        attack_type = "SYN Flood"
        target_port = 80
        request_rate = "50000/sec"
        source_ips = @("10.0.0.1", "10.0.0.2", "10.0.0.3")
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/api/logs/ingest" -Method POST -Body $body -ContentType "application/json"
```

---

### 5. SQL Injection Attack

**PowerShell:**

```powershell
$body = @{
    source = "web_server"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "HIGH"
    message = "SQL injection attempt detected: Malicious query 'OR 1=1--' from 172.16.0.50"
    metadata = @{
        source_ip = "172.16.0.50"
        injection_pattern = "OR 1=1--"
        target_endpoint = "/api/users"
        database = "users_db"
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/api/logs/ingest" -Method POST -Body $body -ContentType "application/json"
```

---

### 6. Ransomware Detection

**PowerShell:**

```powershell
$body = @{
    source = "file_system"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "CRITICAL"
    message = "Ransomware detected: Multiple files encrypted with .locky extension, ransom note found"
    metadata = @{
        affected_files = 500
        encryption_type = ".locky"
        ransom_note = "README_LOCKY.txt"
        source_ip = "192.168.1.200"
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/api/logs/ingest" -Method POST -Body $body -ContentType "application/json"
```

---

### 7. Zero-Day Attack (Unknown Pattern)

**PowerShell:**

```powershell
$body = @{
    source = "ids"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "CRITICAL"
    message = "Anomalous behavior detected: Unknown attack pattern with high anomaly score 0.95"
    metadata = @{
        source_ip = "10.10.10.100"
        anomaly_score = 0.95
        behavior_pattern = "unusual_process_chain"
        indicators = @("suspicious_process_spawn", "unusual_network_activity")
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/api/logs/ingest" -Method POST -Body $body -ContentType "application/json"
```

---

### 8. Data Exfiltration

**PowerShell:**

```powershell
$body = @{
    source = "network_monitor"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "HIGH"
    message = "Data exfiltration detected: Large data transfer 5GB from internal network to external IP 203.0.113.100"
    metadata = @{
        source_ip = "192.168.1.150"
        destination_ip = "203.0.113.100"
        data_size = "5GB"
        transfer_rate = "100MB/s"
        file_types = @("database", "documents")
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/api/logs/ingest" -Method POST -Body $body -ContentType "application/json"
```

---

### 9. Phishing Attempt

**PowerShell:**

```powershell
$body = @{
    source = "email_security"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "MEDIUM"
    message = "Phishing email detected: Suspicious email from external domain attempting credential theft"
    metadata = @{
        sender_email = "fake@example.com"
        target_email = "user@company.com"
        phishing_type = "credential_theft"
        suspicious_link = "http://fake-login.com"
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/api/logs/ingest" -Method POST -Body $body -ContentType "application/json"
```

---

### 10. Unauthorized Access

**PowerShell:**

```powershell
$body = @{
    source = "access_control"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "HIGH"
    message = "Unauthorized access attempt: Failed authentication from 172.16.0.25 trying to access admin panel"
    metadata = @{
        source_ip = "172.16.0.25"
        target_resource = "/admin"
        access_method = "web_interface"
        attempt_count = 3
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/api/logs/ingest" -Method POST -Body $body -ContentType "application/json"
```

---

## 📊 Verify Detection

After sending a threat, check:

### 1. Dashboard (http://localhost:3000)

- **Live Threats Feed** - Should show the threat within 5-10 seconds
- **Real-Time Protection** - Shows blocked IPs and threats
- **Statistics** - Updated threat counts

### 2. Incidents Page

- Click **"Incidents"** in navigation
- Your threat should appear as an incident
- Click on it to see:
  - AI-generated analysis
  - Threat details
  - Mitigation steps
  - Generated script

### 3. Protection Dashboard

- Click **"Protection"** in navigation
- Check:
  - Blocked IPs list
  - Quarantined files
  - Active protection status

---

## 🔄 Automated Testing Script

You can also use the existing test script:

**PowerShell:**

```powershell
powershell -ExecutionPolicy Bypass -File scripts\test_anomalies.ps1
```

**Python:**

```bash
python scripts/test_anomaly_detection.py
```

---

## 🎯 Testing Checklist

After sending each threat, verify:

- [ ] Threat appears in dashboard live feed
- [ ] Incident is created automatically
- [ ] AI analysis is generated
- [ ] IP address is blocked (if applicable)
- [ ] Threat severity is correctly assigned
- [ ] Mitigation steps are provided
- [ ] Protection dashboard shows the threat

---

## 💡 Tips

1. **Wait 5-10 seconds** after sending a threat before checking
2. **Refresh the dashboard** to see updates
3. **Check browser console** for any errors
4. **Use different IP addresses** for each test
5. **Try different severity levels** (CRITICAL, HIGH, MEDIUM, LOW)

---

## 🐛 Troubleshooting

**Threat not appearing?**

- Check if services are running: `docker-compose ps`
- Check logs: `docker-compose logs ml-service`
- Verify API is accessible: `curl http://localhost:8080/api/logs/ingest`

**No incidents created?**

- Check ML service logs for errors
- Verify Kafka is running
- Check database connection

---

**Happy Testing! 🚀**
