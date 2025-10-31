from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, conint
from sqlalchemy import text
from app.core.db import SessionLocal
from app.core.security import get_current_user_id

# Create router
router = APIRouter(prefix="/coins_db", tags=["coins"])

@router.get("/health")
def health():
    return {"ok": True}

@router.get("/balance")
def balance(user_id: int = Depends(get_current_user_id)):
    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT COALESCE(SUM(delta),0) AS bal FROM coin_ledger WHERE user_id=:uid"),
            {"uid": user_id},
        ).mappings().first()
        bal = int(row["bal"] if row and row["bal"] is not None else 0)
        # provide both keys for compatibility with frontend code
        return {"balance": bal, "coins": bal}
    finally:
        db.close()

class MoveCoins(BaseModel):
    amount: conint(ge=1)
    reason: str | None = None

@router.post("/add")
def add(data: MoveCoins, user_id: int = Depends(get_current_user_id)):
    db = SessionLocal()
    try:
        db.execute(
            text("INSERT INTO coin_ledger (user_id, delta, reason) VALUES (:u, :d, :r)"),
            {"u": user_id, "d": int(data.amount), "r": data.reason or "credit"},
        )
        db.commit()
        return {"ok": True}
    finally:
        db.close()

@router.post("/spend")
def spend(data: MoveCoins, user_id: int = Depends(get_current_user_id)):
    db = SessionLocal()
    try:
        # ensure enough balance
        row = db.execute(
            text("SELECT COALESCE(SUM(delta),0) AS bal FROM coin_ledger WHERE user_id=:uid"),
            {"uid": user_id},
        ).mappings().first()
        bal = int(row["bal"] if row and row["bal"] is not None else 0)
        if bal < data.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        db.execute(
            text("INSERT INTO coin_ledger (user_id, delta, reason) VALUES (:u, :d, :r)"),
            {"u": user_id, "d": -int(data.amount), "r": data.reason or "debit"},
        )
        db.commit()
        return {"ok": True}
    finally:
        db.close()


@router.post("/redeem")
def redeem(data: MoveCoins, user_id: int = Depends(get_current_user_id)):
    """Alias endpoint for backwards-compatibility with frontend which calls `/redeem`.
    Performs the same action as `/spend`.
    """
    db = SessionLocal()
    try:
        # ensure enough balance
        row = db.execute(
            text("SELECT COALESCE(SUM(delta),0) AS bal FROM coin_ledger WHERE user_id=:uid"),
            {"uid": user_id},
        ).mappings().first()
        bal = int(row["bal"] if row and row["bal"] is not None else 0)
        if bal < data.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        db.execute(
            text("INSERT INTO coin_ledger (user_id, delta, reason) VALUES (:u, :d, :r)"),
            {"u": user_id, "d": -int(data.amount), "r": data.reason or "debit"},
        )
        db.commit()
        return {"ok": True}
    finally:
        db.close()
