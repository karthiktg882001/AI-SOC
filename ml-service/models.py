from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ARRAY, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid
from datetime import datetime

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(255), unique=True, nullable=False, index=True)
    log_id = Column(String(255))
    severity = Column(String(50), nullable=False)
    status = Column(String(50), default="OPEN")
    threat_type = Column(String(100))
    source_ip = Column(String(45))
    destination_ip = Column(String(45))
    timestamp = Column(DateTime, nullable=False)
    detected_at = Column(DateTime, server_default=func.now())
    anomaly_score = Column(Float)
    description = Column(Text)
    raw_log_data = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    reports = relationship("IncidentReport", back_populates="incident")

class IncidentReport(Base):
    __tablename__ = "incident_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(255), ForeignKey("incidents.incident_id"), nullable=False)
    summary = Column(Text)
    detailed_analysis = Column(Text)
    mitigation_steps = Column(JSON)  # Changed from ARRAY(Text) to JSON to match database JSONB
    mitigation_script = Column(Text)
    generated_at = Column(DateTime, server_default=func.now())
    
    incident = relationship("Incident", back_populates="reports")

class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"
    
    id = Column(Integer, primary_key=True, index=True)
    threat_hash = Column(String(255), unique=True)
    threat_type = Column(String(100))
    ioc_type = Column(String(50))
    ioc_value = Column(Text)
    severity = Column(String(50))
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    detection_count = Column(Integer, default=1)
    threat_metadata = Column(JSON)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    name = Column(String(255))
    password_hash = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # Admin role
    role = Column(String(50), default="user")  # user, admin, analyst
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String(255))

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True)
    token = Column(String(255), unique=True, index=True)
    expires_at = Column(DateTime)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

class BlockedIP(Base):
    __tablename__ = "blocked_ips"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True)
    reason = Column(String)
    blocked_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)

class QuarantinedFile(Base):
    __tablename__ = "quarantined_files"
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True)
    original_path = Column(String)
    threat_type = Column(String)
    quarantined_at = Column(DateTime, server_default=func.now())

class BlockedPort(Base):
    __tablename__ = "blocked_ports"
    id = Column(Integer, primary_key=True, index=True)
    port_number = Column(Integer, unique=True)
    reason = Column(String)
    blocked_at = Column(DateTime, server_default=func.now())

class BlockedProcess(Base):
    __tablename__ = "blocked_processes"
    id = Column(Integer, primary_key=True, index=True)
    process_name = Column(String, unique=True)
    reason = Column(String)
    blocked_at = Column(DateTime, server_default=func.now())

class AccountLockout(Base):
    __tablename__ = "account_lockouts"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    lockout_reason = Column(String)
    locked_at = Column(DateTime, server_default=func.now())
    unlock_at = Column(DateTime)

class SystemInfo(Base):
    __tablename__ = "system_info"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    device_id = Column(String(255))
    platform = Column(String(50))
    os_version = Column(String(100))
    cpu_info = Column(JSON)
    memory_info = Column(JSON)
    network_info = Column(JSON)
    disk_info = Column(JSON)
    processes = Column(JSON)
    timestamp = Column(DateTime, default=datetime.now)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    message = Column(Text, nullable=False)
    response = Column(Text)
    is_admin_chat = Column(Boolean, default=False)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    context = Column(JSON)  # Store context like page, feature, etc.
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", foreign_keys=[user_id])
    admin = relationship("User", foreign_keys=[admin_id])

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String(100))  # login, logout, view_incident, create_report, etc.
    activity_details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User")

class UserSupportRequest(Base):
    __tablename__ = "user_support_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Assigned admin
    subject = Column(String(255))
    message = Column(Text, nullable=False)
    response = Column(Text)
    status = Column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, RESOLVED, CLOSED
    priority = Column(String(50), default="NORMAL")  # LOW, NORMAL, HIGH, URGENT
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    responded_at = Column(DateTime)
    
    user = relationship("User", foreign_keys=[user_id])
    admin = relationship("User", foreign_keys=[admin_id])
