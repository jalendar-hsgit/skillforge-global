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

@router.get("/transactions")
def get_transactions(
    limit: int = 50,
    skip: int = 0,
    user_id: int = Depends(get_current_user_id)
):
    """Get user's coin transaction history with pagination"""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT id, delta, reason, created_at
                FROM coin_ledger
                WHERE user_id = :uid
                ORDER BY created_at DESC
                LIMIT :lim OFFSET :off
            """),
            {"uid": user_id, "lim": limit, "off": skip},
        ).mappings().all()
        
        transactions = []
        for row in rows:
            transactions.append({
                "id": row["id"],
                "amount": abs(row["delta"]),
                "type": "earn" if row["delta"] > 0 else "spend",
                "reason": row["reason"] or "Unknown",
                "timestamp": row["created_at"].isoformat() if row["created_at"] else None,
                "balance_impact": row["delta"]
            })
        
        return transactions
    finally:
        db.close()


@router.get("/transactions/summary")
def get_transaction_summary(user_id: int = Depends(get_current_user_id)):
    """Get summary of coin transactions"""
    db = SessionLocal()
    try:
        # Get totals
        summary = db.execute(
            text("""
                SELECT
                    COUNT(*) as total_transactions,
                    COUNT(CASE WHEN delta > 0 THEN 1 END) as total_earns,
                    COUNT(CASE WHEN delta < 0 THEN 1 END) as total_spends,
                    COALESCE(SUM(CASE WHEN delta > 0 THEN delta ELSE 0 END), 0) as total_earned,
                    COALESCE(SUM(CASE WHEN delta < 0 THEN ABS(delta) ELSE 0 END), 0) as total_spent,
                    COALESCE(SUM(delta), 0) as current_balance
                FROM coin_ledger
                WHERE user_id = :uid
            """),
            {"uid": user_id},
        ).mappings().first()
        
        return {
            "total_transactions": summary["total_transactions"] or 0,
            "total_earns": summary["total_earns"] or 0,
            "total_spends": summary["total_spends"] or 0,
            "total_earned": int(summary["total_earned"] or 0),
            "total_spent": int(summary["total_spent"] or 0),
            "current_balance": int(summary["current_balance"] or 0)
        }
    finally:
        db.close()