from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from ...core.db import get_db
from ...core.security import decode_token
from ...models.progress import Progress
from ...schemas.progress import ProgressList

router = APIRouter(prefix="/progress", tags=["progress"])

def _require_user(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    # decode_token returns the JWT claims dict; extract the `sub` claim
    claims = decode_token(authorization.split(" ",1)[1])
    if not claims:
        raise HTTPException(status_code=401, detail="Invalid token")
    sub = claims.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        return int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("", response_model=ProgressList)
def get_progress(path: str = Query(...), authorization: str | None = Header(None), db: Session = Depends(get_db)):
    user_id = _require_user(authorization)
    rows = db.query(Progress).filter(Progress.user_id==user_id, Progress.path==path).all()
    return ProgressList(path=path, completed=[r.module_id for r in rows])

@router.post("", response_model=ProgressList)
def mark_complete(path: str = Query(...), module_id: str = Query(...), authorization: str | None = Header(None), db: Session = Depends(get_db)):
    user_id = _require_user(authorization)
    exists = db.query(Progress).filter(Progress.user_id==user_id, Progress.module_id==module_id).first()
    if not exists:
        db.add(Progress(user_id=user_id, path=path, module_id=module_id))
        db.commit()
    rows = db.query(Progress).filter(Progress.user_id==user_id, Progress.path==path).all()
    return ProgressList(path=path, completed=[r.module_id for r in rows])
