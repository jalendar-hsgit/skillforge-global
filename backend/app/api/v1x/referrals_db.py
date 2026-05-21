from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.modelsx import Referral, CoinsTransaction
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/referrals", tags=["referrals"])

@router.post("/claim")
def claim(referred_user_id: int, bonus_credits: int = 50, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ref = Referral(referrer_user_id=user.id, referred_user_id=referred_user_id, bonus_credits=bonus_credits)
    db.add(ref)
    db.add(CoinsTransaction(user_id=user.id, type="earn", amount=bonus_credits, reason="referral_bonus"))
    db.commit()
    return {"ok": True}
