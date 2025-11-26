"""
Advanced Features Router
Endpoints for XAI, Active Learning, Graph Analysis, etc.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, Incident
from routers.admin import get_admin_user
# Lazy imports to avoid startup issues
from typing import Dict, Any

router = APIRouter()

@router.get("/xai/explain/{incident_id}")
async def explain_incident(
    incident_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get XAI explanation for an incident"""
    from services.xai_explainer import xai_explainer
    
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        return {"error": "Incident not found"}
    
    if not incident.raw_log_data:
        return {"error": "No log data available for explanation"}
    
    try:
        explanation = xai_explainer.explain_feature_importance(incident.raw_log_data)
        return {
            "incident_id": incident_id,
            "explanation": explanation
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/active-learning/stats")
async def get_active_learning_stats(
    days: int = Query(30, ge=1, le=365),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get active learning statistics"""
    from services.active_learning import active_learning_service
    return active_learning_service.get_feedback_statistics(days)

@router.get("/active-learning/training-data")
async def get_training_data(
    days: int = Query(90, ge=1, le=365),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get prepared training data from feedback"""
    from services.active_learning import active_learning_service
    return active_learning_service.prepare_training_data(days)

@router.get("/graph/entities/{entity_type}/{entity_id}")
async def get_related_entities(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get related entities from graph database"""
    from services.graph_analyzer import graph_analyzer
    return graph_analyzer.get_related_entities(entity_type, entity_id)

@router.get("/graph/attack-path")
async def find_attack_path(
    source_ip: str = Query(...),
    target_ip: str = Query(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Find attack path between two IPs"""
    from services.graph_analyzer import graph_analyzer
    return graph_analyzer.find_attack_path(source_ip, target_ip)

@router.get("/graph/compromised-hosts/{user_id}")
async def get_compromised_hosts(
    user_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get compromised hosts for a user"""
    from services.graph_analyzer import graph_analyzer
    hosts = graph_analyzer.get_compromised_hosts(str(user_id))
    return {"user_id": user_id, "compromised_hosts": hosts}

