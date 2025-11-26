from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from database import get_db
from models import Incident
from datetime import datetime, timedelta
from typing import Dict, Any

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get dashboard statistics"""
    total_incidents = db.query(Incident).count()
    
    # Count by severity
    critical_count = db.query(Incident).filter(Incident.severity == "CRITICAL").count()
    high_count = db.query(Incident).filter(Incident.severity == "HIGH").count()
    medium_count = db.query(Incident).filter(Incident.severity == "MEDIUM").count()
    low_count = db.query(Incident).filter(Incident.severity == "LOW").count()
    
    # Count by status
    open_count = db.query(Incident).filter(Incident.status == "OPEN").count()
    closed_count = db.query(Incident).filter(Incident.status == "CLOSED").count()
    
    # Recent incidents (last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)
    recent_count = db.query(Incident).filter(
        Incident.detected_at >= yesterday
    ).count()
    
    # Average anomaly score
    avg_score = db.query(func.avg(Incident.anomaly_score)).scalar() or 0.0
    
    # Top threat types
    threat_types = db.query(
        Incident.threat_type,
        func.count(Incident.id).label('count')
    ).group_by(Incident.threat_type).order_by(func.count(Incident.id).desc()).limit(5).all()
    
    return {
        "total_incidents": total_incidents,
        "severity_breakdown": {
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count
        },
        "status_breakdown": {
            "open": open_count,
            "closed": closed_count
        },
        "recent_incidents_24h": recent_count,
        "average_anomaly_score": float(avg_score),
        "top_threat_types": [{"type": t[0], "count": t[1]} for t in threat_types],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/threats/recent")
async def get_recent_threats(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recent security threats"""
    incidents = db.query(Incident).order_by(
        Incident.detected_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "incident_id": inc.incident_id,
            "threat_type": inc.threat_type,
            "severity": inc.severity,
            "source_ip": inc.source_ip,
            "anomaly_score": inc.anomaly_score,
            "detected_at": inc.detected_at.isoformat(),
            "status": inc.status
        }
        for inc in incidents
    ]

