"""
Threat Intelligence Service
Integrates external threat intelligence feeds to identify known IOCs
"""
import requests
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json

class ThreatIntelligenceService:
    """Service for checking logs against external threat intelligence feeds"""
    
    def __init__(self):
        self.abuseipdb_api_key = os.getenv("ABUSEIPDB_API_KEY", "")
        self.otx_api_key = os.getenv("OTX_API_KEY", "")
        self.virustotal_api_key = os.getenv("VIRUSTOTAL_API_KEY", "")
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = timedelta(hours=1)
        
    def check_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Check IP address against multiple TI feeds
        Returns: {
            'is_malicious': bool,
            'confidence': float,
            'sources': List[str],
            'details': Dict
        }
        """
        # Check cache first
        cache_key = f"ip:{ip_address}"
        if cache_key in self.cache:
            cached_result, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_result
        
        result = {
            'is_malicious': False,
            'confidence': 0.0,
            'sources': [],
            'details': {}
        }
        
        # Check AbuseIPDB
        abuse_result = self._check_abuseipdb(ip_address)
        if abuse_result['is_malicious']:
            result['is_malicious'] = True
            result['confidence'] = max(result['confidence'], abuse_result['confidence'])
            result['sources'].append('AbuseIPDB')
            result['details']['abuseipdb'] = abuse_result
        
        # Check AlienVault OTX
        otx_result = self._check_otx(ip_address)
        if otx_result['is_malicious']:
            result['is_malicious'] = True
            result['confidence'] = max(result['confidence'], otx_result['confidence'])
            result['sources'].append('AlienVault OTX')
            result['details']['otx'] = otx_result
        
        # Check internal threat intelligence
        internal_result = self._check_internal(ip_address)
        if internal_result['is_malicious']:
            result['is_malicious'] = True
            result['confidence'] = max(result['confidence'], internal_result['confidence'])
            result['sources'].append('Internal TI')
            result['details']['internal'] = internal_result
        
        # Cache result
        self.cache[cache_key] = (result, datetime.now())
        
        return result
    
    def check_hash(self, file_hash: str, hash_type: str = "sha256") -> Dict[str, Any]:
        """
        Check file hash against threat intelligence feeds
        """
        cache_key = f"hash:{hash_type}:{file_hash}"
        if cache_key in self.cache:
            cached_result, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_result
        
        result = {
            'is_malicious': False,
            'confidence': 0.0,
            'sources': [],
            'details': {}
        }
        
        # Check VirusTotal
        vt_result = self._check_virustotal(file_hash, hash_type)
        if vt_result['is_malicious']:
            result['is_malicious'] = True
            result['confidence'] = max(result['confidence'], vt_result['confidence'])
            result['sources'].append('VirusTotal')
            result['details']['virustotal'] = vt_result
        
        # Check internal threat intelligence
        internal_result = self._check_internal_hash(file_hash, hash_type)
        if internal_result['is_malicious']:
            result['is_malicious'] = True
            result['confidence'] = internal_result['confidence']
            result['sources'].append('Internal TI')
            result['details']['internal'] = internal_result
        
        self.cache[cache_key] = (result, datetime.now())
        return result
    
    def check_domain(self, domain: str) -> Dict[str, Any]:
        """
        Check domain against threat intelligence feeds
        """
        cache_key = f"domain:{domain}"
        if cache_key in self.cache:
            cached_result, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_result
        
        result = {
            'is_malicious': False,
            'confidence': 0.0,
            'sources': [],
            'details': {}
        }
        
        # Check internal threat intelligence
        internal_result = self._check_internal_domain(domain)
        if internal_result['is_malicious']:
            result['is_malicious'] = True
            result['confidence'] = internal_result['confidence']
            result['sources'].append('Internal TI')
            result['details']['internal'] = internal_result
        
        self.cache[cache_key] = (result, datetime.now())
        return result
    
    def _check_abuseipdb(self, ip_address: str) -> Dict[str, Any]:
        """Check IP against AbuseIPDB"""
        if not self.abuseipdb_api_key:
            return {'is_malicious': False, 'confidence': 0.0}
        
        try:
            url = "https://api.abuseipdb.com/api/v2/check"
            headers = {
                'Key': self.abuseipdb_api_key,
                'Accept': 'application/json'
            }
            params = {
                'ipAddress': ip_address,
                'maxAgeInDays': 90,
                'verbose': ''
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                abuse_confidence = data.get('data', {}).get('abuseConfidenceScore', 0)
                is_malicious = abuse_confidence >= 25  # AbuseIPDB threshold
                
                return {
                    'is_malicious': is_malicious,
                    'confidence': abuse_confidence / 100.0,
                    'abuse_score': abuse_confidence,
                    'usage_type': data.get('data', {}).get('usageType', 'unknown'),
                    'country': data.get('data', {}).get('countryCode', 'unknown')
                }
        except Exception as e:
            print(f"AbuseIPDB check failed: {e}")
        
        return {'is_malicious': False, 'confidence': 0.0}
    
    def _check_otx(self, ip_address: str) -> Dict[str, Any]:
        """Check IP against AlienVault OTX"""
        if not self.otx_api_key:
            return {'is_malicious': False, 'confidence': 0.0}
        
        try:
            url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip_address}/general"
            headers = {
                'X-OTX-API-KEY': self.otx_api_key
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                pulse_count = data.get('pulse_info', {}).get('count', 0)
                is_malicious = pulse_count > 0
                
                return {
                    'is_malicious': is_malicious,
                    'confidence': min(pulse_count / 10.0, 1.0),  # Cap at 1.0
                    'pulse_count': pulse_count,
                    'references': data.get('pulse_info', {}).get('references', [])
                }
        except Exception as e:
            print(f"OTX check failed: {e}")
        
        return {'is_malicious': False, 'confidence': 0.0}
    
    def _check_internal(self, ip_address: str) -> Dict[str, Any]:
        """Check against internal threat intelligence database"""
        try:
            from database import SessionLocal
            from models import ThreatIntelligence
            
            db = SessionLocal()
            try:
                # Check if IP exists in threat intelligence
                ti_record = db.query(ThreatIntelligence).filter(
                    ThreatIntelligence.ioc_type == "ip",
                    ThreatIntelligence.ioc_value == ip_address
                ).first()
                
                if ti_record:
                    # Calculate confidence based on detection count and severity
                    detection_count = ti_record.detection_count or 1
                    severity_multiplier = {
                        'CRITICAL': 1.0,
                        'HIGH': 0.8,
                        'MEDIUM': 0.6,
                        'LOW': 0.4
                    }.get(ti_record.severity, 0.5)
                    
                    confidence = min(detection_count * 0.1 * severity_multiplier, 1.0)
                    
                    return {
                        'is_malicious': True,
                        'confidence': confidence,
                        'threat_type': ti_record.threat_type,
                        'severity': ti_record.severity,
                        'detection_count': detection_count,
                        'first_seen': ti_record.first_seen.isoformat() if ti_record.first_seen else None,
                        'last_seen': ti_record.last_seen.isoformat() if ti_record.last_seen else None,
                        'source': 'Internal TI Database'
                    }
            finally:
                db.close()
        except Exception as e:
            print(f"Internal TI check failed: {e}")
        
        return {'is_malicious': False, 'confidence': 0.0}
    
    def _check_internal_hash(self, file_hash: str, hash_type: str) -> Dict[str, Any]:
        """Check hash against internal threat intelligence"""
        try:
            from database import SessionLocal
            from models import ThreatIntelligence
            
            db = SessionLocal()
            try:
                ti_record = db.query(ThreatIntelligence).filter(
                    ThreatIntelligence.ioc_type == hash_type.lower(),
                    ThreatIntelligence.ioc_value == file_hash.lower()
                ).first()
                
                if ti_record:
                    detection_count = ti_record.detection_count or 1
                    severity_multiplier = {
                        'CRITICAL': 1.0,
                        'HIGH': 0.8,
                        'MEDIUM': 0.6,
                        'LOW': 0.4
                    }.get(ti_record.severity, 0.5)
                    
                    confidence = min(detection_count * 0.1 * severity_multiplier, 1.0)
                    
                    return {
                        'is_malicious': True,
                        'confidence': confidence,
                        'threat_type': ti_record.threat_type,
                        'severity': ti_record.severity,
                        'source': 'Internal TI Database'
                    }
            finally:
                db.close()
        except Exception as e:
            print(f"Internal hash TI check failed: {e}")
        
        return {'is_malicious': False, 'confidence': 0.0}
    
    def _check_internal_domain(self, domain: str) -> Dict[str, Any]:
        """Check domain against internal threat intelligence"""
        try:
            from database import SessionLocal
            from models import ThreatIntelligence
            
            db = SessionLocal()
            try:
                ti_record = db.query(ThreatIntelligence).filter(
                    ThreatIntelligence.ioc_type == "domain",
                    ThreatIntelligence.ioc_value == domain.lower()
                ).first()
                
                if ti_record:
                    detection_count = ti_record.detection_count or 1
                    severity_multiplier = {
                        'CRITICAL': 1.0,
                        'HIGH': 0.8,
                        'MEDIUM': 0.6,
                        'LOW': 0.4
                    }.get(ti_record.severity, 0.5)
                    
                    confidence = min(detection_count * 0.1 * severity_multiplier, 1.0)
                    
                    return {
                        'is_malicious': True,
                        'confidence': confidence,
                        'threat_type': ti_record.threat_type,
                        'severity': ti_record.severity,
                        'source': 'Internal TI Database'
                    }
            finally:
                db.close()
        except Exception as e:
            print(f"Internal domain TI check failed: {e}")
        
        return {'is_malicious': False, 'confidence': 0.0}
    
    def enrich_log_with_ti(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich log data with threat intelligence information
        Returns log_data with added 'threat_intelligence' field
        """
        ti_data = {
            'source_ip_ti': None,
            'destination_ip_ti': None,
            'file_hash_ti': None,
            'domain_ti': None,
            'has_known_ioc': False,
            'ti_confidence': 0.0
        }
        
        # Check source IP
        if 'source_ip' in log_data:
            source_ti = self.check_ip(log_data['source_ip'])
            ti_data['source_ip_ti'] = source_ti
            if source_ti['is_malicious']:
                ti_data['has_known_ioc'] = True
                ti_data['ti_confidence'] = max(ti_data['ti_confidence'], source_ti['confidence'])
        
        # Check destination IP
        if 'destination_ip' in log_data:
            dest_ti = self.check_ip(log_data['destination_ip'])
            ti_data['destination_ip_ti'] = dest_ti
            if dest_ti['is_malicious']:
                ti_data['has_known_ioc'] = True
                ti_data['ti_confidence'] = max(ti_data['ti_confidence'], dest_ti['confidence'])
        
        # Check file hash if present
        if 'file_hash' in log_data:
            hash_ti = self.check_hash(log_data['file_hash'])
            ti_data['file_hash_ti'] = hash_ti
            if hash_ti['is_malicious']:
                ti_data['has_known_ioc'] = True
                ti_data['ti_confidence'] = max(ti_data['ti_confidence'], hash_ti['confidence'])
        
        # Check domain if present
        if 'domain' in log_data:
            domain_ti = self.check_domain(log_data['domain'])
            ti_data['domain_ti'] = domain_ti
            if domain_ti['is_malicious']:
                ti_data['has_known_ioc'] = True
                ti_data['ti_confidence'] = max(ti_data['ti_confidence'], domain_ti['confidence'])
        
        log_data['threat_intelligence'] = ti_data
        return log_data

# Global instance
threat_intelligence_service = ThreatIntelligenceService()

