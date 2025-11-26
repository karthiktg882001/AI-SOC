-- Create test incidents for dashboard testing
INSERT INTO incidents (incident_id, severity, status, threat_type, source_ip, timestamp, detected_at, anomaly_score, description, raw_log_data) VALUES
('INC-001', 'CRITICAL', 'OPEN', 'Malware', '192.168.1.50', NOW(), NOW(), 0.95, 'Malware detected: Trojan.Win32.Backdoor detected in C:\Windows\System32\suspicious.exe', '{"threat_name": "Trojan.Win32.Backdoor"}'::jsonb),
('INC-002', 'HIGH', 'OPEN', 'Port Scan', '203.0.113.45', NOW(), NOW(), 0.85, 'Port scan detected: Multiple connection attempts from 203.0.113.45 on ports 22, 80, 443, 3389', '{"ports": [22, 80, 443, 3389]}'::jsonb),
('INC-003', 'HIGH', 'OPEN', 'Brute Force', '198.51.100.10', NOW(), NOW(), 0.80, 'Brute force attack detected: 50 failed login attempts from 198.51.100.10 for user admin', '{"failed_attempts": 50}'::jsonb),
('INC-004', 'CRITICAL', 'OPEN', 'DDoS', '10.0.0.1', NOW(), NOW(), 0.92, 'DDoS attack detected: SYN flood from multiple IPs targeting port 80, 50000 requests/second', '{"attack_type": "SYN Flood"}'::jsonb),
('INC-005', 'MEDIUM', 'OPEN', 'SQL Injection', '172.16.0.50', NOW(), NOW(), 0.65, 'SQL injection attempt detected: Malicious query OR 1=1-- from 172.16.0.50', '{"injection_pattern": "OR 1=1--"}'::jsonb),
('INC-006', 'CRITICAL', 'OPEN', 'Ransomware', '192.168.1.200', NOW(), NOW(), 0.90, 'Ransomware detected: Multiple files encrypted with .locky extension, ransom note found', '{"affected_files": 500, "encryption_type": ".locky"}'::jsonb),
('INC-007', 'HIGH', 'OPEN', 'Data Exfiltration', '192.168.1.150', NOW(), NOW(), 0.75, 'Data exfiltration detected: Large data transfer 5GB from internal network to external IP 203.0.113.100', '{"data_size": "5GB"}'::jsonb);

