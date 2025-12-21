"""
Authentication API Router.
Handles user registration, login, and profile management.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from ..database import get_db
from ..models import User, LoginLog
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)

router = APIRouter()


# ============== Schemas ==============

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str



class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    role: str
    avatar_url: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds
    user: UserResponse


class MessageResponse(BaseModel):
    code: int = 200
    message: str


# ============== Endpoints ==============

@router.post("/register", response_model=MessageResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if username exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Ensure password length does not exceed bcrypt limit (72 bytes)
    # Note: Bcrypt has a 72-character limit for the input string.
    password_to_hash = user_data.password[:72]
    hashed_password = get_password_hash(password_to_hash)
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        bio=user_data.bio,
        role="viewer"  # Default role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"code": 201, "message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Log attempt
    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    log_status = 1 if user and verify_password(form_data.password, user.password_hash) else 0
    message = "Success" if log_status == 1 else "Invalid credentials"
    
    try:
        login_log = LoginLog(
            username=form_data.username,
            ip_address=ip,
            browser=user_agent,
            os="unknown", # Simplification
            status=log_status,
            message=message
        )
        db.add(login_log)
        db.commit()
    except Exception as e:
        print(f"Login Logging Error: {e}")
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is disabled"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "user": UserResponse.model_validate(user)
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    # Update fields if provided
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.email is not None:
        # Check if email is being used by another user
        if user_update.email != current_user.email:
            existing_email = db.query(User).filter(User.email == user_update.email).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            current_user.email = user_update.email

    if user_update.phone is not None:
        current_user.phone = user_update.phone
        
    if user_update.bio is not None:
        current_user.bio = user_update.bio
        
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    current_user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return {"code": 200, "message": "Password changed successfully"}


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout current user (client should discard token)."""
    # JWT is stateless, so we just return success
    # In production, you might want to blacklist the token
    return {"code": 200, "message": "Logged out successfully"}

from fastapi import UploadFile, File
import shutil
import os
import uuid

UPLOAD_DIR = "uploads/avatars"

@router.post("/upload-avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload user avatar."""
    # 1. Validate file
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    # 2. Check size (content-length header is not always reliable, but good first check)
    # Actual read check happens during save if needed.
    
    # 3. Generate filename
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{current_user.id}_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 4. Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not save file: {str(e)}"
        )
        
    # 5. Update user profile
    # URL should be relative path that frontend can access via static mount
    avatar_url = f"/uploads/avatars/{filename}"
    current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)
    
    return current_user
