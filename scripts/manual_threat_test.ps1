# Manual Threat Testing Script
# Run individual threat tests interactively

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🧪 Manual Threat Testing Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$API_URL = "http://localhost:8080/api/logs/ingest"

function Send-Threat {
    param(
        [string]$Source,
        [string]$LogLevel,
        [string]$Message,
        [hashtable]$Metadata
    )
    
    $body = @{
        source    = $Source
        timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        logLevel  = $LogLevel
        message   = $Message
        metadata  = $Metadata
    } | ConvertTo-Json -Depth 10
    
    try {
        $response = Invoke-RestMethod -Uri $API_URL -Method POST -Body $body -ContentType "application/json"
        Write-Host "✅ Threat sent successfully!" -ForegroundColor Green
        Write-Host "   Message: $($Message.Substring(0, [Math]::Min(60, $Message.Length)))..." -ForegroundColor Gray
        return $true
    }
    catch {
        Write-Host "❌ Failed to send threat: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

Write-Host "Select threat type to test:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1.  Malware Detection (Trojan/Backdoor)" -ForegroundColor White
Write-Host "2.  Port Intrusion / Port Scanning" -ForegroundColor White
Write-Host "3.  Brute Force Attack" -ForegroundColor White
Write-Host "4.  DDoS Attack" -ForegroundColor White
Write-Host "5.  SQL Injection" -ForegroundColor White
Write-Host "6.  Ransomware Detection" -ForegroundColor White
Write-Host "7.  Zero-Day Attack" -ForegroundColor White
Write-Host "8.  Data Exfiltration" -ForegroundColor White
Write-Host "9.  Phishing Attempt" -ForegroundColor White
Write-Host "10. Unauthorized Access" -ForegroundColor White
Write-Host "11. Send All Threats (Full Test)" -ForegroundColor Cyan
Write-Host "0.  Exit" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "Enter your choice (0-11)"

switch ($choice) {
    "1" {
        Write-Host "`nSending Malware Detection Threat..." -ForegroundColor Yellow
        Send-Threat -Source "antivirus" -LogLevel "CRITICAL" `
            -Message "Malware detected: Trojan.Win32.Backdoor detected in C:\Windows\System32\suspicious.exe" `
            -Metadata @{
            ip          = "192.168.1.50"
            file_path   = "C:\Windows\System32\suspicious.exe"
            process_id  = "1234"
            threat_name = "Trojan.Win32.Backdoor"
        }
    }
    "2" {
        Write-Host "`nSending Port Intrusion Threat..." -ForegroundColor Yellow
        Send-Threat -Source "firewall" -LogLevel "HIGH" `
            -Message "Port scan detected: Multiple connection attempts from 203.0.113.45 on ports 22, 80, 443, 3389" `
            -Metadata @{
            source_ip        = "203.0.113.45"
            destination_ip   = "192.168.1.1"
            ports            = @(22, 80, 443, 3389)
            connection_count = 150
        }
    }
    "3" {
        Write-Host "`nSending Brute Force Attack Threat..." -ForegroundColor Yellow
        Send-Threat -Source "auth" -LogLevel "HIGH" `
            -Message "Brute force attack detected: 50 failed login attempts from 198.51.100.10 for user 'admin'" `
            -Metadata @{
            source_ip       = "198.51.100.10"
            username        = "admin"
            failed_attempts = 50
            time_window     = "5 minutes"
        }
    }
    "4" {
        Write-Host "`nSending DDoS Attack Threat..." -ForegroundColor Yellow
        Send-Threat -Source "network" -LogLevel "CRITICAL" `
            -Message "DDoS attack detected: SYN flood from multiple IPs targeting port 80, 50000 requests/second" `
            -Metadata @{
            attack_type  = "SYN Flood"
            target_port  = 80
            request_rate = "50000/sec"
            source_ips   = @("10.0.0.1", "10.0.0.2", "10.0.0.3")
        }
    }
    "5" {
        Write-Host "`nSending SQL Injection Threat..." -ForegroundColor Yellow
        Send-Threat -Source "web_server" -LogLevel "HIGH" `
            -Message "SQL injection attempt detected: Malicious query 'OR 1=1--' from 172.16.0.50" `
            -Metadata @{
            source_ip         = "172.16.0.50"
            injection_pattern = "OR 1=1--"
            target_endpoint   = "/api/users"
            database          = "users_db"
        }
    }
    "6" {
        Write-Host "`nSending Ransomware Detection Threat..." -ForegroundColor Yellow
        Send-Threat -Source "file_system" -LogLevel "CRITICAL" `
            -Message "Ransomware detected: Multiple files encrypted with .locky extension, ransom note found" `
            -Metadata @{
            affected_files  = 500
            encryption_type = ".locky"
            ransom_note     = "README_LOCKY.txt"
            source_ip       = "192.168.1.200"
        }
    }
    "7" {
        Write-Host "`nSending Zero-Day Attack Threat..." -ForegroundColor Yellow
        Send-Threat -Source "ids" -LogLevel "CRITICAL" `
            -Message "Anomalous behavior detected: Unknown attack pattern with high anomaly score 0.95" `
            -Metadata @{
            source_ip        = "10.10.10.100"
            anomaly_score    = 0.95
            behavior_pattern = "unusual_process_chain"
            indicators       = @("suspicious_process_spawn", "unusual_network_activity")
        }
    }
    "8" {
        Write-Host "`nSending Data Exfiltration Threat..." -ForegroundColor Yellow
        Send-Threat -Source "network_monitor" -LogLevel "HIGH" `
            -Message "Data exfiltration detected: Large data transfer 5GB from internal network to external IP 203.0.113.100" `
            -Metadata @{
            source_ip      = "192.168.1.150"
            destination_ip = "203.0.113.100"
            data_size      = "5GB"
            transfer_rate  = "100MB/s"
            file_types     = @("database", "documents")
        }
    }
    "9" {
        Write-Host "`nSending Phishing Attempt Threat..." -ForegroundColor Yellow
        Send-Threat -Source "email_security" -LogLevel "MEDIUM" `
            -Message "Phishing email detected: Suspicious email from external domain attempting credential theft" `
            -Metadata @{
            sender_email    = "fake@example.com"
            target_email    = "user@company.com"
            phishing_type   = "credential_theft"
            suspicious_link = "http://fake-login.com"
        }
    }
    "10" {
        Write-Host "`nSending Unauthorized Access Threat..." -ForegroundColor Yellow
        Send-Threat -Source "access_control" -LogLevel "HIGH" `
            -Message "Unauthorized access attempt: Failed authentication from 172.16.0.25 trying to access admin panel" `
            -Metadata @{
            source_ip       = "172.16.0.25"
            target_resource = "/admin"
            access_method   = "web_interface"
            attempt_count   = 3
        }
    }
    "11" {
        Write-Host "`nSending All Threat Types..." -ForegroundColor Cyan
        Write-Host "This will send 10 different threats with 2 second delays" -ForegroundColor Gray
        Write-Host ""
        
        $threats = @(
            @{num = 1; name = "Malware"; source = "antivirus"; level = "CRITICAL"; msg = "Malware detected: Trojan.Win32.Backdoor"; meta = @{ip = "192.168.1.50"; threat_name = "Trojan.Win32.Backdoor" } },
            @{num = 2; name = "Port Intrusion"; source = "firewall"; level = "HIGH"; msg = "Port scan detected from 203.0.113.45"; meta = @{source_ip = "203.0.113.45"; ports = @(22, 80, 443) } },
            @{num = 3; name = "Brute Force"; source = "auth"; level = "HIGH"; msg = "Brute force: 50 failed logins from 198.51.100.10"; meta = @{source_ip = "198.51.100.10"; failed_attempts = 50 } },
            @{num = 4; name = "DDoS"; source = "network"; level = "CRITICAL"; msg = "DDoS SYN flood: 50000 req/sec"; meta = @{attack_type = "SYN Flood"; target_port = 80 } },
            @{num = 5; name = "SQL Injection"; source = "web_server"; level = "HIGH"; msg = "SQL injection: OR 1=1-- from 172.16.0.50"; meta = @{source_ip = "172.16.0.50"; injection_pattern = "OR 1=1--" } },
            @{num = 6; name = "Ransomware"; source = "file_system"; level = "CRITICAL"; msg = "Ransomware: .locky encryption detected"; meta = @{affected_files = 500; encryption_type = ".locky" } },
            @{num = 7; name = "Zero-Day"; source = "ids"; level = "CRITICAL"; msg = "Zero-day: Anomaly score 0.95"; meta = @{source_ip = "10.10.10.100"; anomaly_score = 0.95 } },
            @{num = 8; name = "Data Exfiltration"; source = "network_monitor"; level = "HIGH"; msg = "Data exfiltration: 5GB transfer"; meta = @{source_ip = "192.168.1.150"; data_size = "5GB" } },
            @{num = 9; name = "Phishing"; source = "email_security"; level = "MEDIUM"; msg = "Phishing email detected"; meta = @{sender_email = "fake@example.com"; phishing_type = "credential_theft" } },
            @{num = 10; name = "Unauthorized Access"; source = "access_control"; level = "HIGH"; msg = "Unauthorized access attempt"; meta = @{source_ip = "172.16.0.25"; target_resource = "/admin" } }
        )
        
        foreach ($threat in $threats) {
            Write-Host "[$($threat.num)/10] Sending $($threat.name)..." -ForegroundColor Yellow
            Send-Threat -Source $threat.source -LogLevel $threat.level -Message $threat.msg -Metadata $threat.meta
            Start-Sleep -Seconds 2
        }
        
        Write-Host "`n✅ All threats sent!" -ForegroundColor Green
        Write-Host "Check the dashboard at http://localhost:3000" -ForegroundColor Cyan
    }
    "0" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit
    }
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Wait 5-10 seconds for processing" -ForegroundColor White
Write-Host "2. Open dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "3. Check Incidents page for the threat" -ForegroundColor White
Write-Host "4. View AI-generated analysis" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

