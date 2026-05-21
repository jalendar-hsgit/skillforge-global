from fastapi import APIRouter, Header, Cookie, HTTPException
from ...core.security import decode_token

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

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

@router.get("/status")
def get_status(authorization: str | None = Header(None), token: str | None = Cookie(None)):
    _require_user(authorization, token)
    return {"active": False, "plan": None}