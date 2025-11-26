# Quick Test Guide - How Anomaly Detection Works

## ✅ Test Completed!

8 different security threats have been sent to the system. Here's what happens next:

## 🔄 How It Works (Step by Step)

### Step 1: Log Ingestion (0-2 seconds)
- Logs are received by the Log Ingestion Service
- Stored in MongoDB
- Published to Kafka for real-time processing

### Step 2: AI Detection (2-5 seconds)
- **Deep Learning Model** analyzes the log patterns
- **Anomaly Detection** identifies suspicious behavior
- **Threat Classification** determines threat type
- **Zero-Day Detection** identifies unknown patterns

### Step 3: Automatic Response (5-10 seconds)
- **Real-Time Blocking**: Malicious IPs are blocked
- **Incident Creation**: Incidents are automatically created
- **AI Analysis**: Generative AI creates detailed reports
- **Protection Activation**: Active defense system blocks threats

### Step 4: Results Available (10-30 seconds)
- **Dashboard Updates**: Live threat feed shows detected threats
- **Incident Reports**: Full AI-generated analysis available
- **Protection Status**: Shows blocked IPs and statistics

## 📊 View Results Now

### 1. Open the Dashboard
```
http://localhost:3000
```

### 2. Check Live Threat Detection
- Look at the top of the dashboard
- You should see threats appearing in real-time
- Each threat shows:
  - Threat type (Malware, Port Intrusion, etc.)
  - Severity level (CRITICAL, HIGH, MEDIUM)
  - Source IP address
  - Anomaly score

### 3. View Protection Dashboard
- Scroll down to see "Real-Time Protection" section
- Check:
  - Threats blocked today
  - IPs blocked
  - Active protection features
  - Blocked threats list

### 4. Check Incidents Page
- Click "Incidents" in the navigation
- See all detected threats
- Click any incident to see:
  - Full AI-generated analysis
  - Indicators of Compromise (IOCs)
  - Attack vector identification
  - Mitigation steps and scripts

## 🧪 What Was Tested

1. **Malware Detection** - Trojan/Backdoor detection
2. **Port Intrusion** - Port scanning and unauthorized access
3. **Brute Force** - Multiple failed login attempts
4. **DDoS Attack** - SYN flood and traffic spikes
5. **SQL Injection** - Database injection attacks
6. **Ransomware** - File encryption and extortion
7. **Zero-Day Threat** - Unknown attack patterns
8. **Data Exfiltration** - Unauthorized data transfers

## 🎯 Expected Results

For each threat, you should see:

✅ **Automatic Detection**
- Threat appears in live feed
- Severity level assigned
- Threat type classified

✅ **Real-Time Blocking**
- IP addresses blocked
- Protection activated
- Firewall rules applied

✅ **AI Analysis**
- Detailed threat analysis
- IOCs extracted
- Attack vector identified
- Mitigation recommendations

✅ **Incident Reports**
- Full incident created
- AI-generated summary
- Technical analysis
- Actionable mitigation steps

## 🔍 Detailed View

Click on any incident to see:
- **Threat Classification**: Type, severity, confidence
- **Technical Analysis**: IOCs, attack vector, impact
- **AI Summary**: Human-readable analysis
- **Mitigation Steps**: Actionable recommendations
- **Mitigation Script**: Executable script to block threat

## 🚀 Run More Tests

To test again or send more threats:

```powershell
# Run the test script again
powershell -ExecutionPolicy Bypass -File scripts\test_anomalies.ps1
```

Or send individual threats using curl:

```bash
curl -X POST http://localhost:8080/api/logs/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source": "firewall",
    "timestamp": "2024-01-15T10:30:00Z",
    "logLevel": "CRITICAL",
    "message": "Your custom threat message here",
    "metadata": {
      "ip": "192.168.1.100"
    }
  }'
```

## 📈 Monitor in Real-Time

The dashboard updates automatically every:
- **Live Threats**: Every 5 seconds
- **Protection Status**: Every 3 seconds
- **System Info**: Every 5 seconds

Just keep the browser open and watch threats appear!

## 🎓 Understanding the AI Detection

The system uses:
1. **Deep Learning** (Transformer model) for pattern recognition
2. **Anomaly Detection** for unusual behavior
3. **Generative AI** for analysis and reporting
4. **Active Defense** for real-time blocking

All threats are analyzed and blocked automatically - no manual intervention needed!

