from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.config import settings
from app.models.user import User, UserRole

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    # bcrypt max is 72 bytes; trim to be safe
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)

def create_access_token(user_id: int) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)

def _get_token_from_request(request: Request) -> Optional[str]:
    # Prefer cookie
    tok = request.cookies.get("token")
    if tok:
        return tok
    # Fallback: Authorization: Bearer <token>
    auth = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    return None

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user_id(request: Request) -> int:
    token = _get_token_from_request(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    claims = decode_token(token)
    uid = claims.get("sub")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        return int(uid)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    uid = get_current_user_id(request)
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Returns the current user if authenticated, otherwise None.
    Use for endpoints that work with or without authentication.
    """
    token = _get_token_from_request(request)
    if not token:
        return None
    try:
        claims = decode_token(token)
        uid = claims.get("sub")
        if uid:
            user = db.query(User).filter(User.id == int(uid)).first()
            return user
    except (JWTError, ValueError, HTTPException):
        pass
    return None


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to require admin or superadmin role.
    Raises 403 if user is not an admin.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Admin access required. Contact support if you need admin privileges."
        )
    return current_user


def get_current_superadmin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to require superadmin role.
    Raises 403 if user is not a superadmin.
    """
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=403,
            detail="Superadmin access required. This action is restricted."
        )
    return current_user
