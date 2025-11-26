"""
Protection Status Router - Windows Security style protection dashboard
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.active_defense import ActiveDefenseService
from models import Incident
from datetime import datetime, timedelta

router = APIRouter()
active_defense = ActiveDefenseService()

@router.get("/status")
async def get_protection_status():
    """Get real-time protection status"""
    status = active_defense.get_protection_status()
    
    # Add recent threat stats
    db = next(get_db())
    try:
        last_24h = db.query(Incident).filter(
            Incident.timestamp >= datetime.now() - timedelta(hours=24)
        ).count()
        
        critical_threats = db.query(Incident).filter(
            Incident.severity == "CRITICAL",
            Incident.timestamp >= datetime.now() - timedelta(hours=24)
        ).count()
        
        status["recent_threats_24h"] = last_24h
        status["critical_threats_24h"] = critical_threats
    except Exception as e:
        print(f"Error fetching threat stats: {e}")
    finally:
        db.close()
    
    return status

@router.get("/threats-blocked")
async def get_blocked_threats():
    """Get list of blocked threats"""
    return {
        "blocked_ips": list(active_defense.blocked_ips),
        "blocked_ports": list(active_defense.blocked_ports),
        "quarantined_files": list(active_defense.quarantined_files),
        "protection_stats": active_defense.protection_stats
    }

@router.post("/unblock-ip/{ip}")
async def unblock_ip(ip: str):
    """Unblock an IP address"""
    success = await active_defense.unblock_ip(ip)
    return {
        "success": success,
        "ip": ip,
        "message": "IP unblocked successfully" if success else "IP not found in block list"
    }

@router.get("/is-blocked/{ip}")
async def check_ip_blocked(ip: str):
    """Check if an IP is blocked"""
    is_blocked = active_defense.is_ip_blocked(ip)
    return {
        "ip": ip,
        "blocked": is_blocked
    }

