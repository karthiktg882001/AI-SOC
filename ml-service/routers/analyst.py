from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from database import get_db
from models import Incident, IncidentReport, UserActivity
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

router = APIRouter()

class IncidentFeedback(BaseModel):
    feedback_type: str  # "true_positive" or "false_positive"
    notes: Optional[str] = None

class IncidentAssignment(BaseModel):
    assigned_to: Optional[int] = None  # user_id

@router.get("/incidents/active")
async def get_active_incidents(
    sort_by: str = Query("severity", enum=["severity", "mttr", "confidence", "detected_at"]),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get active incidents with sorting and prioritization"""
    incidents = db.query(Incident).filter(
        Incident.status.in_(["OPEN", "IN_PROGRESS"])
    )
    
    # Apply sorting
    if sort_by == "severity":
        severity_order = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
        incidents = incidents.order_by(
            func.case(
                (Incident.severity == "CRITICAL", 1),
                (Incident.severity == "HIGH", 2),
                (Incident.severity == "MEDIUM", 3),
                (Incident.severity == "LOW", 4),
                else_=5
            )
        )
    elif sort_by == "mttr":
        incidents = incidents.order_by(Incident.detected_at.asc())
    elif sort_by == "confidence":
        incidents = incidents.order_by(desc(Incident.anomaly_score))
    else:
        incidents = incidents.order_by(desc(Incident.detected_at))
    
    incidents = incidents.limit(limit).all()
    
    result = []
    for inc in incidents:
        # Calculate MTTR (time since detection)
        mttr_seconds = (datetime.now() - inc.detected_at).total_seconds()
        mttr_hours = mttr_seconds / 3600
        
        # Check if report exists (mitigation readiness)
        report = db.query(IncidentReport).filter(
            IncidentReport.incident_id == inc.incident_id
        ).first()
        mitigation_ready = report is not None
        
        # Check if zero-day (threat_type is UNKNOWN or anomaly_score > 0.8 with unknown pattern)
        is_zero_day = inc.threat_type == "UNKNOWN" or (
            inc.anomaly_score and inc.anomaly_score > 0.8 and 
            inc.threat_type not in ["brute_force", "port_scan", "sql_injection", "ddos", "malware", "xss", "unauthorized_access"]
        )
        
        result.append({
            "incident_id": inc.incident_id,
            "threat_type": inc.threat_type,
            "severity": inc.severity,
            "status": inc.status,
            "source_ip": inc.source_ip,
            "anomaly_score": inc.anomaly_score,
            "confidence_score": inc.anomaly_score,  # Using anomaly_score as confidence
            "detected_at": inc.detected_at.isoformat(),
            "mttr_hours": round(mttr_hours, 2),
            "mitigation_ready": mitigation_ready,
            "zero_day": is_zero_day,
            "description": inc.description
        })
    
    return result

@router.get("/zero-day/count")
async def get_zero_day_count(db: Session = Depends(get_db)):
    """Get count of zero-day threats"""
    yesterday = datetime.now() - timedelta(days=1)
    zero_day_count = db.query(Incident).filter(
        and_(
            Incident.detected_at >= yesterday,
            or_(
                Incident.threat_type == "UNKNOWN",
                and_(
                    Incident.anomaly_score > 0.8,
                    ~Incident.threat_type.in_([
                        "brute_force", "port_scan", "sql_injection", 
                        "ddos", "malware", "xss", "unauthorized_access"
                    ])
                )
            )
        )
    ).count()
    
    return {"zero_day_count": zero_day_count, "timestamp": datetime.now().isoformat()}

@router.get("/assets/at-risk")
async def get_assets_at_risk(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get top users/assets at risk based on aggregated anomaly scores"""
    yesterday = datetime.now() - timedelta(days=1)
    
    # Get top IPs by aggregated anomaly score
    top_ips = db.query(
        Incident.source_ip,
        func.count(Incident.id).label('incident_count'),
        func.avg(Incident.anomaly_score).label('avg_score'),
        func.max(Incident.anomaly_score).label('max_score')
    ).filter(
        and_(
            Incident.detected_at >= yesterday,
            Incident.source_ip.isnot(None)
        )
    ).group_by(Incident.source_ip).order_by(
        desc(func.avg(Incident.anomaly_score))
    ).limit(limit).all()
    
    result = []
    for ip_data in top_ips:
        # Get most critical incident for this IP
        critical_incident = db.query(Incident).filter(
            and_(
                Incident.source_ip == ip_data.source_ip,
                Incident.detected_at >= yesterday
            )
        ).order_by(desc(Incident.anomaly_score)).first()
        
        result.append({
            "entity_type": "IP",
            "entity_value": ip_data.source_ip,
            "incident_count": ip_data.incident_count,
            "avg_anomaly_score": round(float(ip_data.avg_score), 3),
            "max_anomaly_score": round(float(ip_data.max_score), 3),
            "most_critical_incident": critical_incident.incident_id if critical_incident else None,
            "severity": critical_incident.severity if critical_incident else "UNKNOWN"
        })
    
    return result

@router.post("/incidents/{incident_id}/feedback")
async def submit_incident_feedback(
    incident_id: str,
    feedback: IncidentFeedback,
    db: Session = Depends(get_db)
):
    """Submit analyst feedback for an incident (True Positive/False Positive)"""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Store feedback in incident metadata or create activity log
    if not incident.raw_log_data:
        incident.raw_log_data = {}
    
    if not isinstance(incident.raw_log_data, dict):
        incident.raw_log_data = {}
    
    incident.raw_log_data["analyst_feedback"] = {
        "feedback_type": feedback.feedback_type,
        "notes": feedback.notes,
        "submitted_at": datetime.now().isoformat()
    }
    
    # If false positive, optionally close the incident
    if feedback.feedback_type == "false_positive":
        incident.status = "CLOSED"
    
    db.commit()
    db.refresh(incident)
    
    return {
        "message": "Feedback submitted successfully",
        "incident_id": incident_id,
        "feedback_type": feedback.feedback_type
    }

@router.post("/incidents/{incident_id}/assign")
async def assign_incident(
    incident_id: str,
    assignment: IncidentAssignment,
    db: Session = Depends(get_db)
):
    """Assign incident to an analyst"""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Store assignment in raw_log_data metadata
    if not incident.raw_log_data:
        incident.raw_log_data = {}
    
    if not isinstance(incident.raw_log_data, dict):
        incident.raw_log_data = {}
    
    incident.raw_log_data["assigned_to"] = assignment.assigned_to
    incident.raw_log_data["assigned_at"] = datetime.now().isoformat()
    
    if incident.status == "OPEN":
        incident.status = "IN_PROGRESS"
    
    db.commit()
    db.refresh(incident)
    
    return {
        "message": "Incident assigned successfully",
        "incident_id": incident_id,
        "assigned_to": assignment.assigned_to
    }

@router.get("/log-volume/timeline")
async def get_log_volume_timeline(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get log volume timeline with incident overlay"""
    # This would ideally come from MongoDB log ingestion stats
    # For now, we'll use incident detection times as a proxy
    start_time = datetime.now() - timedelta(hours=hours)
    
    # Get incidents grouped by hour - using Python grouping for compatibility
    all_incidents = db.query(Incident).filter(
        Incident.detected_at >= start_time
    ).all()
    
    from collections import defaultdict
    hourly_counts = defaultdict(int)
    for inc in all_incidents:
        hour_key = inc.detected_at.replace(minute=0, second=0, microsecond=0)
        hourly_counts[hour_key] += 1
    
    incidents_by_hour = [(hour, count) for hour, count in sorted(hourly_counts.items())]
    
    result = []
    for hour_data in incidents_by_hour:
        result.append({
            "timestamp": hour_data.hour.isoformat(),
            "incident_count": hour_data.incident_count,
            "estimated_log_volume": hour_data.incident_count * 1000  # Estimate based on incidents
        })
    
    return result

@router.get("/filters/presets")
async def get_filter_presets():
    """Get predefined filter presets for quick access"""
    return {
        "presets": [
            {
                "id": "my_assigned",
                "name": "My Assigned Incidents",
                "filter": {"assigned_to": "current_user", "status": ["OPEN", "IN_PROGRESS"]}
            },
            {
                "id": "needs_review",
                "name": "Needs Review",
                "filter": {"status": "OPEN", "severity": ["CRITICAL", "HIGH"]}
            },
            {
                "id": "today_brute_force",
                "name": "Today's Brute Force",
                "filter": {"threat_type": "brute_force", "date_range": "today"}
            },
            {
                "id": "zero_day",
                "name": "Zero-Day Threats",
                "filter": {"zero_day": True}
            },
            {
                "id": "mitigation_ready",
                "name": "Mitigation Ready",
                "filter": {"mitigation_ready": True}
            }
        ]
    }

