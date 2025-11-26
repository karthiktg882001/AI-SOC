from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Incident, IncidentReport
from services.generative_ai import GenerativeAIService
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()
generative_ai = GenerativeAIService()

class IncidentResponse(BaseModel):
    id: int
    incident_id: str
    log_id: Optional[str] = None
    severity: str
    status: str
    threat_type: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    timestamp: datetime
    detected_at: datetime
    anomaly_score: Optional[float] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class ReportResponse(BaseModel):
    id: int
    incident_id: str
    summary: str
    detailed_analysis: str
    mitigation_steps: List[str]
    mitigation_script: str
    generated_at: datetime
    
    class Config:
        from_attributes = True

@router.get("", response_model=List[IncidentResponse])
async def get_incidents(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    severity: str = None,
    db: Session = Depends(get_db)
):
    """Get all security incidents"""
    query = db.query(Incident)
    
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    
    incidents = query.order_by(Incident.detected_at.desc()).offset(skip).limit(limit).all()
    return incidents

@router.get("/{incident_id}")
async def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Get incident by ID with enhanced AI analysis"""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Extract AI analysis from raw_log_data if available
    ai_analysis = {}
    if incident.raw_log_data:
        raw_data = incident.raw_log_data if isinstance(incident.raw_log_data, dict) else {}
        if "ai_analysis" in raw_data:
            ai_analysis = raw_data["ai_analysis"]
    
    # Get report if exists
    report = db.query(IncidentReport).filter(
        IncidentReport.incident_id == incident_id
    ).first()
    
    # Build response with AI analysis
    response = {
        "id": incident.id,
        "incident_id": incident.incident_id,
        "log_id": incident.log_id,
        "severity": incident.severity,
        "status": incident.status,
        "threat_type": incident.threat_type,
        "source_ip": incident.source_ip,
        "destination_ip": incident.destination_ip,
        "timestamp": incident.timestamp,
        "detected_at": incident.detected_at,
        "anomaly_score": incident.anomaly_score,
        "description": incident.description,
        "ai_analysis": ai_analysis,
        "raw_log_data": incident.raw_log_data,
        "has_report": report is not None
    }
    
    return response

@router.post("/{incident_id}/generate-report", response_model=ReportResponse)
async def generate_report(incident_id: str, db: Session = Depends(get_db)):
    """Generate AI-powered incident report - ensures all fields are populated"""
    # Try to find incident by incident_id first, then by partial match
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    
    # If not found, try partial match (for cases like "INC-001")
    if not incident:
        # Try to find by partial match
        incidents = db.query(Incident).filter(
            Incident.incident_id.like(f"%{incident_id}%")
        ).all()
        if incidents:
            incident = incidents[0]
    
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident not found: {incident_id}")
    
    # Check if report already exists - if it does but is incomplete, regenerate
    existing_report = db.query(IncidentReport).filter(
        IncidentReport.incident_id == incident.incident_id
    ).first()
    
    # Regenerate if report is missing critical fields
    should_regenerate = False
    if existing_report:
        if not existing_report.summary or not existing_report.detailed_analysis or not existing_report.mitigation_steps:
            should_regenerate = True
            db.delete(existing_report)
            db.commit()
    
    if existing_report and not should_regenerate:
        return existing_report
    
    # Generate report with all required fields
    incident_data = {
        "threat_type": incident.threat_type or "UNKNOWN",
        "severity": incident.severity or "MEDIUM",
        "source_ip": incident.source_ip,
        "destination_ip": incident.destination_ip,
        "timestamp": incident.timestamp.isoformat() if incident.timestamp else datetime.now().isoformat(),
        "detected_at": incident.detected_at.isoformat() if incident.detected_at else datetime.now().isoformat(),
        "anomaly_score": incident.anomaly_score or 0.5,
        "description": incident.description or "Security incident detected",
        "raw_log_data": incident.raw_log_data or {}
    }
    
    # Generate complete report
    report_data = generative_ai.generate_report(incident_data)
    
    # Ensure all fields are populated
    summary = report_data.get("summary", "")
    if not summary:
        summary = f"Security incident of type {incident_data['threat_type']} with severity {incident_data['severity']} detected."
    
    detailed_analysis = report_data.get("detailed_analysis", "")
    if not detailed_analysis:
        detailed_analysis = f"Detailed analysis for {incident_data['threat_type']} threat. Anomaly score: {incident_data['anomaly_score']:.2%}."
    
    mitigation_steps = report_data.get("mitigation_steps", [])
    if not mitigation_steps or len(mitigation_steps) == 0:
        # Fallback: generate basic mitigation steps
        mitigation_steps = [
            "Isolate affected systems from the network",
            "Block the source IP address immediately",
            "Review all logs related to this incident",
            "Check for data exfiltration or unauthorized access",
            "Update security policies and rules",
            "Notify security team and management"
        ]
    
    mitigation_script = report_data.get("mitigation_script", "")
    if not mitigation_script:
        source_ip = incident_data.get("source_ip")
        if source_ip:
            mitigation_script = f"""#!/bin/bash
# Auto-generated mitigation script
# Block source IP: {source_ip}
iptables -A INPUT -s {source_ip} -j DROP
echo "$(date): Blocked IP {source_ip}" >> /var/log/soc_mitigation.log
"""
    
    # Ensure mitigation_steps is a list (will be stored as JSON)
    if not isinstance(mitigation_steps, list):
        mitigation_steps = [str(mitigation_steps)] if mitigation_steps else []
    
    # Save report (mitigation_steps will be automatically converted to JSON by SQLAlchemy)
    report = IncidentReport(
        incident_id=incident.incident_id,
        summary=summary,
        detailed_analysis=detailed_analysis,
        mitigation_steps=mitigation_steps,  # List will be stored as JSON
        mitigation_script=mitigation_script
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Ensure mitigation_steps is a list (it comes from JSON in DB)
    if isinstance(report.mitigation_steps, str):
        import json
        try:
            report.mitigation_steps = json.loads(report.mitigation_steps)
        except:
            report.mitigation_steps = [report.mitigation_steps] if report.mitigation_steps else []
    elif report.mitigation_steps is None:
        report.mitigation_steps = []
    
    return report

@router.get("/{incident_id}/report", response_model=ReportResponse)
async def get_report(incident_id: str, db: Session = Depends(get_db)):
    """Get incident report"""
    # Try exact match first
    report = db.query(IncidentReport).filter(
        IncidentReport.incident_id == incident_id
    ).first()
    
    # If not found, try partial match
    if not report:
        incidents = db.query(IncidentReport).filter(
            IncidentReport.incident_id.like(f"%{incident_id}%")
        ).all()
        if incidents:
            report = incidents[0]
    
    if not report:
        raise HTTPException(status_code=404, detail=f"Report not found for incident: {incident_id}")
    
    # Ensure mitigation_steps is a list (it comes from JSON in DB)
    if isinstance(report.mitigation_steps, str):
        import json
        try:
            report.mitigation_steps = json.loads(report.mitigation_steps)
        except:
            report.mitigation_steps = [report.mitigation_steps] if report.mitigation_steps else []
    elif report.mitigation_steps is None:
        report.mitigation_steps = []
    
    return report

@router.patch("/{incident_id}/status")
async def update_status(
    incident_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    """Update incident status"""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident.status = status
    db.commit()
    db.refresh(incident)
    
    return {"message": "Status updated", "incident_id": incident_id, "status": status}

