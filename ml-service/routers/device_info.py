from fastapi import APIRouter, Request, Depends
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from models import User
from routers.auth import get_current_user

router = APIRouter()

@router.get("/device-info")
async def get_device_info(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get client device information including real-time IP address and connection details"""
    # Get client IP address
    client_ip = request.client.host if request.client else "Unknown"
    
    # Try to get real IP from headers (if behind proxy/nginx)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        client_ip = real_ip
    
    # Get connection details
    connection_info = {
        "host": request.client.host if request.client else "Unknown",
        "port": request.client.port if request.client else None,
        "scheme": request.url.scheme,
        "path": str(request.url.path),
        "method": request.method
    }
    
    # Get user agent
    user_agent = request.headers.get("User-Agent", "Unknown")
    
    # Get other headers
    accept_language = request.headers.get("Accept-Language", "Unknown")
    accept_encoding = request.headers.get("Accept-Encoding", "Unknown")
    
    # Get referer if available
    referer = request.headers.get("Referer", "Direct")
    
    # Connection timestamp
    connection_timestamp = datetime.now()
    
    # Determine if connection is secure
    is_secure = request.url.scheme == "https" or request.headers.get("X-Forwarded-Proto") == "https"
    
    return {
        "ip_address": client_ip,
        "connection_info": connection_info,
        "user_agent": user_agent,
        "accept_language": accept_language,
        "accept_encoding": accept_encoding,
        "referer": referer,
        "is_secure": is_secure,
        "timestamp": connection_timestamp.isoformat(),
        "connection_time": connection_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": current_user.id if current_user else None,
        "user_email": current_user.email if current_user else None
    }

