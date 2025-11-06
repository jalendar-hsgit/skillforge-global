from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks, Request
from urllib.parse import urlparse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import logging
import hashlib

from app.core.db import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.models.user import User
from app.services.email_service import email_service
from app.services.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None  # Optional field from frontend

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

async def send_welcome_email_background(email: str, name: str):
    """Background task to send welcome email."""
    try:
        await email_service.send_welcome_email(email, name)
        logger.info(f"Welcome email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {str(e)}")

@router.post("/signup")
async def signup(
    data: SignupRequest, 
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Rate limit signup by IP (5 signups per hour per IP)
    client_ip = request.client.host if request.client else "unknown"
    ip_hash = int(hashlib.md5(client_ip.encode()).hexdigest()[:8], 16)
    rate_limit(ip_hash, "auth:signup", limit=5, window_seconds=3600)
    
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user = User(email=data.email, password_hash=get_password_hash(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Award welcome bonus coins (100 coins for new users)
    try:
        from sqlalchemy import text
        db.execute(
            text("INSERT INTO coin_ledger (user_id, delta, reason) VALUES (:u, :d, :r)"),
            {"u": user.id, "d": 100, "r": "Welcome bonus"}
        )
        db.commit()
        logger.info(f"Awarded 100 welcome coins to user {user.id}")
    except Exception as e:
        logger.error(f"Failed to award welcome coins to user {user.id}: {str(e)}")
    
    # Send welcome email in background (non-blocking)
    user_name = data.full_name if data.full_name else data.email.split('@')[0]
    background_tasks.add_task(send_welcome_email_background, data.email, user_name)
    
    return {"created": True}

@router.post("/login")
def login(res: Response, request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    # Rate limit login attempts by IP (10 attempts per 5 minutes per IP)
    client_ip = request.client.host if request.client else "unknown"
    ip_hash = int(hashlib.md5(client_ip.encode()).hexdigest()[:8], 16)
    rate_limit(ip_hash, "auth:login", limit=10, window_seconds=300)
    
    u = db.query(User).filter(User.email == data.email).first()
    if not u or not verify_password(data.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid login")
    token = create_access_token(u.id)
    # Cookie flags: HttpOnly + SameSite=Lax always; Secure only when frontend origin is https
    try:
        from app.core.config import settings
        parsed = urlparse(getattr(settings, "FRONTEND_ORIGIN", ""))
        secure = parsed.scheme == "https"
    except Exception:
        secure = False

    res.set_cookie(
        key="token",
        value=token,
        httponly=True,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 7,
        secure=secure,
    )
    return {"logged": True}

@router.post("/logout")
def logout(res: Response):
    res.delete_cookie("token", path="/")
    return {"logged_out": True}

@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"id": user.id, "email": user.email}
