from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.subscriber import Subscriber

router = APIRouter(prefix="/subscribe", tags=["newsletter"])

class SubscribeIn(BaseModel):
    email: EmailStr

@router.post("")
def subscribe(payload: SubscribeIn, db: Session = Depends(get_db)):
    existing = db.query(Subscriber).filter(Subscriber.email == payload.email).first()
    if existing:
        return {"ok": True, "message": "Already subscribed"}
    db.add(Subscriber(email=payload.email))
    db.commit()
    return {"ok": True, "message": "Subscribed"}
