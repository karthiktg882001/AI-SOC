"""
Direct Detection Router - Process logs immediately without Kafka
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from services.auto_threat_detector import AutoThreatDetector
import asyncio

router = APIRouter()

# Lazy initialization to avoid startup issues
_auto_threat_detector = None

def get_auto_threat_detector():
    """Lazy initialization of AutoThreatDetector"""
    global _auto_threat_detector
    if _auto_threat_detector is None:
        _auto_threat_detector = AutoThreatDetector()
    return _auto_threat_detector

class DirectDetectionRequest(BaseModel):
    logData: Dict[str, Any]

@router.post("/detect")
async def detect_direct(request: DirectDetectionRequest):
    """Directly detect threats from log data (bypasses Kafka)"""
    try:
        # Use auto threat detector (lazy initialization)
        detector = get_auto_threat_detector()
        result = detector.detect_threat_with_ai(request.logData)
        
        return {
            "success": True,
            "threat_detected": result["threat_detected"],
            "threat_type": result["threat_type"],
            "severity": result["severity"],
            "anomaly_score": result["anomaly_score"],
            "is_zero_day": result["is_zero_day"],
            "incident_id": result.get("incident_id"),
            "blocked": result.get("blocked", False),
            "ai_analysis": result.get("ai_analysis", {}),
            "recommendations": result.get("recommendations", []),
            "detected_at": result["detected_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")
