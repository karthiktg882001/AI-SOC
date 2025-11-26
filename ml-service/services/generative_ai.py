from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI package not available. Using fallback responses.")

class GenerativeAIService:
    def __init__(self):
        self._ready = True
        self.openai_client = None
        self.openai_enabled = False
        
        # Initialize OpenAI client if API key is available
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY", "")
            if api_key:
                try:
                    self.openai_client = OpenAI(api_key=api_key)
                    self.openai_enabled = True
                    print("✅ OpenAI client initialized successfully")
                except Exception as e:
                    print(f"⚠️ Failed to initialize OpenAI client: {e}")
                    print("   Using fallback rule-based responses")
            else:
                print("⚠️ OPENAI_API_KEY not set. Using fallback rule-based responses")
        else:
            print("⚠️ OpenAI package not installed. Using fallback rule-based responses")
    
    def _call_openai(self, prompt: str, system_prompt: str = None, model: str = "gpt-3.5-turbo", max_tokens: int = 1000) -> Optional[str]:
        """Call OpenAI API with error handling"""
        if not self.openai_enabled or not self.openai_client:
            return None
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ OpenAI API call failed: {e}")
            return None
    
    def is_ready(self) -> bool:
        return self._ready
    
    def generate_help_response(self, message: str, context: str = "default") -> str:
        """Generate AI-powered help response for security-related questions"""
        message_lower = message.lower()
        
        # Security-related question handlers
        security_keywords = {
            "malware": "Malware (malicious software) includes viruses, trojans, ransomware, and spyware. Our SOC Assistant uses AI and Deep Learning to detect malware patterns, zero-day threats, and suspicious behaviors. If you suspect malware, check the Incidents page for detected threats and follow the AI-generated mitigation steps.",
            "virus": "A virus is a type of malware that replicates itself. Our system detects viruses through behavioral analysis and pattern recognition. Check the Protection Dashboard to see blocked threats and quarantined files. Always keep your antivirus updated and avoid suspicious downloads.",
            "threat": "Security threats include malware, intrusions, DDoS attacks, and unauthorized access attempts. Our AI-powered system continuously monitors for threats and provides real-time alerts. View the Dashboard for current threat statistics and the Incidents page for detailed threat information.",
            "attack": "Common attacks include brute force, SQL injection, port scanning, DDoS, and phishing. Our system detects these automatically and provides mitigation recommendations. Check the Incidents page to see detected attacks and their severity levels.",
            "intrusion": "Intrusions are unauthorized access attempts. Our system monitors for port scans, failed login attempts, and suspicious network activity. View incidents marked as 'intrusion' for details and follow the AI-generated response steps.",
            "firewall": "A firewall protects your network by blocking unauthorized access. Our system can automatically block malicious IPs. Check the Protection Dashboard to see blocked IPs, ports, and processes.",
            "password": "Strong passwords should be at least 8 characters with uppercase, lowercase, numbers, and symbols. Enable multi-factor authentication (MFA) for better security. You can change your password in the Profile section.",
            "phishing": "Phishing is a social engineering attack where attackers trick users into revealing sensitive information. Be cautious of suspicious emails and links. Our system can detect phishing attempts through log analysis.",
            "ddos": "DDoS (Distributed Denial of Service) attacks overwhelm systems with traffic. Our system detects DDoS patterns and recommends mitigation steps like rate limiting and IP blocking. Check incidents for DDoS detection.",
            "vulnerability": "Vulnerabilities are security weaknesses in software or systems. Keep all software updated, apply security patches promptly, and use the Reports feature to analyze potential vulnerabilities in your logs.",
            "zero-day": "Zero-day attacks exploit unknown vulnerabilities. Our Deep Learning models are trained to detect zero-day threats through anomaly detection and behavioral analysis. Check the Dashboard for zero-day threat alerts.",
            "encryption": "Encryption protects data by converting it into unreadable format. Use strong encryption for sensitive data, secure communications (HTTPS/TLS), and encrypted storage. Our system monitors for unencrypted data transmission.",
            "breach": "A data breach is unauthorized access to sensitive data. If detected, immediately isolate affected systems, change all passwords, notify authorities if required, and review access logs. Check the Incidents page for breach-related alerts.",
            "log": "Security logs record system activities and security events. Our system analyzes logs using AI to detect threats. Use the Reports feature to generate comprehensive log analysis reports.",
            "incident": "Security incidents are detected threats or breaches. View all incidents on the Incidents page, where you can see details, AI analysis, and mitigation steps. Critical incidents require immediate attention.",
            "detection": "Our AI-powered detection system uses Deep Learning to identify threats in real-time. It analyzes patterns, behaviors, and anomalies to detect malware, intrusions, and attacks. Check the Dashboard for detection statistics.",
            "protection": "The Protection Dashboard shows real-time security status including blocked IPs, quarantined files, blocked ports, and terminated processes. It provides active defense against threats.",
            "security": "Security best practices include: using strong passwords, enabling MFA, keeping software updated, monitoring logs regularly, using firewalls, encrypting sensitive data, and following the AI-generated security recommendations from our reports."
        }
        
        # Check for security-related keywords
        for keyword, response in security_keywords.items():
            if keyword in message_lower:
                return response
        
        # Feature-related responses
        help_responses = {
            "dashboard": "The Dashboard shows real-time security statistics, threat detection metrics, recent incidents, and system health. Monitor active threats, view threat trends, and access quick security actions.",
            "incidents": "The Incidents page displays all security incidents detected by our AI system. View detailed threat information, AI-generated analysis, mitigation steps, and executable scripts. Filter by severity, status, or threat type.",
            "reports": "Generate comprehensive AI-powered security reports for individual logs or analyze all logs together. Reports include detailed threat analysis, risk assessment, mitigation recommendations, and actionable security insights.",
            "profile": "Manage your account settings, view device information (IP, browser, OS), monitor real-time system resources (CPU, memory, network, processes), change your password, and view application version.",
            "admin": "Admin Dashboard provides full system management: user management (create, edit, delete), system statistics, incident management, user analytics, and system configuration settings.",
            "login": "Use your registered email and password to login. If you forgot your password, use the password reset feature. For security, use strong passwords and enable MFA if available.",
            "default": "I'm your SOC Security Assistant! I can help with:\n\n🔒 Security Questions:\n• Malware, viruses, and threats\n• Attack types (DDoS, phishing, intrusion)\n• Security best practices\n• Vulnerability management\n• Zero-day detection\n\n📊 System Features:\n• Dashboard and threat monitoring\n• Incident management\n• Security reports\n• Protection settings\n• Account management\n\nAsk me anything about cybersecurity or the SOC Assistant system!"
        }
        
        base_response = help_responses.get(context, help_responses["default"])
        
        # Add contextual information based on message keywords
        if "how" in message_lower or "what" in message_lower:
            return f"{base_response}\n\n💡 Tip: Be specific about your security concern for more detailed guidance!"
        elif "help" in message_lower:
            return f"{base_response}\n\nI'm here 24/7 to assist with all your security questions!"
        else:
            return base_response
    
    def generate_admin_response(self, message: str, context: dict = None) -> str:
        """Generate AI response for admin chat"""
        admin_responses = {
            "users": "User management allows you to create, edit, activate/deactivate, and delete user accounts. You can also assign admin roles and reset passwords.",
            "incidents": "As an admin, you can view all incidents, update their status, delete incidents, and access comprehensive incident reports.",
            "statistics": "The admin dashboard provides system-wide statistics including total users, active users, admin count, total incidents, and resolution metrics.",
            "settings": "System settings allow you to configure application parameters, security policies, and system-wide preferences.",
            "default": "As an administrator, you have access to:\n\n• User Management: Create, edit, and manage user accounts\n• Incident Management: Full control over security incidents\n• System Statistics: Comprehensive system analytics\n• Settings: System configuration and preferences\n\nHow can I assist you with administrative tasks?"
        }
        
        if context:
            context_type = context.get("type", "default")
            return admin_responses.get(context_type, admin_responses["default"])
        
        return admin_responses["default"]
    
    def generate_incident_summary(self, incident_data: Dict[str, Any]) -> str:
        """Generate AI-powered incident summary using OpenAI"""
        threat_type = incident_data.get("threat_type", "UNKNOWN")
        severity = incident_data.get("severity", "MEDIUM")
        source_ip = incident_data.get("source_ip", "N/A")
        description = incident_data.get("description", "")
        anomaly_score = incident_data.get("anomaly_score", 0.0)
        
        # Try OpenAI first
        if self.openai_enabled:
            system_prompt = """You are a cybersecurity expert analyzing security incidents. 
Provide clear, concise, and actionable summaries of security threats. Focus on:
1. What happened (threat type and severity)
2. Why it's concerning (anomaly score and indicators)
3. Immediate recommended actions"""
            
            prompt = f"""Analyze this security incident and provide a comprehensive summary:

Threat Type: {threat_type}
Severity: {severity}
Anomaly Score: {anomaly_score:.2%}
Source IP: {source_ip}
Description: {description}
Timestamp: {incident_data.get('timestamp', 'N/A')}
Destination IP: {incident_data.get('destination_ip', 'N/A')}

Provide a detailed summary including:
- Executive summary of the threat
- Key indicators and why this is concerning
- Immediate recommended actions (3-5 steps)
- Risk assessment

Format the response as a clear, professional security incident summary."""
            
            ai_summary = self._call_openai(prompt, system_prompt, max_tokens=800)
            if ai_summary:
                return ai_summary
        
        # Fallback to rule-based
        summary = f"""
SECURITY INCIDENT SUMMARY

Threat Type: {threat_type}
Severity: {severity}
Anomaly Score: {anomaly_score:.2%}
Source IP: {source_ip}
Timestamp: {incident_data.get('timestamp', 'N/A')}

Description:
{description}

Analysis:
This incident has been flagged as a {severity} severity threat of type {threat_type}. 
The anomaly detection system identified suspicious patterns with a confidence score of {anomaly_score:.2%}.
The source IP {source_ip} has been associated with potentially malicious activity.

Recommended Actions:
1. Immediately investigate the source IP address
2. Review firewall rules and access logs
3. Check for any data exfiltration attempts
4. Consider blocking the source IP if confirmed malicious
5. Update threat intelligence database
"""
        return summary.strip()
    
    def generate_detailed_analysis(self, incident_data: Dict[str, Any]) -> str:
        """Generate detailed technical analysis using OpenAI"""
        threat_type = incident_data.get("threat_type", "UNKNOWN")
        raw_log = incident_data.get("raw_log_data", {})
        
        # Try OpenAI first
        if self.openai_enabled:
            system_prompt = """You are a senior cybersecurity analyst specializing in threat analysis. 
Provide detailed technical analysis of security incidents including:
- Technical indicators of compromise (IOCs)
- Attack vectors and methodologies
- Behavioral patterns
- Impact assessment
- Timeline analysis"""
            
            log_data_str = json.dumps(raw_log, indent=2) if raw_log else "No raw log data available"
            
            prompt = f"""Perform a detailed technical analysis of this security incident:

INCIDENT DETAILS:
- Threat Type: {threat_type}
- Severity: {incident_data.get('severity', 'MEDIUM')}
- Anomaly Score: {incident_data.get('anomaly_score', 0.0):.2%}
- Source IP: {incident_data.get('source_ip', 'N/A')}
- Destination IP: {incident_data.get('destination_ip', 'N/A')}
- Description: {incident_data.get('description', 'N/A')}
- Detected At: {incident_data.get('detected_at', 'N/A')}
- Log Timestamp: {incident_data.get('timestamp', 'N/A')}

RAW LOG DATA:
{log_data_str}

Provide a comprehensive technical analysis covering:
1. Technical Indicators of Compromise (IOCs)
2. Attack Vector Analysis
3. Behavioral Pattern Analysis
4. Impact Assessment (potential damage, affected systems, data at risk)
5. Timeline and Attack Progression
6. Detection Methodology Analysis

Format as a detailed technical report suitable for security analysts."""
            
            ai_analysis = self._call_openai(prompt, system_prompt, max_tokens=1500)
            if ai_analysis:
                return ai_analysis
        
        # Fallback to rule-based
        analysis = f"""
DETAILED TECHNICAL ANALYSIS

Threat Classification: {threat_type}

Log Analysis:
{json.dumps(raw_log, indent=2) if raw_log else "No raw log data available"}

Technical Indicators:
- Anomaly Score: {incident_data.get('anomaly_score', 0.0):.2%}
- Detection Method: AI-Powered Anomaly Detection
- Source: {incident_data.get('source_ip', 'N/A')}
- Destination: {incident_data.get('destination_ip', 'N/A')}

Behavioral Patterns:
The detected activity exhibits characteristics consistent with {threat_type} attacks.
The system has identified multiple indicators of compromise (IOCs) that suggest
this is not a false positive.

Impact Assessment:
Based on the severity level ({incident_data.get('severity', 'MEDIUM')}), 
this incident requires immediate attention. The potential impact includes:
- Unauthorized access to systems
- Data breach risk
- Service disruption
- Compliance violations

Timeline:
- First Detected: {incident_data.get('detected_at', 'N/A')}
- Log Timestamp: {incident_data.get('timestamp', 'N/A')}
"""
        return analysis.strip()
    
    def generate_mitigation_steps(self, incident_data: Dict[str, Any]) -> List[str]:
        """Generate actionable mitigation steps using OpenAI - ensures steps for all threat types"""
        threat_type = incident_data.get("threat_type", "UNKNOWN")
        source_ip = incident_data.get("source_ip")
        severity = incident_data.get("severity", "MEDIUM")
        
        # Try OpenAI first
        if self.openai_enabled:
            system_prompt = """You are a cybersecurity incident response expert. 
Provide clear, actionable, prioritized mitigation steps for security incidents.
Format each step as a numbered list item starting with the action verb.
Steps should be specific, executable, and ordered by priority."""
            
            prompt = f"""Generate prioritized mitigation steps for this security incident:

Threat Type: {threat_type}
Severity: {severity}
Source IP: {source_ip or 'N/A'}
Destination IP: {incident_data.get('destination_ip', 'N/A')}
Description: {incident_data.get('description', 'N/A')}
Anomaly Score: {incident_data.get('anomaly_score', 0.0):.2%}

Provide 6-8 specific, actionable mitigation steps ordered by priority.
Each step should:
- Start with an action verb (e.g., "Block", "Review", "Enable")
- Be specific and executable
- Include technical details where relevant
- Consider the threat type and severity level

Format as a numbered list, one step per line."""
            
            ai_steps = self._call_openai(prompt, system_prompt, max_tokens=600)
            if ai_steps:
                # Parse the response into a list
                steps_list = []
                for line in ai_steps.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                        # Remove numbering/bullets and clean up
                        step = line.lstrip('0123456789.-•) ').strip()
                        if step:
                            steps_list.append(step)
                
                if steps_list:
                    if severity == "CRITICAL":
                        steps_list.insert(0, "URGENT: Escalate to security incident response team immediately")
                    return steps_list
        
        # Fallback to rule-based - ensure steps for ALL threat types
        steps = []
        
        # Base steps for all incidents
        base_steps = [
            "Isolate affected systems from the network if possible",
            "Block the source IP address immediately in firewall rules",
            "Review all logs related to this incident",
            "Check for data exfiltration or unauthorized access",
            "Update security policies and rules",
            "Notify security team and management",
            "Document incident for post-mortem analysis"
        ]
        
        # Threat-specific additional steps
        threat_specific_steps = {
            "brute_force": [
                "Enable account lockout policies for affected user accounts",
                "Review and strengthen password policies",
                "Enable multi-factor authentication (MFA) for all accounts",
                "Monitor affected accounts for unauthorized access",
                "Review authentication logs for other suspicious activity"
            ],
            "port_scan": [
                "Review firewall logs for other scanning attempts",
                "Verify that all exposed ports are necessary and secured",
                "Implement rate limiting on network services",
                "Update intrusion detection rules",
                "Consider implementing honeypots to detect future scans"
            ],
            "port_intrusion": [
                "Review firewall logs for other scanning attempts",
                "Verify that all exposed ports are necessary and secured",
                "Implement rate limiting on network services",
                "Update intrusion detection rules",
                "Consider implementing honeypots to detect future scans"
            ],
            "sql_injection": [
                "Immediately review and sanitize database queries",
                "Implement parameterized queries and prepared statements",
                "Review application logs for successful injection attempts",
                "Check database for unauthorized data access",
                "Update web application firewall (WAF) rules",
                "Conduct security code review for SQL injection vulnerabilities"
            ],
            "ddos": [
                "Activate DDoS mitigation services",
                "Rate limit incoming connections",
                "Block malicious IP ranges",
                "Scale up infrastructure resources if needed",
                "Contact ISP for upstream filtering",
                "Monitor network traffic patterns",
                "Document attack characteristics for future prevention"
            ],
            "malware": [
                "Quarantine affected files and systems",
                "Run antivirus/anti-malware scans",
                "Review system processes for suspicious activity",
                "Check for lateral movement indicators",
                "Update antivirus signatures",
                "Review file integrity monitoring alerts"
            ],
            "ransomware": [
                "Immediately disconnect affected systems from network",
                "Do NOT pay the ransom",
                "Identify the ransomware variant",
                "Check for backup availability",
                "Review file encryption patterns",
                "Contact law enforcement if required",
                "Document ransom note and payment demands"
            ],
            "data_exfiltration": [
                "Immediately block outbound connections if possible",
                "Review data access logs",
                "Identify what data was accessed",
                "Check for unauthorized data transfers",
                "Review user access permissions",
                "Notify data protection officer if required"
            ],
            "network_scanning": [
                "Block the scanning IP address at network perimeter",
                "Review firewall logs for other scanning attempts",
                "Verify that all exposed ports are necessary and secured",
                "Implement rate limiting on network services",
                "Update intrusion detection rules"
            ]
        }
        
        # Combine base steps with threat-specific steps
        if threat_type.lower() in threat_specific_steps:
            steps = threat_specific_steps[threat_type.lower()] + base_steps
        else:
            # For unknown or other threat types, use base steps with generic additions
            steps = [
                f"Investigate {threat_type} threat patterns",
                "Review threat intelligence feeds for similar attacks",
                "Check for indicators of compromise (IOCs)"
            ] + base_steps
        
        # Add critical severity escalation
        if severity == "CRITICAL":
            steps.insert(0, "URGENT: Escalate to security incident response team immediately")
        
        # Ensure we always return at least 5 steps
        if len(steps) < 5:
            steps.extend([
                "Review security monitoring dashboards",
                "Check for related incidents in the past 24 hours"
            ])
        
        return steps[:10]  # Limit to 10 steps max
    
    def generate_mitigation_script(self, incident_data: Dict[str, Any]) -> str:
        """Generate executable mitigation script"""
        threat_type = incident_data.get("threat_type", "UNKNOWN")
        source_ip = incident_data.get("source_ip")
        
        if threat_type == "brute_force" and source_ip:
            script = f"""#!/bin/bash
# Auto-generated mitigation script for {threat_type} attack
# Source IP: {source_ip}
# Generated: {datetime.now().isoformat()}

echo "Blocking source IP: {source_ip}"

# Firewall rule (iptables)
iptables -A INPUT -s {source_ip} -j DROP
iptables -A OUTPUT -d {source_ip} -j DROP

# Save firewall rules
iptables-save > /etc/iptables/rules.v4

# Log the action
echo "$(date): Blocked IP {source_ip} due to {threat_type} attack" >> /var/log/soc_mitigation.log

# Alternative: Using ufw (Ubuntu)
# ufw deny from {source_ip}

# Alternative: Using firewalld (CentOS/RHEL)
# firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="{source_ip}" reject'
# firewall-cmd --reload

echo "Mitigation complete. IP {source_ip} has been blocked."
"""
        elif threat_type == "port_scan" and source_ip:
            script = f"""#!/bin/bash
# Auto-generated mitigation script for {threat_type} attack
# Source IP: {source_ip}
# Generated: {datetime.now().isoformat()}

echo "Blocking port scanning source IP: {source_ip}"

# Block IP
iptables -A INPUT -s {source_ip} -j DROP

# Rate limiting for future scans
iptables -A INPUT -p tcp --dport 1:65535 -m state --state NEW -m recent --set
iptables -A INPUT -p tcp --dport 1:65535 -m state --state NEW -m recent --update --seconds 60 --hitcount 10 -j DROP

iptables-save > /etc/iptables/rules.v4
echo "$(date): Blocked port scanning IP {source_ip}" >> /var/log/soc_mitigation.log

echo "Mitigation complete."
"""
        else:
            script = f"""#!/bin/bash
# Auto-generated mitigation script for {threat_type} attack
# Generated: {datetime.now().isoformat()}

echo "Generic mitigation script for {threat_type}"

# Block source IP if available
if [ ! -z "{source_ip}" ]; then
    iptables -A INPUT -s {source_ip} -j DROP
    echo "$(date): Blocked IP {source_ip}" >> /var/log/soc_mitigation.log
fi

# Review logs
echo "Reviewing security logs..."
tail -n 100 /var/log/auth.log | grep -i suspicious

echo "Mitigation script executed. Please review logs manually."
"""
        
        return script
    
    def generate_report(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete incident report - ensures all fields are populated"""
        # Generate all components
        summary = self.generate_incident_summary(incident_data)
        detailed_analysis = self.generate_detailed_analysis(incident_data)
        mitigation_steps = self.generate_mitigation_steps(incident_data)
        mitigation_script = self.generate_mitigation_script(incident_data)
        
        # Ensure all fields have content (fallback if empty)
        if not summary or len(summary.strip()) < 50:
            threat_type = incident_data.get('threat_type', 'UNKNOWN')
            severity = incident_data.get('severity', 'MEDIUM')
            score = incident_data.get('anomaly_score', 0.0)
            summary = f"Security incident of type {threat_type} with severity {severity} detected. Anomaly score: {score:.2%}. Immediate investigation and response required."
        
        if not detailed_analysis or len(detailed_analysis.strip()) < 100:
            threat_type = incident_data.get('threat_type', 'UNKNOWN')
            source_ip = incident_data.get('source_ip', 'N/A')
            score = incident_data.get('anomaly_score', 0.0)
            detailed_analysis = f"Detailed technical analysis for {threat_type} threat. Source IP: {source_ip}. Anomaly score: {score:.2%}. This incident requires thorough investigation of the attack vector and potential impact."
        
        if not mitigation_steps or len(mitigation_steps) == 0:
            mitigation_steps = self.generate_mitigation_steps(incident_data)
        
        if not mitigation_script or len(mitigation_script.strip()) < 50:
            mitigation_script = self.generate_mitigation_script(incident_data)
        
        return {
            "summary": summary,
            "detailed_analysis": detailed_analysis,
            "mitigation_steps": mitigation_steps,
            "mitigation_script": mitigation_script,
            "generated_at": datetime.now().isoformat()
        }

