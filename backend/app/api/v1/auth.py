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
    create_password_reset_token,
    decode_token,
    get_current_superadmin,
)
import requests
from app.models.user import User
from app.services.email_service import email_service
from app.services.rate_limiter import rate_limit
from app.core.config import settings
# Import security audit utilities
from app.api.v1x.security import record_login_attempt, log_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None  # Optional field from frontend
    # Note: role is NOT allowed in public signup - users always start as 'user'
    # Only superadmins can promote users via admin panel

class LoginRequest(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str


class ForgotRequest(BaseModel):
    email: EmailStr


class ResetRequest(BaseModel):
    token: str
    new_password: str


class OAuthRequest(BaseModel):
    code: str
    redirect_uri: str | None = None
    code_verifier: str | None = None


class AdminCreateRequest(BaseModel):
    email: EmailStr
    password: str
    role: str | None = "ADMIN"

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
    # Relax or bypass rate limit in E2E tests
    if not settings.E2E_TEST_MODE:
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
        # Relax or bypass rate limit in E2E tests
        if not settings.E2E_TEST_MODE:
            rate_limit(ip_hash, "auth:login", limit=10, window_seconds=300)

        # Lookup user by email or username
        if data.email:
            u = db.query(User).filter(User.email == data.email).first()
        elif data.username:
            u = db.query(User).filter(User.username == data.username).first()
        else:
            raise HTTPException(status_code=400, detail="Email or username required")
            
        if n# Record failed login attempt
            record_login_attempt(
                db=db,
                user_id=0,
                ip_address=client_ip,
                user_agent=request.headers.get("User-Agent"),
                device="unknown",
                success=False,
                failure_reason="User not found"
            )
            log_action(
                db=db,
                user_id=None,
                action="LOGIN_FAILED",
                resource_type="user",
                ip_address=client_ip,
                details={"reason": "user_not_found"}
            )
            raise HTTPException(status_code=401, detail="Invalid login")

        # Verify password
        if not verify_password(data.password, u.password_hash):
            logger.debug("Login failed: bad password")
            # Record failed login attempt
            record_login_attempt(
                db=db,
                user_id=u.id,
                ip_address=client_ip,
                user_agent=request.headers.get("User-Agent"),
                device="unknown",
                success=False,
                failure_reason="Invalid password"
            )
            log_action(
                db=db,
                user_id=u.id,
                action="LOGIN_FAILED",
                resource_type="user",
                resource_id=u.id,
                ip_address=client_ip,
                details={"reason": "invalid_password"}
            )
            raise HTTPException(status_code=401, detail="Invalid login")

        # Create token
        token = create_access_token(u.id)
        logger.debug("Login success: token created")
        
        # Record successful login attempt
        record_login_attempt(
            db=db,
            user_id=u.id,
            ip_address=client_ip,
            user_agent=request.headers.get("User-Agent"),
            device="web",
            success=True
        )
        
        # Log successful login
        log_action(
            db=db,
            user_id=u.id,
            action="LOGIN_SUCCESS",
            resource_type="user",
            resource_id=u.id,
            ip_address=client_ip
        
        token = create_access_token(u.id)
        logger.debug("Login success: token created")

        # Cookie flags: HttpOnly + SameSite=Lax always; Secure only when frontend origin is https
        try:
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


@router.post("/forgot")
def forgot(request: ForgotRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Always return success to avoid leaking whether an email exists
    u = db.query(User).filter(User.email == request.email).first()
    if not u:
        return {"sent": True}

    token = create_password_reset_token(u.id)
    user_name = u.email.split("@")[0]
    background_tasks.add_task(email_service.send_password_reset_email, u.email, user_name, token)
    return {"sent": True}


@router.post("/reset")
def reset(data: ResetRequest, db: Session = Depends(get_db)):
    try:
        claims = decode_token(data.token)
        uid = claims.get("sub")
        if not uid:
            raise HTTPException(status_code=400, detail="Invalid token")
        user = db.query(User).filter(User.id == int(uid)).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        user.password_hash = get_password_hash(data.new_password)
        db.add(user)
        db.commit()
        return {"reset": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")


@router.post("/oauth/{provider}")
def oauth_exchange(provider: str, data: OAuthRequest, response: Response, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    provider = provider.lower()
    email = None
    name = None

    try:
        if provider == "github":
            # Exchange code for access token
            # GitHub does not support PKCE, so ignore code_verifier
            token_resp = requests.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": data.code,
                    "redirect_uri": data.redirect_uri,
                },
                headers={"Accept": "application/json"},
                timeout=10,
            )
            token_resp.raise_for_status()
            token_json = token_resp.json()
            access_token = token_json.get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="Failed to obtain access token from GitHub")
            user_resp = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {access_token}"},
                timeout=10,
            )
            user_resp.raise_for_status()
            user_json = user_resp.json()
            name = user_json.get("name") or user_json.get("login")
            email = user_json.get("email")
            # If email is not public on primary user object, fetch emails
            if not email:
                emails_resp = requests.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"token {access_token}"},
                    timeout=10,
                )
                emails_resp.raise_for_status()
                emails = emails_resp.json()
                primary = next((e for e in emails if e.get("primary")), None)
                email = (primary or (emails[0] if emails else {})).get("email")

        elif provider == "google":
            # Build token request data; include code_verifier if provided (PKCE)
            token_data = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": data.code,
                "redirect_uri": data.redirect_uri,
                "grant_type": "authorization_code",
            }
            if data.code_verifier:
                token_data["code_verifier"] = data.code_verifier
            
            token_resp = requests.post(
                "https://oauth2.googleapis.com/token",
                data=token_data,
                timeout=10,
            )
            token_resp.raise_for_status()
            token_json = token_resp.json()
            access_token = token_json.get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="Failed to obtain access token from Google")
            user_resp = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                params={"alt": "json", "access_token": access_token},
                timeout=10,
            )
            user_resp.raise_for_status()
            user_json = user_resp.json()
            email = user_json.get("email")
            name = user_json.get("name") or user_json.get("given_name")
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")

        if not email:
            raise HTTPException(status_code=400, detail="Could not determine user email from provider")

        # Find or create user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Create user with random password hash
            import secrets
            rand_pw = secrets.token_urlsafe(32)
            user = User(email=email, password_hash=get_password_hash(rand_pw))
            db.add(user)
            db.commit()
            db.refresh(user)
            # Send welcome email in background
            user_name = name or email.split("@")[0]
            background_tasks.add_task(send_welcome_email_background, email, user_name)

        # Issue app token and set cookie
        token = create_access_token(user.id)
        try:
            parsed = urlparse(getattr(settings, "FRONTEND_ORIGIN", ""))
            secure = parsed.scheme == "https"
        except Exception:
            secure = False
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            samesite="lax",
            path="/",
            max_age=60 * 60 * 24 * 7,
            secure=secure,
        )

        # Login notification email (non-blocking)
        client_ip = request.client.host if request.client else None
        background_tasks.add_task(email_service.send_login_notification, email, client_ip)

        return {"logged": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"OAuth exchange failed: {e}")
        raise HTTPException(status_code=500, detail="OAuth exchange failed")


@router.post("/admin/create")
def admin_create(data: AdminCreateRequest, db: Session = Depends(get_db), _sa: User = Depends(get_current_superadmin)):
    # Only superadmins may create admin or superadmin accounts
    if data.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(email=data.email, password_hash=get_password_hash(data.password), role=data.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"created": True, "id": user.id}
