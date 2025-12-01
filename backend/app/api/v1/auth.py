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
    # Note: role is NOT allowed in public signup - users always start as 'user'
    # Only superadmins can promote users via admin panel

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
    # Check if new registrations are allowed
    from app.services.settings_service import allow_new_registrations
    if not allow_new_registrations():
        raise HTTPException(
            status_code=403,
            detail="New user registrations are currently disabled. Please contact support."
        )
    
    # Rate limit signup by IP (100 signups per hour per IP for development)
    # In production, consider lowering this to 5-10
    client_ip = request.client.host if request.client else "unknown"
    ip_hash = int(hashlib.md5(client_ip.encode()).hexdigest()[:8], 16)
    rate_limit(ip_hash, "auth:signup", limit=100, window_seconds=3600)
    
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # All public signups are regular users by default
    # Only superadmins can promote users to admin/superadmin roles
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
    """Login endpoint: validates credentials and sets auth cookie.
    Added debug logs to diagnose 500s when proxying via Next.js.
    """
    try:
        # Rate limit login attempts by IP (10 attempts per 5 minutes per IP)
        client_ip = request.client.host if request.client else "unknown"
        logger.debug(f"/auth/login from {client_ip}")
        ip_hash = int(hashlib.md5(client_ip.encode()).hexdigest()[:8], 16)
        rate_limit(ip_hash, "auth:login", limit=10, window_seconds=300)

        # Lookup user
        u = db.query(User).filter(User.email == data.email).first()
        if not u:
            logger.debug("Login failed: user not found")
            raise HTTPException(status_code=401, detail="Invalid login")

        # Verify password
        if not verify_password(data.password, u.password_hash):
            logger.debug("Login failed: bad password")
            raise HTTPException(status_code=401, detail="Invalid login")

        # Create token
        token = create_access_token(u.id)
        logger.debug("Login success: token created")

        # Cookie flags: HttpOnly + SameSite=Lax always; Secure only when frontend origin is https
        try:
            from app.core.config import settings
            parsed = urlparse(getattr(settings, "FRONTEND_ORIGIN", ""))
            secure = parsed.scheme == "https"
        except Exception as se:
            logger.warning(f"Failed to parse FRONTEND_ORIGIN: {se}")
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
        logger.debug("Auth cookie set on response")
        return {"logged": True}
    except HTTPException:
        # Re-raise HTTP errors (401/429)
        raise
    except Exception as e:
        # Log and surface as 500 for easier diagnosis in dev
        logger.exception(f"Unexpected error in /auth/login: {e}")
        raise HTTPException(status_code=500, detail="Login failed due to server error")

@router.post("/logout")
def logout(res: Response):
    res.delete_cookie("token", path="/")
    return {"logged_out": True}

@router.get("/me")
def me(user=Depends(get_current_user)):
    # Include role so frontend SSR admin guard can authorize access
    return {"id": user.id, "email": user.email, "role": user.role}
