"""
Auto Threat Detection Router
Uses Deep Learning and Generative AI to automatically detect and analyze threats
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from services.auto_threat_detector import AutoThreatDetector
from database import get_db
from sqlalchemy.orm import Session
from models import Incident, IncidentReport
from datetime import datetime, timedelta
import json

router = APIRouter()

# Lazy initialization to avoid startup issues
_auto_threat_detector = None

def get_auto_threat_detector():
    """Lazy initialization of AutoThreatDetector"""
    global _auto_threat_detector
    if _auto_threat_detector is None:
        _auto_threat_detector = AutoThreatDetector()
    return _auto_threat_detector

class ThreatDetectionRequest(BaseModel):
    logId: Optional[str] = None
    logData: Dict[str, Any]

class ThreatDetectionResponse(BaseModel):
    threat_detected: bool
    threat_type: str
    severity: str
    anomaly_score: float
    is_zero_day: bool
    ai_analysis: Dict[str, Any]
    incident_id: Optional[str] = None
    recommendations: List[str]
    detected_at: str

@router.post("/auto-detect", response_model=ThreatDetectionResponse)
async def auto_detect_threat(request: ThreatDetectionRequest):
    """
    Automatically detect threats using Deep Learning and Generative AI
    Returns comprehensive threat analysis with AI-generated insights
    """
    try:
        # Use auto threat detector (lazy initialization)
        detector = get_auto_threat_detector()
        result = detector.detect_threat_with_ai(request.logData)
        
        return ThreatDetectionResponse(
            threat_detected=result["threat_detected"],
            threat_type=result["threat_type"],
            severity=result["severity"],
            anomaly_score=result["anomaly_score"],
            is_zero_day=result["is_zero_day"],
            ai_analysis=result["ai_analysis"],
            incident_id=result["incident_id"],
            recommendations=result["recommendations"],
            detected_at=result["detected_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto threat detection error: {str(e)}")

@router.get("/recent-auto-detected")
async def get_recent_auto_detected_threats(limit: int = 20, db: Session = Depends(get_db)):
    """Get recently auto-detected threats with AI analysis"""
    try:
        # Get recent incidents with AI reports
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        incidents = db.query(Incident).filter(
            Incident.timestamp >= cutoff_time
        ).order_by(
            Incident.timestamp.desc()
        ).limit(limit).all()
        
        result = []
        for incident in incidents:
            # Get AI report if available
            report = db.query(IncidentReport).filter(
                IncidentReport.incident_id == incident.incident_id
            ).first()
            
            # Extract AI analysis from raw log data
            ai_analysis = {}
            if incident.raw_log_data:
                raw_data = incident.raw_log_data if isinstance(incident.raw_log_data, dict) else json.loads(incident.raw_log_data)
                if "ai_analysis" in raw_data:
                    ai_analysis = raw_data["ai_analysis"]
            
            result.append({
                "incident_id": incident.incident_id,
                "threat_type": incident.threat_type,
                "severity": incident.severity,
                "anomaly_score": float(incident.anomaly_score),
                "source_ip": incident.source_ip,
                "destination_ip": incident.destination_ip,
                "status": incident.status,
                "detected_at": incident.timestamp.isoformat(),
                "description": incident.description,
                "ai_summary": report.summary if report else ai_analysis.get("ai_generated_summary", ""),
                "ai_detailed_analysis": report.detailed_analysis if report else ai_analysis.get("ai_detailed_analysis", ""),
                "iocs": ai_analysis.get("technical_analysis", {}).get("indicators_of_compromise", []),
                "attack_vector": ai_analysis.get("technical_analysis", {}).get("attack_vector", ""),
                "potential_impact": ai_analysis.get("technical_analysis", {}).get("potential_impact", ""),
                "mitigation_steps": report.mitigation_steps if report else ai_analysis.get("mitigation_strategy", {}).get("mitigation_steps", []),
                "mitigation_script": report.mitigation_script if report else ai_analysis.get("mitigation_strategy", {}).get("mitigation_script", "")
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching auto-detected threats: {str(e)}")

@router.get("/live-threats")
async def get_live_threats(limit: int = 10, db: Session = Depends(get_db)):
    """Get live/real-time threats detected in the last hour"""
    try:
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        incidents = db.query(Incident).filter(
            Incident.timestamp >= cutoff_time,
            Incident.status == "OPEN"
        ).order_by(
            Incident.timestamp.desc()
        ).limit(limit).all()
        
        result = []
        for incident in incidents:
            result.append({
                "incident_id": incident.incident_id,
                "threat_type": incident.threat_type,
                "severity": incident.severity,
                "anomaly_score": float(incident.anomaly_score),
                "source_ip": incident.source_ip,
                "detected_at": incident.timestamp.isoformat(),
                "description": incident.description[:100] + "..." if len(incident.description) > 100 else incident.description
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching live threats: {str(e)}")

@router.get("/threat-stats")
async def get_threat_stats(db: Session = Depends(get_db)):
    """Get statistics about auto-detected threats"""
    try:
        total_threats = db.query(Incident).count()
        zero_day_count = db.query(Incident).filter(
            Incident.raw_log_data.contains('"is_zero_day": true')
        ).count()
        
        last_24h = db.query(Incident).filter(
            Incident.timestamp >= datetime.now() - timedelta(hours=24)
        ).count()
        
        critical_count = db.query(Incident).filter(
            Incident.severity == "CRITICAL"
        ).count()
        
        return {
            "total_auto_detected": total_threats,
            "zero_day_detections": zero_day_count,
            "last_24h_detections": last_24h,
            "critical_threats": critical_count,
            "detection_rate": f"{(last_24h / 24 * 100):.2f}% per hour" if last_24h > 0 else "0%"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching threat stats: {str(e)}")

