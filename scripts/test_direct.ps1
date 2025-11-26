# Direct Test Script - Bypasses Kafka and calls ML service directly
# This works even if Kafka is not running

$MLServiceUrl = "http://localhost:8000/api/direct/process-log"

function Send-Threat {
    param($ThreatData)
    try {
        $response = Invoke-RestMethod -Uri $MLServiceUrl -Method Post -Body ($ThreatData | ConvertTo-Json -Depth 10) -ContentType "application/json"
        if ($response.threat_detected) {
            Write-Host "THREAT DETECTED!" -ForegroundColor Red
            Write-Host "  Type: $($response.threat_type)" -ForegroundColor Yellow
            Write-Host "  Severity: $($response.severity)" -ForegroundColor Yellow
            Write-Host "  Score: $([math]::Round($response.anomaly_score * 100, 1))%" -ForegroundColor Yellow
            Write-Host "  Incident ID: $($response.incident_id)" -ForegroundColor Cyan
            if ($response.blocked) {
                Write-Host "  Status: BLOCKED" -ForegroundColor Green
            }
        } else {
            Write-Host "No threat detected" -ForegroundColor Gray
        }
        return $true
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Direct Threat Detection Test (Bypasses Kafka)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Malware
Write-Host "[TEST 1] Malware Detection..." -ForegroundColor Yellow
$malware = @{
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
}
Send-Threat -ThreatData $malware
Start-Sleep -Seconds 2

# Test 2: Port Intrusion
Write-Host "`n[TEST 2] Port Intrusion Detection..." -ForegroundColor Yellow
$portScan = @{
    source = "firewall"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "WARN"
    message = "Port scan detected from 203.0.113.45 - scanning ports 22, 80, 443, 3389"
    metadata = @{
        ip = "203.0.113.45"
        source_ip = "203.0.113.45"
        port = "22"
        protocol = "TCP"
        scan_type = "stealth_scan"
    }
}
Send-Threat -ThreatData $portScan
Start-Sleep -Seconds 2

# Test 3: Brute Force
Write-Host "`n[TEST 3] Brute Force Attack..." -ForegroundColor Yellow
$bruteForce = @{
    source = "application"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "ERROR"
    message = "Multiple failed login attempts detected for user admin from IP 172.16.0.50 - 15 failed attempts in 5 minutes"
    metadata = @{
        ip = "172.16.0.50"
        source_ip = "172.16.0.50"
        username = "admin"
        failed_attempts = 15
        time_window = "5 minutes"
    }
}
Send-Threat -ThreatData $bruteForce
Start-Sleep -Seconds 2

# Test 4: DDoS
Write-Host "`n[TEST 4] DDoS Attack..." -ForegroundColor Yellow
$ddos = @{
    source = "firewall"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "CRITICAL"
    message = "DDoS attack detected: SYN flood from multiple IPs targeting port 80 - 10,000+ requests/second"
    metadata = @{
        ip = "203.0.113.0/24"
        source_ip = "203.0.113.1"
        port = "80"
        attack_type = "syn_flood"
        requests_per_second = 10000
    }
}
Send-Threat -ThreatData $ddos
Start-Sleep -Seconds 2

# Test 5: SQL Injection
Write-Host "`n[TEST 5] SQL Injection..." -ForegroundColor Yellow
$sqlInjection = @{
    source = "application"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "ERROR"
    message = "SQL injection attempt detected: UNION SELECT attack from 192.168.1.200 on endpoint /api/users"
    metadata = @{
        ip = "192.168.1.200"
        source_ip = "192.168.1.200"
        endpoint = "/api/users"
        attack_pattern = "UNION SELECT"
    }
}
Send-Threat -ThreatData $sqlInjection
Start-Sleep -Seconds 2

# Test 6: Ransomware
Write-Host "`n[TEST 6] Ransomware..." -ForegroundColor Yellow
$ransomware = @{
    source = "file_system"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "CRITICAL"
    message = "Ransomware activity detected: Multiple files encrypted with .locky extension - ransom note found"
    metadata = @{
        ip = "192.168.1.150"
        file_path = "C:\Users\Documents\"
        encrypted_files = 500
        extension = ".locky"
        ransom_amount = "0.5 BTC"
    }
}
Send-Threat -ThreatData $ransomware
Start-Sleep -Seconds 2

# Test 7: Zero-Day
Write-Host "`n[TEST 7] Zero-Day Threat..." -ForegroundColor Yellow
$zeroDay = @{
    source = "ids"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "CRITICAL"
    message = "Unknown attack pattern detected: Novel exploit targeting zero-day vulnerability in web server"
    metadata = @{
        ip = "192.0.2.50"
        source_ip = "192.0.2.50"
        attack_type = "unknown"
        signature = "unidentified"
        anomaly_score = 0.95
    }
}
Send-Threat -ThreatData $zeroDay

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "Test Complete! Check Dashboard: http://localhost:3000" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

