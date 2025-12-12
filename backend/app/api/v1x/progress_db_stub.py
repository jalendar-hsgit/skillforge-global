from fastapi import APIRouter, Header, Cookie, HTTPException
from ...core.security import decode_token

router = APIRouter(prefix="/progress-db", tags=["progress-db"])

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

@router.get("")
def list_progress(authorization: str | None = Header(None), token: str | None = Cookie(None)):
    _require_user(authorization, token)
    return []
