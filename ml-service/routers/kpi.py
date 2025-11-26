from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from database import get_db
from models import Incident, UserActivity, User
from datetime import datetime, timedelta
from typing import Dict, Any, List
from routers.admin import get_admin_user
from models import User as UserModel

router = APIRouter()

@router.get("/mttd-mttr/trends")
async def get_mttd_mttr_trends(
    days: int = Query(30, ge=1, le=365),
    admin: UserModel = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get MTTD and MTTR trends over time (admin only)"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # Get incidents grouped by day
        incidents = db.query(Incident).filter(
            Incident.detected_at >= start_date
        ).all()
        
        # Group by day and calculate metrics
        from collections import defaultdict
        daily_metrics = defaultdict(lambda: {"incidents": [], "mttd_sum": 0, "mttr_sum": 0, "count": 0, "mttr_count": 0})
        
        for inc in incidents:
            day_key = inc.detected_at.date() if inc.detected_at else datetime.now().date()
            
            # MTTD: Time from log timestamp to detection
            if inc.timestamp and inc.detected_at:
                mttd_seconds = (inc.detected_at - inc.timestamp).total_seconds()
                daily_metrics[day_key]["mttd_sum"] += max(0, mttd_seconds)
            
            # MTTR: Time from detection to resolution (if resolved)
            if inc.status == "CLOSED":
                if inc.updated_at and inc.detected_at:
                    mttr_seconds = (inc.updated_at - inc.detected_at).total_seconds()
                    daily_metrics[day_key]["mttr_sum"] += max(0, mttr_seconds)
                    daily_metrics[day_key]["mttr_count"] += 1
                elif inc.detected_at:
                    # Fallback: use detected_at if updated_at not available
                    mttr_seconds = (datetime.now() - inc.detected_at).total_seconds()
                    daily_metrics[day_key]["mttr_sum"] += max(0, mttr_seconds)
                    daily_metrics[day_key]["mttr_count"] += 1
            
            daily_metrics[day_key]["count"] += 1
            daily_metrics[day_key]["incidents"].append(inc)
        
        result = []
        for day in sorted(daily_metrics.keys()):
            metrics = daily_metrics[day]
            avg_mttd = (metrics["mttd_sum"] / metrics["count"]) / 3600 if metrics["count"] > 0 else 0  # Convert to hours
            avg_mttr = (metrics["mttr_sum"] / metrics["mttr_count"]) / 3600 if metrics["mttr_count"] > 0 else 0  # Convert to hours
            
            result.append({
                "date": day.isoformat(),
                "mttd_hours": round(avg_mttd, 2),
                "mttr_hours": round(avg_mttr, 2),
                "incident_count": metrics["count"]
            })
        
        return {
            "trends": result,
            "period_days": days,
            "average_mttd_hours": round(sum(r["mttd_hours"] for r in result) / len(result) if result else 0, 2),
            "average_mttr_hours": round(sum(r["mttr_hours"] for r in result) / len(result) if result else 0, 2)
        }
    except Exception as e:
        return {
            "trends": [],
            "period_days": days,
            "average_mttd_hours": 0,
            "average_mttr_hours": 0,
            "error": str(e)
        }

@router.get("/false-positive-rate")
async def get_false_positive_rate(
    days: int = Query(30, ge=1, le=365),
    admin: UserModel = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Calculate False Positive Rate from analyst feedback (admin only)"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        incidents = db.query(Incident).filter(
            Incident.detected_at >= start_date
        ).all()
        
        total_incidents = len(incidents)
        false_positives = 0
        true_positives = 0
        
        for inc in incidents:
            if inc.raw_log_data and isinstance(inc.raw_log_data, dict):
                feedback = inc.raw_log_data.get("analyst_feedback", {})
                if feedback:
                    feedback_type = feedback.get("feedback_type", "")
                    if feedback_type == "false_positive":
                        false_positives += 1
                    elif feedback_type == "true_positive":
                        true_positives += 1
        
        total_feedback = false_positives + true_positives
        fpr = (false_positives / total_feedback * 100) if total_feedback > 0 else 0
        
        return {
            "false_positive_rate": round(fpr, 2),
            "false_positives": false_positives,
            "true_positives": true_positives,
            "total_with_feedback": total_feedback,
            "total_incidents": total_incidents,
            "period_days": days,
            "target_fpr": 5.0,
            "meets_target": fpr < 5.0
        }
    except Exception as e:
        return {
            "false_positive_rate": 0,
            "false_positives": 0,
            "true_positives": 0,
            "total_with_feedback": 0,
            "total_incidents": 0,
            "period_days": days,
            "target_fpr": 5.0,
            "meets_target": False,
            "error": str(e)
        }

@router.get("/detection-accuracy")
async def get_detection_accuracy(
    days: int = Query(30, ge=1, le=365),
    admin: UserModel = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Calculate Detection Accuracy (F1 Score) from feedback (admin only)"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        incidents = db.query(Incident).filter(
            Incident.detected_at >= start_date
        ).all()
        
        true_positives = 0
        false_positives = 0
        false_negatives = 0  # Would need ground truth data for this
        
        for inc in incidents:
            if inc.raw_log_data and isinstance(inc.raw_log_data, dict):
                feedback = inc.raw_log_data.get("analyst_feedback", {})
                if feedback:
                    feedback_type = feedback.get("feedback_type", "")
                    if feedback_type == "true_positive":
                        true_positives += 1
                    elif feedback_type == "false_positive":
                        false_positives += 1
        
        # Calculate precision, recall, F1
        precision = (true_positives / (true_positives + false_positives)) if (true_positives + false_positives) > 0 else 0
        recall = (true_positives / (true_positives + false_negatives)) if (true_positives + false_negatives) > 0 else 1.0  # Assuming no false negatives tracked
        f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
        
        return {
            "precision": round(precision * 100, 2),
            "recall": round(recall * 100, 2),
            "f1_score": round(f1_score * 100, 2),
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "period_days": days,
            "target_f1": 90.0,
            "meets_target": f1_score * 100 >= 90.0
        }
    except Exception as e:
        return {
            "precision": 0,
            "recall": 0,
            "f1_score": 0,
            "true_positives": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "period_days": days,
            "target_f1": 90.0,
            "meets_target": False,
            "error": str(e)
        }

@router.get("/incident-volume/by-category")
async def get_incident_volume_by_category(
    days: int = Query(30, ge=1, le=365),
    admin: UserModel = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get incident volume broken down by threat category (admin only)"""
    start_date = datetime.now() - timedelta(days=days)
    
    category_counts = db.query(
        Incident.threat_type,
        func.count(Incident.id).label('count'),
        func.avg(Incident.anomaly_score).label('avg_score')
    ).filter(
        Incident.detected_at >= start_date
    ).group_by(
        Incident.threat_type
    ).order_by(
        func.count(Incident.id).desc()
    ).all()
    
    result = []
    for cat in category_counts:
        result.append({
            "category": cat.threat_type or "UNKNOWN",
            "count": cat.count,
            "avg_anomaly_score": round(float(cat.avg_score), 3),
            "percentage": 0  # Will calculate after
        })
    
    total = sum(r["count"] for r in result)
    for r in result:
        r["percentage"] = round((r["count"] / total * 100) if total > 0 else 0, 2)
    
    return {
        "categories": result,
        "total_incidents": total,
        "period_days": days
    }

@router.get("/service-health")
async def get_service_health(admin: UserModel = Depends(get_admin_user)):
    """Get health status of all microservices (admin only)"""
    try:
        import requests
        import os
        
        services = {}
        
        # Check ML Service (self) - always UP since we're running
        services["ml_service"] = {"status": "UP", "response_time_ms": 0}
        
        # Check Log Ingestion Service
        try:
            log_health = requests.get("http://log-ingestion-service:8080/api/logs/stats", timeout=2)
            services["log_ingestion"] = {
                "status": "UP" if log_health.status_code == 200 else "DEGRADED",
                "response_time_ms": round(log_health.elapsed.total_seconds() * 1000, 2)
            }
        except Exception as e:
            services["log_ingestion"] = {"status": "DOWN", "response_time_ms": None, "error": str(e)}
        
        # Check Frontend (basic check)
        try:
            frontend_health = requests.get("http://frontend:3000", timeout=2)
            services["frontend"] = {
                "status": "UP" if frontend_health.status_code == 200 else "DEGRADED",
                "response_time_ms": round(frontend_health.elapsed.total_seconds() * 1000, 2)
            }
        except Exception as e:
            services["frontend"] = {"status": "DOWN", "response_time_ms": None, "error": str(e)}
        
        # Database connectivity - check by trying a simple query
        from database import get_db
        try:
            db = next(get_db())
            db.execute("SELECT 1")
            services["postgresql"] = {"status": "UP", "response_time_ms": None}
            db.close()
        except:
            services["postgresql"] = {"status": "DOWN", "response_time_ms": None}
        
        # MongoDB - assume UP if we got here
        services["mongodb"] = {"status": "UP", "response_time_ms": None}
        
        overall_status = "UP" if all(s["status"] == "UP" for s in services.values()) else "DEGRADED"
        
        return {
            "overall_status": overall_status,
            "services": services,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "overall_status": "UNKNOWN",
            "services": {},
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/log-ingestion/status")
async def get_log_ingestion_status(
    admin: UserModel = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get real-time log ingestion status and throughput (admin only)"""
    try:
        # Get recent incident count as proxy for log volume
        last_hour = datetime.now() - timedelta(hours=1)
        incidents_last_hour = db.query(Incident).filter(
            Incident.detected_at >= last_hour
        ).count()
        
        # Estimate logs per second (assuming 1 incident per 1000 logs on average)
        estimated_logs_per_sec = (incidents_last_hour * 1000) / 3600 if incidents_last_hour > 0 else 0
        
        return {
            "target_throughput": 10000,  # logs/second
            "estimated_throughput": round(estimated_logs_per_sec, 2),
            "incidents_last_hour": incidents_last_hour,
            "status": "HEALTHY" if estimated_logs_per_sec > 1000 else "DEGRADED",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "target_throughput": 10000,
            "estimated_throughput": 0,
            "incidents_last_hour": 0,
            "status": "UNKNOWN",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/compliance/readiness")
async def get_compliance_readiness(
    framework: str = Query("NIST", enum=["NIST", "ISO27001", "PCI-DSS"]),
    admin: UserModel = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get compliance readiness score based on incident patterns (admin only)"""
    try:
        # Simplified compliance scoring based on incident management
        last_90_days = datetime.now() - timedelta(days=90)
        
        total_incidents = db.query(Incident).filter(
            Incident.detected_at >= last_90_days
        ).count()
        
        resolved_incidents = db.query(Incident).filter(
            and_(
                Incident.detected_at >= last_90_days,
                Incident.status == "CLOSED"
            )
        ).count()
        
        critical_incidents = db.query(Incident).filter(
            and_(
                Incident.detected_at >= last_90_days,
                Incident.severity == "CRITICAL"
            )
        ).count()
        
        # Calculate readiness score (simplified)
        resolution_rate = (resolved_incidents / total_incidents * 100) if total_incidents > 0 else 100
        critical_response_rate = 100 if critical_incidents == 0 else max(0, 100 - (critical_incidents * 5))
        
        overall_score = (resolution_rate * 0.6 + critical_response_rate * 0.4)
        
        return {
            "framework": framework,
            "readiness_score": round(overall_score, 2),
            "resolution_rate": round(resolution_rate, 2),
            "critical_response_rate": round(critical_response_rate, 2),
            "total_incidents_90d": total_incidents,
            "resolved_incidents_90d": resolved_incidents,
            "critical_incidents_90d": critical_incidents,
            "status": "COMPLIANT" if overall_score >= 80 else "NEEDS_IMPROVEMENT",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "framework": framework,
            "readiness_score": 0,
            "resolution_rate": 0,
            "critical_response_rate": 0,
            "total_incidents_90d": 0,
            "resolved_incidents_90d": 0,
            "critical_incidents_90d": 0,
            "status": "UNKNOWN",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/resource-usage")
async def get_resource_usage(admin: UserModel = Depends(get_admin_user)):
    """Get AI/ML resource usage metrics (admin only)"""
    import psutil
    import os
    
    # Get CPU and memory usage
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    # Get process info for ML service
    process = psutil.Process(os.getpid())
    process_memory_mb = process.memory_info().rss / 1024 / 1024
    
    return {
        "cpu_usage_percent": round(cpu_percent, 2),
        "memory_usage_percent": round(memory.percent, 2),
        "memory_total_gb": round(memory.total / 1024 / 1024 / 1024, 2),
        "memory_used_gb": round(memory.used / 1024 / 1024 / 1024, 2),
        "ml_service_memory_mb": round(process_memory_mb, 2),
        "timestamp": datetime.now().isoformat()
    }

