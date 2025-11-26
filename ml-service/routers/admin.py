"""
Admin Router - Admin-only features for user management, system settings, etc.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import User, Incident, IncidentReport, UserActivity, ChatMessage
from routers.auth import get_current_user, verify_password, get_password_hash, decrypt_password
import os

router = APIRouter()

# Admin dependency - ensures user is admin
async def get_admin_user(current_user: User = Depends(get_current_user)):
    """Dependency to ensure current user is an admin"""
    if not getattr(current_user, 'is_admin', False) and getattr(current_user, 'role', 'user') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    is_admin: bool = False
    role: str = "user"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None  # Optional password change
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    role: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    new_password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool
    is_admin: bool
    role: str
    password: Optional[str] = None  # Decrypted password for admin viewing
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SystemStats(BaseModel):
    total_users: int
    active_users: int
    admin_users: int
    total_incidents: int
    open_incidents: int
    resolved_incidents: int

# User Management
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only) - includes decrypted passwords, ordered by ID"""
    users = db.query(User).order_by(User.id.asc()).offset(skip).limit(limit).all()
    result = []
    for user in users:
        user_dict = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "role": user.role,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "password": (
                decrypt_password(user.password_hash) 
                if user.password_hash and decrypt_password(user.password_hash) != "[ENCRYPTION_KEY_MISMATCH]"
                else "[Password reset required]" if user.password_hash else None
            )
        }
        result.append(user_dict)
    return result

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only) - includes decrypted password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    decrypted_pwd = decrypt_password(user.password_hash) if user.password_hash else None
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "role": user.role,
        "created_at": user.created_at,
        "last_login": user.last_login,
        "password": (
            decrypted_pwd 
            if decrypted_pwd and decrypted_pwd != "[ENCRYPTION_KEY_MISMATCH]"
            else "[Password reset required]" if user.password_hash else None
        )
    }

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hashed_password,
        is_admin=user_data.is_admin,
        role=user_data.role if user_data.is_admin else "user",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user (admin only) - includes password change"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Protect permanent admin user from critical changes
    is_permanent_admin = user.email == "admin@soc.local"
    
    if is_permanent_admin:
        # Prevent changes to permanent admin user's critical fields
        if user_data.email is not None and user_data.email != "admin@soc.local":
            raise HTTPException(
                status_code=403,
                detail="Cannot change email of permanent admin user (admin@soc.local). This is a protected system account."
            )
        if user_data.is_admin is not None and user_data.is_admin == False:
            raise HTTPException(
                status_code=403,
                detail="Cannot remove admin privileges from permanent admin user (admin@soc.local). This is a protected system account."
            )
        if user_data.role is not None and user_data.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Cannot change role of permanent admin user (admin@soc.local). This is a protected system account."
            )
        if user_data.is_active is not None and user_data.is_active == False:
            raise HTTPException(
                status_code=403,
                detail="Cannot deactivate permanent admin user (admin@soc.local). This is a protected system account."
            )
    
    # Prevent admin from deactivating themselves (for non-permanent admins)
    if not is_permanent_admin and user_id == admin.id and user_data.is_active == False:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    
    # Allow name changes for permanent admin (for display purposes)
    if user_data.name is not None:
        user.name = user_data.name
    
    if user_data.email is not None:
        # Check if email is already taken
        existing = db.query(User).filter(User.email == user_data.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = user_data.email
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    if user_data.is_admin is not None:
        user.is_admin = user_data.is_admin
        if user_data.is_admin:
            user.role = "admin"
    
    if user_data.role is not None:
        user.role = user_data.role
    
    # Handle password change
    if user_data.password is not None and user_data.password.strip():
        if len(user_data.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        user.password_hash = get_password_hash(user_data.password)
        # Log password change activity
        activity = UserActivity(
            user_id=admin.id,
            activity_type="admin_change_user_password",
            activity_details={"target_user_id": user_id, "target_user_email": user.email}
        )
        db.add(activity)
    
    db.commit()
    db.refresh(user)
    
    # Return user with decrypted password for admin viewing
    decrypted_pwd = decrypt_password(user.password_hash) if user.password_hash else None
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "role": user.role,
        "created_at": user.created_at,
        "last_login": user.last_login,
        "password": (
            decrypted_pwd 
            if decrypted_pwd and decrypted_pwd != "[ENCRYPTION_KEY_MISMATCH]"
            else "[Password reset required]" if user.password_hash else None
        )
    }

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete user (admin only) and resequence remaining user IDs"""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deletion of permanent admin user
    if user.email == "admin@soc.local":
        raise HTTPException(
            status_code=403, 
            detail="Cannot delete permanent admin user (admin@soc.local). This is a protected system account."
        )
    
    # Store admin ID before deletion
    admin_id = admin.id
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    # Resequence remaining user IDs
    # Get all remaining users ordered by current ID
    remaining_users = db.query(User).order_by(User.id.asc()).all()
    
    # Resequence IDs starting from 1
    new_id = 1
    for user in remaining_users:
        if user.id != new_id:
            # Store old ID before updating
            old_id = user.id
            
            # Temporarily set ID to a high value to avoid conflicts
            temp_id = 999999 + new_id
            db.execute(text(f"UPDATE users SET id = {temp_id} WHERE id = {old_id}"))
            db.commit()
            
            # Now set to the correct new ID
            db.execute(text(f"UPDATE users SET id = {new_id} WHERE id = {temp_id}"))
            db.commit()
            
            # Update any foreign key references
            try:
                db.execute(text(f"UPDATE user_activities SET user_id = {new_id} WHERE user_id = {old_id}"))
                db.commit()
            except Exception:
                pass  # Table might not exist or have no data
            
            try:
                db.execute(text(f"UPDATE chat_messages SET user_id = {new_id} WHERE user_id = {old_id}"))
                db.commit()
            except Exception:
                pass  # Table might not exist or have no data
        
        new_id += 1
    
    # Reset the sequence to the next available ID
    try:
        max_id = db.execute(text("SELECT MAX(id) FROM users")).scalar() or 0
        db.execute(text(f"SELECT setval('users_id_seq', {max_id})"))
        db.commit()
    except Exception as e:
        # If sequence doesn't exist or can't be reset, that's okay
        print(f"Note: Could not reset sequence: {e}")
    
    return {"message": "User deleted successfully and IDs resequenced"}

@router.put("/users/{user_id}/password", response_model=dict)
async def change_user_password(
    user_id: int,
    password_data: PasswordChangeRequest,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Change user password (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate password length
    if len(password_data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    # Update password
    user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    # Log activity
    activity = UserActivity(
        user_id=admin.id,
        activity_type="admin_change_user_password",
        activity_details={"target_user_id": user_id, "target_user_email": user.email}
    )
    db.add(activity)
    db.commit()
    
    return {"message": "Password changed successfully", "user_id": user_id}

# System Statistics
@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system statistics (admin only)"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    total_incidents = db.query(Incident).count()
    open_incidents = db.query(Incident).filter(Incident.status == "OPEN").count()
    resolved_incidents = db.query(Incident).filter(Incident.status == "RESOLVED").count()
    
    return SystemStats(
        total_users=total_users,
        active_users=active_users,
        admin_users=admin_users,
        total_incidents=total_incidents,
        open_incidents=open_incidents,
        resolved_incidents=resolved_incidents
    )

# Incident Management (Admin)
class IncidentStatusUpdate(BaseModel):
    status: str

@router.put("/incidents/{incident_id}/status")
async def update_incident_status(
    incident_id: str,
    status_data: IncidentStatusUpdate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update incident status (admin only)"""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident.status = status_data.status
    db.commit()
    db.refresh(incident)
    return {"message": "Incident status updated", "incident_id": incident_id, "status": status_data.status}

@router.delete("/incidents/{incident_id}")
async def delete_incident(
    incident_id: str,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete incident (admin only)"""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Delete related reports
    db.query(IncidentReport).filter(IncidentReport.incident_id == incident_id).delete()
    db.delete(incident)
    db.commit()
    return {"message": "Incident deleted successfully"}

# System Settings
@router.get("/settings")
async def get_system_settings(admin: User = Depends(get_admin_user)):
    """Get system settings (admin only)"""
    return {
        "app_name": "SOC Assistant",
        "version": "1.0.0",
        "max_users": int(os.getenv("MAX_USERS", "1000")),
        "max_incidents": int(os.getenv("MAX_INCIDENTS", "10000")),
        "auto_threat_detection": os.getenv("AUTO_THREAT_DETECTION", "true").lower() == "true",
        "ai_enabled": os.getenv("AI_ENABLED", "true").lower() == "true"
    }

@router.get("/logs")
async def get_system_logs(
    limit: int = 100,
    admin: User = Depends(get_admin_user)
):
    """Get system logs (admin only) - placeholder"""
    # This would typically read from log files or a logging service
    return {
        "message": "System logs endpoint",
        "note": "Implement log aggregation service for production",
        "limit": limit
    }

# User Analytics
@router.get("/analytics/users")
async def get_user_analytics(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive user analytics (admin only)"""
    from datetime import datetime, timedelta
    from sqlalchemy import func, and_
    
    # Total users by role
    users_by_role = db.query(
        User.role,
        func.count(User.id).label('count')
    ).group_by(User.role).all()
    
    # Active vs inactive users
    active_count = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    inactive_count = db.query(func.count(User.id)).filter(User.is_active == False).scalar()
    
    # New users in last 7, 30 days
    seven_days_ago = datetime.now() - timedelta(days=7)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    new_users_7d = db.query(func.count(User.id)).filter(
        User.created_at >= seven_days_ago
    ).scalar()
    new_users_30d = db.query(func.count(User.id)).filter(
        User.created_at >= thirty_days_ago
    ).scalar()
    
    # User activity statistics
    total_activities = db.query(func.count(UserActivity.id)).scalar()
    activities_by_type = db.query(
        UserActivity.activity_type,
        func.count(UserActivity.id).label('count')
    ).group_by(UserActivity.activity_type).order_by(func.count(UserActivity.id).desc()).limit(10).all()
    
    # Recent logins (last 24 hours)
    last_24h = datetime.now() - timedelta(hours=24)
    recent_logins = db.query(func.count(User.id)).filter(
        User.last_login >= last_24h
    ).scalar()
    
    # Chat usage statistics
    total_chats = db.query(func.count(ChatMessage.id)).scalar()
    admin_chats = db.query(func.count(ChatMessage.id)).filter(
        ChatMessage.is_admin_chat == True
    ).scalar()
    user_chats = total_chats - admin_chats
    
    return {
        "users_by_role": {role: count for role, count in users_by_role},
        "active_users": active_count,
        "inactive_users": inactive_count,
        "new_users_7d": new_users_7d,
        "new_users_30d": new_users_30d,
        "recent_logins_24h": recent_logins,
        "total_activities": total_activities,
        "top_activities": {activity_type: count for activity_type, count in activities_by_type},
        "chat_statistics": {
            "total_chats": total_chats,
            "admin_chats": admin_chats,
            "user_chats": user_chats
        }
    }

@router.get("/analytics/activity")
async def get_activity_analytics(
    days: int = 30,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get user activity analytics (admin only)"""
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Activities by day
    activities_by_day = db.query(
        func.date(UserActivity.created_at).label('date'),
        func.count(UserActivity.id).label('count')
    ).filter(
        UserActivity.created_at >= start_date
    ).group_by(func.date(UserActivity.created_at)).order_by('date').all()
    
    # Activities by user
    activities_by_user = db.query(
        User.email,
        User.name,
        func.count(UserActivity.id).label('count')
    ).join(
        UserActivity, User.id == UserActivity.user_id
    ).filter(
        UserActivity.created_at >= start_date
    ).group_by(User.id, User.email, User.name).order_by(func.count(UserActivity.id).desc()).limit(20).all()
    
    return {
        "period_days": days,
        "activities_by_day": [{"date": str(date), "count": count} for date, count in activities_by_day],
        "top_active_users": [
            {"email": email, "name": name, "activity_count": count}
            for email, name, count in activities_by_user
        ]
    }

