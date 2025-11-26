"""
AI-Powered Log Report Generation Router
Generates comprehensive reports for individual logs and all logs
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from database import get_db
from models import Incident
from services.generative_ai import GenerativeAIService
from services.anomaly_detector import AnomalyDetector
from datetime import datetime, timedelta
import json

router = APIRouter()
generative_ai = GenerativeAIService()
anomaly_detector = AnomalyDetector()

class LogReportRequest(BaseModel):
    log_data: Dict[str, Any]
    include_analysis: bool = True
    include_recommendations: bool = True

class AllLogsReportRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    severity_filter: Optional[str] = None
    threat_type_filter: Optional[str] = None

class LogReportResponse(BaseModel):
    log_id: str
    report: Dict[str, Any]
    generated_at: str
    analysis_summary: str
    recommendations: List[str]
    threat_assessment: Dict[str, Any]

@router.post("/generate", response_model=LogReportResponse)
async def generate_log_report(
    request: LogReportRequest,
    db: Session = Depends(get_db)
):
    """Generate AI-powered report for a single log"""
    try:
        log_data = request.log_data
        log_id = log_data.get("id") or log_data.get("log_id") or f"log_{datetime.now().timestamp()}"
        
        # Analyze log for threats
        is_anomaly, anomaly_score, threat_type = anomaly_detector.detect_anomaly(log_data)
        
        # Generate comprehensive AI report
        incident_data = {
            "threat_type": threat_type or "NORMAL",
            "severity": "HIGH" if anomaly_score > 0.7 else "MEDIUM" if anomaly_score > 0.4 else "LOW",
            "source_ip": log_data.get("metadata", {}).get("ip") or log_data.get("metadata", {}).get("source_ip"),
            "destination_ip": log_data.get("metadata", {}).get("destination_ip"),
            "description": log_data.get("message", ""),
            "anomaly_score": anomaly_score,
            "timestamp": log_data.get("timestamp", datetime.now().isoformat()),
            "raw_log_data": log_data
        }
        
        # Generate AI report
        ai_report = generative_ai.generate_report(incident_data)
        
        # Build comprehensive report
        report = {
            "log_metadata": {
                "log_id": log_id,
                "source": log_data.get("source", "unknown"),
                "timestamp": log_data.get("timestamp"),
                "log_level": log_data.get("logLevel", log_data.get("log_level", "INFO"))
            },
            "threat_analysis": {
                "is_anomaly": is_anomaly,
                "anomaly_score": float(anomaly_score),
                "threat_type": threat_type or "NORMAL",
                "severity": incident_data["severity"],
                "confidence": float(anomaly_score) * 100
            },
            "ai_analysis": {
                "summary": ai_report.get("summary", ""),
                "detailed_analysis": ai_report.get("detailed_analysis", ""),
                "key_findings": [
                    f"Anomaly Score: {anomaly_score:.2%}",
                    f"Threat Type: {threat_type or 'Normal Activity'}",
                    f"Severity: {incident_data['severity']}"
                ]
            },
            "indicators": {
                "source_ip": incident_data["source_ip"],
                "destination_ip": incident_data["destination_ip"],
                "message_pattern": log_data.get("message", "")[:200],
                "metadata": log_data.get("metadata", {})
            },
            "recommendations": ai_report.get("mitigation_steps", []) if request.include_recommendations else []
        }
        
        return LogReportResponse(
            log_id=log_id,
            report=report,
            generated_at=datetime.now().isoformat(),
            analysis_summary=ai_report.get("summary", ""),
            recommendations=ai_report.get("mitigation_steps", []),
            threat_assessment={
                "is_threat": is_anomaly,
                "severity": incident_data["severity"],
                "confidence": float(anomaly_score) * 100
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating log report: {str(e)}")

@router.post("/generate-all")
async def generate_all_logs_report(
    request: AllLogsReportRequest,
    db: Session = Depends(get_db)
):
    """Generate comprehensive AI report for all logs within a time period"""
    try:
        # Query incidents/logs based on filters
        query = db.query(Incident)
        
        if request.start_date:
            start = datetime.fromisoformat(request.start_date.replace("Z", "+00:00"))
            query = query.filter(Incident.timestamp >= start)
        
        if request.end_date:
            end = datetime.fromisoformat(request.end_date.replace("Z", "+00:00"))
            query = query.filter(Incident.timestamp <= end)
        
        if request.severity_filter:
            query = query.filter(Incident.severity == request.severity_filter)
        
        if request.threat_type_filter:
            query = query.filter(Incident.threat_type == request.threat_type_filter)
        
        incidents = query.order_by(Incident.detected_at.desc()).all()
        
        # Aggregate statistics
        total_incidents = len(incidents)
        severity_counts = {}
        threat_type_counts = {}
        total_anomaly_score = 0
        
        for incident in incidents:
            severity_counts[incident.severity] = severity_counts.get(incident.severity, 0) + 1
            threat_type_counts[incident.threat_type or "UNKNOWN"] = threat_type_counts.get(incident.threat_type or "UNKNOWN", 0) + 1
            if incident.anomaly_score:
                total_anomaly_score += incident.anomaly_score
        
        avg_anomaly_score = total_anomaly_score / total_incidents if total_incidents > 0 else 0
        
        # Generate comprehensive AI report
        report_data = {
            "total_incidents": total_incidents,
            "time_period": {
                "start": request.start_date or (datetime.now() - timedelta(days=7)).isoformat(),
                "end": request.end_date or datetime.now().isoformat()
            },
            "statistics": {
                "severity_distribution": severity_counts,
                "threat_type_distribution": threat_type_counts,
                "average_anomaly_score": float(avg_anomaly_score),
                "critical_incidents": severity_counts.get("CRITICAL", 0),
                "high_severity": severity_counts.get("HIGH", 0),
                "medium_severity": severity_counts.get("MEDIUM", 0),
                "low_severity": severity_counts.get("LOW", 0)
            },
            "top_threats": sorted(
                threat_type_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "incidents": [
                {
                    "incident_id": inc.incident_id,
                    "threat_type": inc.threat_type,
                    "severity": inc.severity,
                    "source_ip": inc.source_ip,
                    "timestamp": inc.timestamp.isoformat() if inc.timestamp else None,
                    "anomaly_score": float(inc.anomaly_score) if inc.anomaly_score else 0
                }
                for inc in incidents[:100]  # Limit to 100 for report
            ]
        }
        
        # Generate AI summary
        ai_summary_prompt = f"""
        Generate a comprehensive security report summary for {total_incidents} security incidents.
        Severity Distribution: {severity_counts}
        Threat Types: {threat_type_counts}
        Average Anomaly Score: {avg_anomaly_score:.2%}
        """
        
        # Use generative AI to create executive summary
        executive_summary = generative_ai.generate_incident_summary({
            "threat_type": "MULTIPLE",
            "severity": "HIGH" if severity_counts.get("CRITICAL", 0) > 0 else "MEDIUM",
            "description": f"Security analysis of {total_incidents} incidents",
            "anomaly_score": avg_anomaly_score
        })
        
        return {
            "report_id": f"report_{datetime.now().timestamp()}",
            "generated_at": datetime.now().isoformat(),
            "executive_summary": executive_summary,
            "detailed_statistics": report_data,
            "recommendations": [
                f"Monitor {threat_type_counts.get(max(threat_type_counts, key=threat_type_counts.get), 'threats')} threats closely",
                f"Review {severity_counts.get('CRITICAL', 0)} critical incidents immediately",
                "Implement additional security controls based on threat patterns",
                "Update threat intelligence database with new findings"
            ],
            "time_range": {
                "start": request.start_date or (datetime.now() - timedelta(days=7)).isoformat(),
                "end": request.end_date or datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating all logs report: {str(e)}")

@router.get("/recent")
async def get_recent_log_reports(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recently generated log reports"""
    # Get recent incidents with reports
    incidents = db.query(Incident).join(
        IncidentReport, Incident.incident_id == IncidentReport.incident_id
    ).order_by(IncidentReport.generated_at.desc()).limit(limit).all()
    
    return [
        {
            "incident_id": inc.incident_id,
            "threat_type": inc.threat_type,
            "severity": inc.severity,
            "has_report": True
        }
        for inc in incidents
    ]

