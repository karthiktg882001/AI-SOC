from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from services.anomaly_detector import AnomalyDetector
from database import SessionLocal
from models import Incident
from datetime import datetime
import uuid

router = APIRouter()
anomaly_detector = AnomalyDetector()

class AnomalyDetectionRequest(BaseModel):
    logId: Optional[str] = None
    logData: Dict[str, Any]

class AnomalyDetectionResponse(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    threat_type: str
    severity: str
    incident_id: Optional[str] = None

@router.post("/anomaly", response_model=AnomalyDetectionResponse)
async def detect_anomaly(request: AnomalyDetectionRequest):
    """Detect anomalies in log data"""
    try:
        is_anomaly, anomaly_score, threat_type = anomaly_detector.detect_anomaly(
            request.logData
        )
        
        # Determine severity
        if anomaly_score > 0.8:
            severity = "CRITICAL"
        elif anomaly_score > 0.6:
            severity = "HIGH"
        elif anomaly_score > 0.4:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        incident_id = None
        if is_anomaly:
            # Create incident record
            db = SessionLocal()
            try:
                log_data = request.logData
                metadata = log_data.get("metadata", {})
                
                incident = Incident(
                    incident_id=str(uuid.uuid4()),
                    log_id=request.logId or log_data.get("id"),
                    severity=severity,
                    status="OPEN",
                    threat_type=threat_type,
                    source_ip=metadata.get("ip") or metadata.get("source_ip"),
                    destination_ip=metadata.get("destination_ip"),
                    timestamp=datetime.fromisoformat(
                        log_data.get("timestamp").replace("Z", "+00:00")
                    ) if isinstance(log_data.get("timestamp"), str) else datetime.now(),
                    anomaly_score=anomaly_score,
                    description=log_data.get("message", ""),
                    raw_log_data=log_data
                )
                db.add(incident)
                db.commit()
                db.refresh(incident)
                incident_id = incident.incident_id
            except Exception as e:
                db.rollback()
                print(f"Error creating incident: {e}")
            finally:
                db.close()
        
        return AnomalyDetectionResponse(
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            threat_type=threat_type,
            severity=severity,
            incident_id=incident_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")

