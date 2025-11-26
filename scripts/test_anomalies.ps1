# Test Anomaly Detection Script for Windows
# Tests the AI SOC Assistant anomaly detection system

$IngestionUrl = "http://localhost:8080/api/logs/ingest"

function Send-Log {
    param($LogData)
    try {
        $response = Invoke-RestMethod -Uri $IngestionUrl -Method Post -Body ($LogData | ConvertTo-Json -Depth 10) -ContentType "application/json"
        $msg = $LogData.message
        if ($msg.Length -gt 50) { $msg = $msg.Substring(0, 50) + "..." }
        Write-Host "SUCCESS: Sent - $msg" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "ERROR: Failed - $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "AI SOC Assistant - Anomaly Detection Test Suite" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will generate various security threats to test"
Write-Host "the AI-powered anomaly detection system."
Write-Host ""
Write-Host "Starting tests in 3 seconds..."
Write-Host ""
Start-Sleep -Seconds 3

# Test 1: Malware Detection
Write-Host "[TEST 1] Testing Malware Detection..." -ForegroundColor Yellow
$malwareLog = @{
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
Send-Log -LogData $malwareLog
Start-Sleep -Seconds 2

# Test 2: Port Intrusion
Write-Host "[TEST 2] Testing Port Intrusion Detection..." -ForegroundColor Yellow
$portScanLog = @{
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
Send-Log -LogData $portScanLog
Start-Sleep -Seconds 2

# Test 3: Brute Force
Write-Host "[TEST 3] Testing Brute Force Attack Detection..." -ForegroundColor Yellow
$bruteForceLog = @{
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
Send-Log -LogData $bruteForceLog
Start-Sleep -Seconds 2

# Test 4: DDoS
Write-Host "[TEST 4] Testing DDoS Attack Detection..." -ForegroundColor Yellow
$ddosLog = @{
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
Send-Log -LogData $ddosLog
Start-Sleep -Seconds 2

# Test 5: SQL Injection
Write-Host "[TEST 5] Testing SQL Injection Detection..." -ForegroundColor Yellow
$sqlInjectionLog = @{
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
Send-Log -LogData $sqlInjectionLog
Start-Sleep -Seconds 2

# Test 6: Ransomware
Write-Host "[TEST 6] Testing Ransomware Detection..." -ForegroundColor Yellow
$ransomwareLog = @{
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
Send-Log -LogData $ransomwareLog
Start-Sleep -Seconds 2

# Test 7: Zero-Day
Write-Host "[TEST 7] Testing Zero-Day Threat Detection..." -ForegroundColor Yellow
$zeroDayLog = @{
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
Send-Log -LogData $zeroDayLog
Start-Sleep -Seconds 2

# Test 8: Data Exfiltration
Write-Host "[TEST 8] Testing Data Exfiltration Detection..." -ForegroundColor Yellow
$dataExfilLog = @{
    source = "network"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    logLevel = "ERROR"
    message = "Large data transfer detected: 50GB of sensitive data uploaded to external server 198.51.100.50"
    metadata = @{
        ip = "198.51.100.50"
        source_ip = "192.168.1.100"
        data_size = "50GB"
        data_type = "sensitive"
        destination = "external_server"
    }
}
Send-Log -LogData $dataExfilLog

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Test Suite Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "View Results:" -ForegroundColor Yellow
Write-Host "  1. Open Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "  2. Check Live Threat Detection section" -ForegroundColor White
Write-Host "  3. View Incidents page for detailed analysis" -ForegroundColor White
Write-Host "  4. Check Protection dashboard for blocked threats" -ForegroundColor White
Write-Host ""
Write-Host "The AI system should have:" -ForegroundColor Yellow
Write-Host "  - Detected all threats automatically" -ForegroundColor White
Write-Host "  - Created incident reports" -ForegroundColor White
Write-Host "  - Generated AI-powered analysis" -ForegroundColor White
Write-Host "  - Blocked malicious IPs in real-time" -ForegroundColor White
Write-Host ""
