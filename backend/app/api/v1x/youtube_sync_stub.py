from fastapi import APIRouter

router = APIRouter(prefix="/youtube", tags=["youtube"])

@router.get("/sync/status")
def get_sync_status():
    return {"status": "disabled", "last_sync": None}
