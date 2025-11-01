from fastapi import APIRouter, Depends, HTTPException, Response
from urllib.parse import urlparse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(email=data.email, password_hash=get_password_hash(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"created": True}

@router.post("/login")
def login(res: Response, data: LoginRequest, db: Session = Depends(get_db)):
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
