from fastapi import APIRouter, Header, Cookie, HTTPException
from ...core.security import decode_token

router = APIRouter(prefix="/coins_db", tags=["coins"])

def _require_user(authorization: str | None, token: str | None):
    if authorization and authorization.startswith("Bearer "):
        claims = decode_token(authorization.split(" ",1)[1])
    elif token:
        claims = decode_token(token)
    else:
        raise HTTPException(status_code=401, detail="Missing token")
    if not claims or not claims.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid token")
    return claims.get("sub")

@router.get("/balance")
def get_balance(authorization: str | None = Header(None), token: str | None = Cookie(None)):
    _require_user(authorization, token)
    return {"balance": 0, "currency": "coins"}

@router.get("/transactions")
def list_transactions(authorization: str | None = Header(None), token: str | None = Cookie(None)):
    _require_user(authorization, token)
    return []

@router.get("/transactions/summary")
def get_transaction_summary(authorization: str | None = Header(None), token: str | None = Cookie(None)):
    _require_user(authorization, token)
    return {
        "total_transactions": 0,
        "total_earns": 0,
        "total_spends": 0,
        "total_earned": 0,
        "total_spent": 0,
        "current_balance": 0
    }
