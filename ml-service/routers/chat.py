"""
Chat Assistant Router - AI-powered help and chat functionality
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import ChatMessage, User, UserActivity, UserSupportRequest
from routers.auth import get_current_user
from services.generative_ai import GenerativeAIService
import json

router = APIRouter()

# Lazy initialization to avoid startup issues
_generative_ai = None

def get_generative_ai():
    """Lazy initialization of GenerativeAIService"""
    global _generative_ai
    if _generative_ai is None:
        _generative_ai = GenerativeAIService()
    return _generative_ai

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
    message_id: int
    timestamp: datetime

class ChatMessageResponse(BaseModel):
    id: int
    message: str
    response: Optional[str]
    is_admin_chat: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# AI-powered help responses
HELP_RESPONSES = {
    "dashboard": "The dashboard shows real-time security statistics, threat detection metrics, and recent security incidents. You can monitor system health and view threat trends here.",
    "incidents": "The incidents page displays all security incidents detected by the system. You can view details, generate AI reports, and manage incident status.",
    "reports": "Generate AI-powered security reports for individual logs or comprehensive analysis of all logs. Reports include detailed analysis and mitigation recommendations.",
    "profile": "Manage your account settings, view device information, monitor system resources, and change your password.",
    "admin": "Admin dashboard allows you to manage users, view system statistics, manage incidents, and configure system settings.",
    "login": "Use your email and password to login. If you forgot your password, use the password reset feature.",
    "default": "I'm your SOC Assistant! I can help you with:\n- Understanding dashboard features\n- Managing incidents\n- Generating reports\n- Account management\n- System navigation\n\nWhat would you like to know?"
}

@router.post("/help", response_model=ChatResponse)
async def get_help(
    request: ChatRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered help response"""
    try:
        # Determine context from message
        message_lower = request.message.lower()
        context_type = "default"
        
        for key in HELP_RESPONSES.keys():
            if key in message_lower:
                context_type = key
                break
        
        # Generate AI response (lazy initialization)
        ai_service = get_generative_ai()
        ai_response = ai_service.generate_help_response(request.message, context_type)
        
        # Save chat message
        chat_msg = ChatMessage(
            user_id=current_user.id if current_user else None,
            message=request.message,
            response=ai_response,
            context=request.context or {"type": context_type}
        )
        db.add(chat_msg)
        db.commit()
        db.refresh(chat_msg)
        
        # Log activity
        if current_user:
            activity = UserActivity(
                user_id=current_user.id,
                activity_type="chat_help",
                activity_details={"message": request.message, "context": context_type}
            )
            db.add(activity)
            db.commit()
        
        return ChatResponse(
            response=ai_response,
            message_id=chat_msg.id,
            timestamp=chat_msg.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating help response: {str(e)}")

@router.get("/history", response_model=List[ChatMessageResponse])
async def get_chat_history(
    limit: int = 50,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for current user"""
    if not current_user:
        return []
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    return messages

@router.post("/admin/chat", response_model=ChatResponse)
async def admin_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin chat communication - for administrators to communicate via chat"""
    # Check if user is admin
    if not getattr(current_user, 'is_admin', False) and getattr(current_user, 'role', 'user') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Generate AI response for admin (lazy initialization)
        ai_service = get_generative_ai()
        ai_response = ai_service.generate_admin_response(request.message, request.context)
        
        # Save admin chat message
        chat_msg = ChatMessage(
            user_id=current_user.id,
            message=request.message,
            response=ai_response,
            is_admin_chat=True,
            admin_id=current_user.id,
            context=request.context or {}
        )
        db.add(chat_msg)
        db.commit()
        db.refresh(chat_msg)
        
        # Log admin activity
        activity = UserActivity(
            user_id=current_user.id,
            activity_type="admin_chat",
            activity_details={"message": request.message}
        )
        db.add(activity)
        db.commit()
        
        return ChatResponse(
            response=ai_response,
            message_id=chat_msg.id,
            timestamp=chat_msg.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in admin chat: {str(e)}")

@router.get("/admin/chat/history", response_model=List[ChatMessageResponse])
async def get_admin_chat_history(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get admin chat history"""
    if not getattr(current_user, 'is_admin', False) and getattr(current_user, 'role', 'user') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.is_admin_chat == True
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    return messages

# User Support Requests (User to Admin)
class SupportRequestCreate(BaseModel):
    subject: Optional[str] = None
    message: str
    priority: str = "NORMAL"

class SupportRequestResponse(BaseModel):
    id: int
    user_id: int
    admin_id: Optional[int]
    subject: Optional[str]
    message: str
    response: Optional[str]
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    responded_at: Optional[datetime]
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    
    class Config:
        from_attributes = True

@router.post("/support/request", response_model=SupportRequestResponse)
async def create_support_request(
    request: SupportRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """User creates a support request to get help from admin"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    support_request = UserSupportRequest(
        user_id=current_user.id,
        subject=request.subject,
        message=request.message,
        priority=request.priority,
        status="PENDING"
    )
    db.add(support_request)
    db.commit()
    db.refresh(support_request)
    
    # Log activity
    activity = UserActivity(
        user_id=current_user.id,
        activity_type="support_request",
        activity_details={"request_id": support_request.id, "priority": request.priority}
    )
    db.add(activity)
    db.commit()
    
    result = SupportRequestResponse(
        id=support_request.id,
        user_id=support_request.user_id,
        admin_id=support_request.admin_id,
        subject=support_request.subject,
        message=support_request.message,
        response=support_request.response,
        status=support_request.status,
        priority=support_request.priority,
        created_at=support_request.created_at,
        updated_at=support_request.updated_at,
        responded_at=support_request.responded_at,
        user_name=current_user.name,
        user_email=current_user.email
    )
    
    return result

@router.get("/support/my-requests", response_model=List[SupportRequestResponse])
async def get_my_support_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's support requests"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    requests = db.query(UserSupportRequest).filter(
        UserSupportRequest.user_id == current_user.id
    ).order_by(UserSupportRequest.created_at.desc()).all()
    
    return [
        SupportRequestResponse(
            id=req.id,
            user_id=req.user_id,
            admin_id=req.admin_id,
            subject=req.subject,
            message=req.message,
            response=req.response,
            status=req.status,
            priority=req.priority,
            created_at=req.created_at,
            updated_at=req.updated_at,
            responded_at=req.responded_at,
            user_name=current_user.name,
            user_email=current_user.email
        ) for req in requests
    ]

# Admin Support Management
class SupportRequestUpdate(BaseModel):
    response: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None

@router.get("/admin/support/requests", response_model=List[SupportRequestResponse])
async def get_all_support_requests(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all support requests (admin only)"""
    if not getattr(current_user, 'is_admin', False) and getattr(current_user, 'role', 'user') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    query = db.query(UserSupportRequest)
    if status_filter:
        query = query.filter(UserSupportRequest.status == status_filter)
    
    requests = query.order_by(UserSupportRequest.created_at.desc()).all()
    
    result = []
    for req in requests:
        user = db.query(User).filter(User.id == req.user_id).first()
        result.append(SupportRequestResponse(
            id=req.id,
            user_id=req.user_id,
            admin_id=req.admin_id,
            subject=req.subject,
            message=req.message,
            response=req.response,
            status=req.status,
            priority=req.priority,
            created_at=req.created_at,
            updated_at=req.updated_at,
            responded_at=req.responded_at,
            user_name=user.name if user else None,
            user_email=user.email if user else None
        ))
    
    return result

@router.put("/admin/support/requests/{request_id}", response_model=SupportRequestResponse)
async def update_support_request(
    request_id: int,
    update: SupportRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin responds to or updates support request"""
    if not getattr(current_user, 'is_admin', False) and getattr(current_user, 'role', 'user') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    support_request = db.query(UserSupportRequest).filter(
        UserSupportRequest.id == request_id
    ).first()
    
    if not support_request:
        raise HTTPException(status_code=404, detail="Support request not found")
    
    if update.response:
        support_request.response = update.response
        support_request.admin_id = current_user.id
        support_request.responded_at = datetime.now()
        if support_request.status == "PENDING":
            support_request.status = "IN_PROGRESS"
    
    if update.status:
        support_request.status = update.status
    
    if update.priority:
        support_request.priority = update.priority
    
    db.commit()
    db.refresh(support_request)
    
    user = db.query(User).filter(User.id == support_request.user_id).first()
    
    return SupportRequestResponse(
        id=support_request.id,
        user_id=support_request.user_id,
        admin_id=support_request.admin_id,
        subject=support_request.subject,
        message=support_request.message,
        response=support_request.response,
        status=support_request.status,
        priority=support_request.priority,
        created_at=support_request.created_at,
        updated_at=support_request.updated_at,
        responded_at=support_request.responded_at,
        user_name=user.name if user else None,
        user_email=user.email if user else None
    )

@router.get("/admin/support/stats")
async def get_support_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get support request statistics (admin only)"""
    if not getattr(current_user, 'is_admin', False) and getattr(current_user, 'role', 'user') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    from sqlalchemy import func
    
    total = db.query(func.count(UserSupportRequest.id)).scalar()
    pending = db.query(func.count(UserSupportRequest.id)).filter(
        UserSupportRequest.status == "PENDING"
    ).scalar()
    in_progress = db.query(func.count(UserSupportRequest.id)).filter(
        UserSupportRequest.status == "IN_PROGRESS"
    ).scalar()
    resolved = db.query(func.count(UserSupportRequest.id)).filter(
        UserSupportRequest.status == "RESOLVED"
    ).scalar()
    
    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "closed": total - pending - in_progress - resolved
    }

@router.get("/admin/user/{user_id}/messages")
async def get_user_messages(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages and support requests for a specific user (admin only)"""
    if not getattr(current_user, 'is_admin', False) and getattr(current_user, 'role', 'user') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get user info
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all chat messages from this user
    chat_messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    # Get all support requests from this user
    support_requests = db.query(UserSupportRequest).filter(
        UserSupportRequest.user_id == user_id
    ).order_by(UserSupportRequest.created_at.asc()).all()
    
    # Combine and format messages
    messages = []
    
    # Add chat messages
    for msg in chat_messages:
        messages.append({
            "id": f"chat_{msg.id}",
            "type": "chat",
            "user_message": msg.message,
            "admin_response": msg.response,
            "timestamp": msg.created_at,
            "is_admin_chat": msg.is_admin_chat
        })
    
    # Add support requests
    for req in support_requests:
        messages.append({
            "id": f"support_{req.id}",
            "type": "support",
            "user_message": req.message,
            "admin_response": req.response,
            "timestamp": req.created_at,
            "status": req.status,
            "priority": req.priority,
            "subject": req.subject
        })
    
    # Sort by timestamp
    messages.sort(key=lambda x: x["timestamp"])
    
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_active": user.is_active
        },
        "messages": messages,
        "total_messages": len(messages),
        "unread_count": len([m for m in messages if not m.get("admin_response")])
    }

@router.post("/admin/user/{user_id}/respond")
async def respond_to_user(
    user_id: int,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin responds to a user's message (admin only)"""
    if not getattr(current_user, 'is_admin', False) and getattr(current_user, 'role', 'user') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create a chat message as admin response
    chat_msg = ChatMessage(
        user_id=user_id,
        message=request.message,  # This will be the user's original message context
        response=request.message,  # Admin's response
        is_admin_chat=True,
        admin_id=current_user.id,
        context=request.context or {"type": "admin_response"}
    )
    db.add(chat_msg)
    db.commit()
    db.refresh(chat_msg)
    
    # Log activity
    activity = UserActivity(
        user_id=current_user.id,
        activity_type="admin_respond_user",
        activity_details={"user_id": user_id, "message_id": chat_msg.id}
    )
    db.add(activity)
    db.commit()
    
    return ChatResponse(
        response=chat_msg.response,
        message_id=chat_msg.id,
        timestamp=chat_msg.created_at
    )

