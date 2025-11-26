from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "soc_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "soc_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "soc_db")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import all models here to ensure they are registered with Base.metadata
    from models import Incident, IncidentReport, ThreatIntelligence, User, PasswordResetToken, SystemInfo, ChatMessage, UserActivity, UserSupportRequest
    Base.metadata.create_all(bind=engine)
    
    # Create permanent admin user only when DB is freshly initialized (users table empty)
    from routers.auth import get_password_hash
    db = SessionLocal()
    try:
        admin_email = "admin@soc.local"
        # Fixed permanent admin credentials (can be overridden via env var)
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin@12345")
        admin_name = os.getenv("ADMIN_NAME", "Admin")

        # Only create the protected admin account if this is a fresh DB
        # We'll check whether there are any users already in the table. If none, assume a fresh DB
        existing_user_count = db.query(User).count()
        if existing_user_count == 0:
            admin_user = User(
                email=admin_email,
                name=admin_name,
                password_hash=get_password_hash(admin_password),
                is_admin=True,
                role="admin",
                is_active=True,
                email_verified=True
            )
            db.add(admin_user)
            db.commit()
            print(f"✅ Permanent admin user created: {admin_email} / {admin_password}")
            print(f"   ⚠️  This account is PROTECTED and cannot be deleted or have critical fields modified.")
        else:
            # DB already has users; do not create or overwrite the permanent admin automatically
            print(f"ℹ️  Skipping permanent admin creation: DB already contains {existing_user_count} user(s).")
    except Exception as e:
        print(f"⚠️  Error creating/updating permanent admin user: {e}")
        db.rollback()
    finally:
        db.close()

