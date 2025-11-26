"""
Authentication Router - User registration, login, password reset
STANDALONE VERSION - No dependencies on other services
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from cryptography.fernet import Fernet
from database import get_db
from models import User, PasswordResetToken
import os
import sys

router = APIRouter()

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "soc-secret-key-change-in-production-use-strong-random-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password encryption key (for reversible storage - allows admin to view passwords)
PASSWORD_ENCRYPTION_KEY = os.getenv("PASSWORD_ENCRYPTION_KEY", "")
if not PASSWORD_ENCRYPTION_KEY:
    # Generate a key if not provided
    key = Fernet.generate_key()
    PASSWORD_ENCRYPTION_KEY = key.decode()
    print(f"⚠️  Generated new password encryption key. Set PASSWORD_ENCRYPTION_KEY={PASSWORD_ENCRYPTION_KEY} in production")

try:
    fernet = Fernet(PASSWORD_ENCRYPTION_KEY.encode() if isinstance(PASSWORD_ENCRYPTION_KEY, str) else PASSWORD_ENCRYPTION_KEY)
except Exception as e:
    # If key is invalid, generate a new one
    key = Fernet.generate_key()
    fernet = Fernet(key)
    PASSWORD_ENCRYPTION_KEY = key.decode()
    print(f"⚠️  Generated new password encryption key due to error: {e}")
    print(f"⚠️  Set PASSWORD_ENCRYPTION_KEY={PASSWORD_ENCRYPTION_KEY} in production")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

# Password Functions
def encrypt_password(password: str) -> str:
    """Encrypt a password (reversible - for admin viewing)"""
    try:
        if not password:
            return ""
        password_bytes = password.encode('utf-8')
        encrypted = fernet.encrypt(password_bytes)
        return encrypted.decode('utf-8')
    except Exception as e:
        print(f"❌ Password encryption error: {e}", file=sys.stderr)
        # Fallback: use bcrypt if encryption fails
        return get_password_hash_bcrypt(password)

def decrypt_password(encrypted_password: str) -> str:
    """Decrypt a password (for admin viewing)"""
    try:
        if not encrypted_password:
            return ""
        # Check if it's a bcrypt hash (starts with $2)
        if encrypted_password.startswith('$2'):
            return "[BCRYPT_HASH]"  # Can't decrypt bcrypt
        encrypted_bytes = encrypted_password.encode('utf-8')
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    except Exception as e:
        error_str = str(e).lower()
        if "invalidtoken" in error_str or "invalid" in error_str:
            return "[ENCRYPTION_KEY_MISMATCH]"
        print(f"⚠️  Password decryption error: {e}", file=sys.stderr)
        return ""

def get_password_hash_bcrypt(password: str) -> str:
    """Hash password using bcrypt (one-way)"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Verify a password - supports both encrypted (Fernet) and bcrypt hashed passwords
    This ensures backward compatibility
    """
    if not stored_password or not plain_password:
        return False
    
    # Method 1: Try to decrypt (Fernet encrypted passwords)
    try:
        if not stored_password.startswith('$2'):  # Not a bcrypt hash
            decrypted = decrypt_password(stored_password)
            if decrypted and decrypted == plain_password:
                return True
    except Exception:
        pass  # Continue to bcrypt verification
    
    # Method 2: Try bcrypt verification only when the stored password looks like a bcrypt hash
    try:
        if stored_password.startswith('$2'):
            return bcrypt.checkpw(plain_password.encode('utf-8'), stored_password.encode('utf-8'))
        # If it doesn't look like a bcrypt hash and decryption failed, do not attempt bcrypt verification
        # This avoids "Invalid salt" errors when stored_password is actually a Fernet token or other format
        return False
    except Exception as e:
        print(f"⚠️  Password verification error: {e}", file=sys.stderr)
        return False

def get_password_hash(password: str) -> str:
    """Hash/encrypt a password - uses Fernet encryption for admin viewing capability"""
    return encrypt_password(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as e:
        print(f"⚠️  JWT decode error: {e}", file=sys.stderr)
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Authentication Endpoints
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login endpoint - STANDALONE, no dependencies on other services
    Accepts form-urlencoded data with 'username' (email) and 'password'
    """
    try:
        email = form_data.username.strip().lower()
        password = form_data.password
        
        print(f"🔐 Login attempt for: {email}", flush=True)
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User not found: {email}", flush=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            print(f"❌ User account inactive: {email}", flush=True)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Verify password
        if not user.password_hash:
            print(f"❌ No password hash for user: {email}", flush=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        password_valid = verify_password(password, user.password_hash)
        print(f"🔑 Password verification result: {password_valid}", flush=True)
        
        if not password_valid:
            print(f"❌ Invalid password for user: {email}", flush=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login timestamp
        try:
            user.last_login = datetime.now()
            db.commit()
        except Exception as e:
            print(f"⚠️  Failed to update last_login: {e}", file=sys.stderr)
            db.rollback()
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        print(f"✅ Login successful for: {email}", flush=True)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_admin": getattr(user, 'is_admin', False),
                "role": getattr(user, 'role', 'user')
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user_data.email.lower()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = User(
            email=user_data.email.lower(),
            name=user_data.name,
            password_hash=get_password_hash(user_data.password),
            is_active=True,
            email_verified=False,
            role="user"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Registration error: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "is_active": current_user.is_active,
        "is_admin": getattr(current_user, 'is_admin', False),
        "role": getattr(current_user, 'role', 'user'),
        "email_verified": current_user.email_verified,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.post("/request-password-reset")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset via email"""
    user = db.query(User).filter(User.email == reset_request.email.lower()).first()
    if not user:
        # Don't reveal if user exists
        return {"message": "If the email exists, a password reset link has been sent"}
    
    import secrets
    # Generate reset token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)
    
    # Save token
    reset_token = PasswordResetToken(
        email=reset_request.email.lower(),
        token=token,
        expires_at=expires_at,
        used=False
    )
    db.add(reset_token)
    db.commit()
    
    # In production, send email with reset link
    reset_link = f"/reset-password?token={token}"
    
    return {
        "message": "Password reset link sent to email",
        "reset_link": reset_link,  # Remove in production
        "token": token  # Remove in production
    }

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """Reset password using token"""
    # Find token
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == reset_data.token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.now()
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Find user
    user = db.query(User).filter(User.email == reset_token.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.password_hash = get_password_hash(reset_data.new_password)
    reset_token.used = True
    db.commit()
    
    return {"message": "Password reset successfully"}

@router.put("/update-profile")
async def update_profile(
    name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if name:
        current_user.name = name
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Profile updated successfully",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name
        }
    }
