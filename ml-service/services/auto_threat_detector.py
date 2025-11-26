"""
Auto Threat Detection Service
Uses Deep Learning and Generative AI to automatically detect and analyze threats
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, Tuple, List
from datetime import datetime
import json
from services.anomaly_detector import AnomalyDetector
from services.generative_ai import GenerativeAIService
from services.active_defense import ActiveDefenseService
from database import SessionLocal
from models import Incident, IncidentReport
import uuid
import asyncio

class EnhancedThreatDetectionModel(nn.Module):
    """Enhanced Transformer-based model for threat detection"""
    def __init__(self, input_size=128, d_model=256, nhead=8, num_layers=4, num_classes=2):
        super(EnhancedThreatDetectionModel, self).__init__()
        self.embedding = nn.Linear(input_size, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=512,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.classifier = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )
        
    def forward(self, x):
        x = self.embedding(x)
        x = self.transformer(x)
        x = x[:, -1, :]  # Take last sequence output
        x = self.classifier(x)
        return x

class AutoThreatDetector:
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.generative_ai = GenerativeAIService()
        self.active_defense = ActiveDefenseService()  # Real-time blocking
        self.enhanced_model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._initialize_enhanced_model()
        self.threat_patterns = self._load_threat_patterns()
    
    def _initialize_enhanced_model(self):
        """Initialize enhanced deep learning model"""
        try:
            self.enhanced_model = EnhancedThreatDetectionModel()
            # In production, load pre-trained weights
            # self.enhanced_model.load_state_dict(torch.load('models/enhanced_threat_model.pth'))
            self.enhanced_model.eval()
            print("Enhanced threat detection model initialized")
        except Exception as e:
            print(f"Warning: Enhanced model not available, using fallback: {e}")
            self.enhanced_model = None
    
    def _load_threat_patterns(self) -> Dict[str, List[str]]:
        """Load comprehensive threat patterns for detection - Windows Security style"""
        return {
            "malware": [
                "malware", "trojan", "backdoor", "rootkit", "spyware", "adware",
                "keylogger", "botnet", "command and control", "c2 server",
                "suspicious executable", "unknown process", "malicious file"
            ],
            "virus": [
                "virus", "infected", "worm", "payload", "exploit", "infection",
                "virus signature", "antivirus", "quarantine", "cleanup"
            ],
            "port_intrusion": [
                "port scan", "port intrusion", "unauthorized port access",
                "port enumeration", "port probe", "connection attempt",
                "syn flood", "tcp scan", "udp scan", "stealth scan"
            ],
            "network_scanning": [
                "network scan", "host discovery", "service enumeration",
                "vulnerability scan", "reconnaissance", "network probe",
                "ping sweep", "arp scan", "network mapping"
            ],
            "zero_day": [
                "unusual process", "unknown signature", "anomalous behavior",
                "suspicious pattern", "unidentified", "novel attack", "zero day"
            ],
            "advanced_persistent_threat": [
                "long-term", "persistent", "covert", "stealth", "dormant",
                "lateral movement", "privilege escalation", "apt"
            ],
            "ransomware": [
                "encryption", "ransom", "bitcoin", "payment", "decrypt",
                "files locked", "crypto", "extortion", "ransomware"
            ],
            "brute_force": [
                "brute force", "password attack", "credential stuffing",
                "dictionary attack", "login attempt", "authentication failed",
                "multiple failed logins", "account lockout"
            ],
            "ddos": [
                "ddos", "distributed denial", "flood", "overload", "traffic spike",
                "syn flood", "udp flood", "icmp flood", "http flood"
            ],
            "sql_injection": [
                "sql injection", "union select", "drop table", "sql error",
                "database query", "sql attack", "injection attempt"
            ],
            "xss": [
                "xss", "cross-site scripting", "script injection", "javascript injection",
                "dom manipulation", "reflected xss", "stored xss"
            ],
            "data_exfiltration": [
                "large transfer", "data export", "bulk download", "unauthorized access",
                "sensitive data", "confidential", "massive upload", "data breach"
            ],
            "insider_threat": [
                "internal user", "privileged access", "unauthorized access",
                "data access", "after hours", "unusual time"
            ],
            "iot_attack": [
                "iot device", "smart device", "sensor", "embedded",
                "device compromise", "firmware"
            ],
            "cloud_breach": [
                "cloud service", "s3 bucket", "api key", "cloud storage",
                "unauthorized cloud", "misconfigured"
            ],
            "phishing": [
                "phishing", "suspicious email", "malicious link", "social engineering",
                "credential harvest", "fake website"
            ],
            "man_in_the_middle": [
                "mitm", "man in the middle", "ssl strip", "certificate",
                "intercepted", "proxy attack"
            ]
        }
    
    def detect_threat_with_ai(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically detect threat using deep learning and generate AI analysis
        Returns comprehensive threat analysis
        """
        # Step 0: Threat Intelligence Check (before ML processing)
        from services.threat_intelligence import threat_intelligence_service
        log_data = threat_intelligence_service.enrich_log_with_ti(log_data)
        ti_data = log_data.get('threat_intelligence', {})
        has_known_ioc = ti_data.get('has_known_ioc', False)
        ti_confidence = ti_data.get('ti_confidence', 0.0)
        
        # If known IOC found, create deterministic alert
        if has_known_ioc and ti_confidence > 0.7:
            return {
                'is_threat': True,
                'anomaly_score': ti_confidence,
                'threat_type': 'Known IOC',
                'severity': 'HIGH' if ti_confidence > 0.8 else 'MEDIUM',
                'is_zero_day': False,
                'threat_intelligence': ti_data,
                'detection_method': 'Threat Intelligence',
                'confidence': ti_confidence
            }
        
        # Step 1: Deep Learning Detection
        is_anomaly, anomaly_score, threat_type = self.anomaly_detector.detect_anomaly(log_data)
        
        # Step 1.5: Apply Adaptive Threshold
        from services.adaptive_threshold import adaptive_threshold_service
        context = self._get_detection_context(log_data)
        adaptive_threshold = adaptive_threshold_service.get_threshold(context)
        
        # Adjust anomaly detection based on adaptive threshold
        is_anomaly = anomaly_score >= adaptive_threshold
        
        # Step 2: Enhanced Pattern Matching
        enhanced_threat_type = self._detect_enhanced_threat_type(log_data, threat_type)
        
        # Step 3: Zero-day Detection
        is_zero_day = self._detect_zero_day(log_data, anomaly_score)
        
        # Step 4: Threat Severity Assessment (using adaptive threshold)
        from services.adaptive_threshold import adaptive_threshold_service
        severity = adaptive_threshold_service.get_severity_from_score(anomaly_score, context)
        
        # Enhance severity if TI data exists
        if has_known_ioc and severity in ['LOW', 'MEDIUM']:
            severity = 'HIGH'  # Known IOC always gets at least HIGH severity
        
        # Step 4.5: Generate XAI Explanation
        xai_explanation = None
        if is_anomaly or anomaly_score > 0.5:
            try:
                from services.xai_explainer import xai_explainer
                xai_explanation = xai_explainer.explain_feature_importance(log_data)
            except Exception as e:
                print(f"XAI explanation generation failed: {e}")
        
        # Step 5: Generate AI-Powered Analysis
        threat_analysis = self._generate_threat_analysis(
            log_data, enhanced_threat_type, severity, is_zero_day, anomaly_score
        )
        
        # Step 6: Auto-create Incident if threat detected
        incident_id = None
        blocking_result = None
        
        if is_anomaly or severity in ["HIGH", "CRITICAL"]:
            incident_id = self._auto_create_incident(
                log_data, enhanced_threat_type, severity, anomaly_score, threat_analysis
            )
            
            # Step 7: Real-time blocking (Windows Security style)
            threat_data = {
                "threat_type": enhanced_threat_type,
                "severity": severity,
                "source_ip": log_data.get("metadata", {}).get("ip") or log_data.get("metadata", {}).get("source_ip"),
                "metadata": log_data.get("metadata", {})
            }
            
            # Block threat in real-time (async)
            try:
                import asyncio
                # Create a new event loop for blocking
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                if loop.is_running():
                    # Schedule blocking as a task
                    blocking_result = {"blocked": True, "async": True}
                    asyncio.create_task(self.active_defense.block_threat(threat_data))
                else:
                    blocking_result = loop.run_until_complete(
                        self.active_defense.block_threat(threat_data)
                    )
            except Exception as e:
                print(f"Error in real-time blocking: {e}")
                blocking_result = {"blocked": False, "error": str(e)}
        
        return {
            "threat_detected": is_anomaly or severity in ["HIGH", "CRITICAL"] or has_known_ioc,
            "threat_type": enhanced_threat_type,
            "original_threat_type": threat_type,
            "severity": severity,
            "anomaly_score": float(anomaly_score),
            "is_zero_day": is_zero_day,
            "ai_analysis": threat_analysis,
            "incident_id": incident_id,
            "blocked": blocking_result is not None and blocking_result.get("blocked", False),
            "blocking_result": blocking_result if isinstance(blocking_result, dict) else None,
            "recommendations": self._generate_recommendations(enhanced_threat_type, severity),
            "detected_at": datetime.now().isoformat(),
            "threat_intelligence": ti_data,
            "has_known_ioc": has_known_ioc,
            "adaptive_threshold": adaptive_threshold,
            "detection_method": "Threat Intelligence" if has_known_ioc and ti_confidence > 0.7 else "ML Detection",
            "xai_explanation": xai_explanation
        }
    
    def _detect_enhanced_threat_type(self, log_data: Dict[str, Any], base_threat_type: str) -> str:
        """Enhanced threat type detection using pattern matching - Windows Security style"""
        message = str(log_data.get("message", "")).lower()
        metadata = log_data.get("metadata", {})
        source = str(log_data.get("source", "")).lower()
        
        # Priority-based detection (most specific first)
        # Check against enhanced threat patterns
        for threat_type, patterns in self.threat_patterns.items():
            if any(pattern in message for pattern in patterns):
                return threat_type
        
        # Check metadata for specific indicators
        if "encryption" in message or "ransom" in message or "bitcoin" in message:
            return "ransomware"
        if "malware" in message or "trojan" in message or "virus" in message:
            return "malware" if "virus" not in message else "virus"
        if "port" in message and ("scan" in message or "intrusion" in message):
            return "port_intrusion"
        if "scan" in message or "reconnaissance" in message:
            return "network_scanning"
        if "cloud" in message or "s3" in message or "api key" in message:
            return "cloud_breach"
        if "iot" in message or "device" in message:
            return "iot_attack"
        if source == "firewall" and ("blocked" in message or "denied" in message):
            return "port_intrusion"
        
        return base_threat_type or "unknown_threat"
    
    def _get_detection_context(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get context for adaptive threshold calculation"""
        from datetime import datetime
        from services.adaptive_threshold import adaptive_threshold_service
        now = datetime.now()
        return {
            'current_hour': now.hour,
            'day_of_week': now.weekday(),
            'recent_false_positive_rate': adaptive_threshold_service.false_positive_rate,
            'network_load': 0.5,  # Could be calculated from recent log volume
            'recent_incident_count': 0  # Could be queried from database
        }
    
    def _detect_zero_day(self, log_data: Dict[str, Any], anomaly_score: float) -> bool:
        """Detect potential zero-day attacks"""
        message = str(log_data.get("message", "")).lower()
        
        # Zero-day indicators
        zero_day_indicators = [
            "unknown", "unidentified", "novel", "new pattern",
            "unseen", "unrecognized", "anomalous", "unusual"
        ]
        
        # High anomaly score with unknown patterns
        if anomaly_score > 0.7:
            if any(indicator in message for indicator in zero_day_indicators):
                return True
            # Check if threat type is unknown but score is high
            if "unknown" in message or "unidentified" in message:
                return True
        
        return False
    
    def _assess_threat_severity(self, anomaly_score: float, threat_type: str, is_zero_day: bool) -> str:
        """Assess threat severity using AI logic"""
        base_severity = "LOW"
        
        if anomaly_score > 0.8:
            base_severity = "CRITICAL"
        elif anomaly_score > 0.6:
            base_severity = "HIGH"
        elif anomaly_score > 0.4:
            base_severity = "MEDIUM"
        
        # Zero-day attacks are always high severity
        if is_zero_day:
            base_severity = "CRITICAL" if base_severity != "CRITICAL" else "CRITICAL"
        
        # Critical threat types
        critical_types = ["ransomware", "data_exfiltration", "advanced_persistent_threat"]
        if threat_type in critical_types:
            if base_severity == "LOW":
                base_severity = "MEDIUM"
            elif base_severity == "MEDIUM":
                base_severity = "HIGH"
        
        return base_severity
    
    def _generate_threat_analysis(self, log_data: Dict[str, Any], threat_type: str, 
                                  severity: str, is_zero_day: bool, score: float) -> Dict[str, Any]:
        """Generate comprehensive AI-powered threat analysis"""
        message = log_data.get("message", "")
        metadata = log_data.get("metadata", {})
        
        # Use Generative AI to create detailed analysis
        analysis_prompt = {
            "threat_type": threat_type,
            "severity": severity,
            "is_zero_day": is_zero_day,
            "anomaly_score": score,
            "message": message,
            "metadata": metadata,
            "timestamp": log_data.get("timestamp", datetime.now().isoformat())
        }
        
        # Prepare incident data for AI report generation
        incident_data = {
            "threat_type": threat_type,
            "severity": severity,
            "source_ip": metadata.get("ip") or metadata.get("source_ip"),
            "destination_ip": metadata.get("destination_ip"),
            "description": message,
            "anomaly_score": score,
            "timestamp": log_data.get("timestamp", datetime.now().isoformat()),
            "raw_log_data": log_data
        }
        
        # Generate AI analysis
        ai_report = self.generative_ai.generate_report(incident_data)
        
        # Enhanced analysis
        enhanced_analysis = {
            "threat_classification": {
                "primary_type": threat_type,
                "severity": severity,
                "confidence": score,
                "zero_day_indicator": is_zero_day
            },
            "technical_analysis": {
                "log_analysis": message,
                "indicators_of_compromise": self._extract_iocs(log_data),
                "attack_vector": self._identify_attack_vector(log_data, threat_type),
                "potential_impact": self._assess_impact(threat_type, severity)
            },
            "ai_generated_summary": ai_report.get("summary", ""),
            "ai_detailed_analysis": ai_report.get("detailed_analysis", ""),
            "mitigation_strategy": {
                "mitigation_steps": ai_report.get("mitigation_steps", []),
                "mitigation_script": ai_report.get("mitigation_script", "")
            }
        }
        
        return enhanced_analysis
    
    def _extract_iocs(self, log_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract Indicators of Compromise"""
        iocs = []
        metadata = log_data.get("metadata", {})
        
        if "ip" in metadata:
            iocs.append({"type": "IP Address", "value": metadata["ip"], "severity": "HIGH"})
        if "source_ip" in metadata:
            iocs.append({"type": "Source IP", "value": metadata["source_ip"], "severity": "HIGH"})
        if "destination_ip" in metadata:
            iocs.append({"type": "Destination IP", "value": metadata["destination_ip"], "severity": "MEDIUM"})
        if "port" in metadata:
            iocs.append({"type": "Port", "value": str(metadata["port"]), "severity": "MEDIUM"})
        
        # Extract from message
        message = str(log_data.get("message", ""))
        if "hash" in message.lower() or "md5" in message.lower():
            # Try to extract hash
            import re
            hash_pattern = r'\b[a-fA-F0-9]{32,64}\b'
            hashes = re.findall(hash_pattern, message)
            for h in hashes:
                iocs.append({"type": "File Hash", "value": h, "severity": "HIGH"})
        
        return iocs
    
    def _identify_attack_vector(self, log_data: Dict[str, Any], threat_type: str) -> str:
        """Identify the attack vector"""
        message = str(log_data.get("message", "")).lower()
        source = log_data.get("source", "").lower()
        
        if "sql" in message or "injection" in message:
            return "SQL Injection via Web Application"
        if "xss" in message or "script" in message:
            return "Cross-Site Scripting (XSS)"
        if "brute" in message or "login" in message:
            return "Brute Force Authentication Attack"
        if "port" in message or "scan" in message:
            return "Network Reconnaissance / Port Scanning"
        if "ddos" in message or "flood" in message:
            return "Distributed Denial of Service (DDoS)"
        if source == "firewall":
            return "Network Perimeter Attack"
        if source == "application":
            return "Application Layer Attack"
        
        return f"Unknown Attack Vector - {threat_type}"
    
    def _assess_impact(self, threat_type: str, severity: str) -> str:
        """Assess potential impact of the threat"""
        impact_map = {
            "ransomware": "Critical: Data encryption, business disruption, financial loss",
            "data_exfiltration": "High: Sensitive data breach, compliance violations, reputation damage",
            "advanced_persistent_threat": "Critical: Long-term compromise, intellectual property theft",
            "zero_day": "Critical: Unknown attack vector, no existing defenses",
            "cloud_breach": "High: Cloud infrastructure compromise, data exposure",
            "iot_attack": "Medium-High: Device compromise, network infiltration"
        }
        
        base_impact = impact_map.get(threat_type, "Medium: System compromise, potential data loss")
        
        if severity == "CRITICAL":
            return f"CRITICAL IMPACT: {base_impact}"
        elif severity == "HIGH":
            return f"HIGH IMPACT: {base_impact}"
        else:
            return base_impact
    
    def _generate_recommendations(self, threat_type: str, severity: str) -> List[str]:
        """Generate AI-powered recommendations"""
        recommendations = []
        
        if severity == "CRITICAL":
            recommendations.append("🚨 IMMEDIATE ACTION REQUIRED: Isolate affected systems immediately")
            recommendations.append("🚨 Escalate to incident response team")
        
        if threat_type == "zero_day":
            recommendations.append("⚠️ Zero-day threat detected - update threat intelligence immediately")
            recommendations.append("⚠️ Implement additional monitoring and behavioral analysis")
        
        recommendations.append(f"Review and strengthen defenses against {threat_type} attacks")
        recommendations.append("Update security policies and access controls")
        recommendations.append("Conduct post-incident analysis and update playbooks")
        
        return recommendations
    
    def _auto_create_incident(self, log_data: Dict[str, Any], threat_type: str, 
                             severity: str, score: float, analysis: Dict[str, Any]) -> str:
        """Automatically create incident with AI-generated report"""
        db = SessionLocal()
        try:
            incident_id = str(uuid.uuid4())
            metadata = log_data.get("metadata", {})
            
            # Create incident
            incident = Incident(
                incident_id=incident_id,
                log_id=log_data.get("id"),
                severity=severity,
                status="OPEN",
                threat_type=threat_type,
                source_ip=metadata.get("ip") or metadata.get("source_ip"),
                destination_ip=metadata.get("destination_ip"),
                timestamp=datetime.fromisoformat(
                    log_data.get("timestamp").replace("Z", "+00:00")
                ) if isinstance(log_data.get("timestamp"), str) else datetime.now(),
                anomaly_score=score,
                description=log_data.get("message", ""),
                raw_log_data=log_data
            )
            db.add(incident)
            db.commit()
            db.refresh(incident)
            
            # Auto-generate AI report - ensure all fields are populated
            mitigation_strategy = analysis.get("mitigation_strategy", {})
            mitigation_steps_list = mitigation_strategy.get("mitigation_steps", [])
            
            # Ensure mitigation_steps is a list
            if isinstance(mitigation_steps_list, str):
                try:
                    import json
                    mitigation_steps_list = json.loads(mitigation_steps_list)
                except:
                    mitigation_steps_list = [mitigation_steps_list] if mitigation_steps_list else []
            elif not isinstance(mitigation_steps_list, list):
                mitigation_steps_list = []
            
            # If no mitigation steps, generate them
            if not mitigation_steps_list or len(mitigation_steps_list) == 0:
                from services.generative_ai import GenerativeAIService
                gen_ai = GenerativeAIService()
                incident_data_for_report = {
                    "threat_type": threat_type,
                    "severity": severity,
                    "source_ip": metadata.get("ip") or metadata.get("source_ip"),
                    "destination_ip": metadata.get("destination_ip"),
                    "description": log_data.get("message", ""),
                    "anomaly_score": score,
                    "timestamp": log_data.get("timestamp", datetime.now().isoformat()),
                    "raw_log_data": log_data
                }
                mitigation_steps_list = gen_ai.generate_mitigation_steps(incident_data_for_report)
            
            # Ensure summary and detailed_analysis exist
            summary = analysis.get("ai_generated_summary", "")
            if not summary:
                from services.generative_ai import GenerativeAIService
                gen_ai = GenerativeAIService()
                incident_data_for_report = {
                    "threat_type": threat_type,
                    "severity": severity,
                    "source_ip": metadata.get("ip") or metadata.get("source_ip"),
                    "destination_ip": metadata.get("destination_ip"),
                    "description": log_data.get("message", ""),
                    "anomaly_score": score,
                    "timestamp": log_data.get("timestamp", datetime.now().isoformat()),
                    "raw_log_data": log_data
                }
                summary = gen_ai.generate_incident_summary(incident_data_for_report)
            
            detailed_analysis = analysis.get("ai_detailed_analysis", "")
            if not detailed_analysis:
                from services.generative_ai import GenerativeAIService
                gen_ai = GenerativeAIService()
                incident_data_for_report = {
                    "threat_type": threat_type,
                    "severity": severity,
                    "source_ip": metadata.get("ip") or metadata.get("source_ip"),
                    "destination_ip": metadata.get("destination_ip"),
                    "description": log_data.get("message", ""),
                    "anomaly_score": score,
                    "timestamp": log_data.get("timestamp", datetime.now().isoformat()),
                    "raw_log_data": log_data
                }
                detailed_analysis = gen_ai.generate_detailed_analysis(incident_data_for_report)
            
            mitigation_script = mitigation_strategy.get("mitigation_script", "")
            if not mitigation_script:
                from services.generative_ai import GenerativeAIService
                gen_ai = GenerativeAIService()
                incident_data_for_report = {
                    "threat_type": threat_type,
                    "severity": severity,
                    "source_ip": metadata.get("ip") or metadata.get("source_ip"),
                    "destination_ip": metadata.get("destination_ip"),
                    "description": log_data.get("message", ""),
                    "anomaly_score": score,
                    "timestamp": log_data.get("timestamp", datetime.now().isoformat()),
                    "raw_log_data": log_data
                }
                mitigation_script = gen_ai.generate_mitigation_script(incident_data_for_report)
            
            # Ensure mitigation_steps_list is a proper list (will be stored as JSON)
            if not isinstance(mitigation_steps_list, list):
                mitigation_steps_list = [str(mitigation_steps_list)] if mitigation_steps_list else []
            
            report = IncidentReport(
                incident_id=incident_id,
                summary=summary,
                detailed_analysis=detailed_analysis,
                mitigation_steps=mitigation_steps_list,  # List will be stored as JSON
                mitigation_script=mitigation_script
            )
            db.add(report)
            db.commit()
            
            print(f"✅ Auto-created incident {incident_id} for {threat_type} threat")
            return incident_id
            
        except Exception as e:
            db.rollback()
            print(f"Error auto-creating incident: {e}")
            return None
        finally:
            db.close()

