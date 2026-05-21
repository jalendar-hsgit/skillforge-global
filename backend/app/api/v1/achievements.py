from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import json
import os
from threading import Lock

from app.api.v1.auth import get_current_user  # assumes this returns a dict/user model with id
from app.services.realtime_events import on_achievement_unlocked

router = APIRouter(prefix="/achievements", tags=["achievements"]) 

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DATA_FILE = os.path.join(DATA_DIR, "achievements.json")
_file_lock = Lock()

class AchievementIn(BaseModel):
    key: str = Field(..., description="Unique key per achievement, e.g., 'quiz:python-ai:perfect'")
    title: str = Field(..., description="Display title for the achievement")
    description: str | None = Field(None, description="Optional description")
    points: int | None = Field(0, description="Optional points awarded")

class Achievement(AchievementIn):
    unlocked_at: str

class UserAchievements(BaseModel):
    user_id: int
    items: List[Achievement] = []


def _ensure_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


def _load_all() -> Dict[str, Any]:
    _ensure_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_all(data: Dict[str, Any]):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, DATA_FILE)


@router.get("/me", response_model=UserAchievements)
def get_my_achievements(user=Depends(get_current_user)):
    all_data = _load_all()
    uid = str(user.id if hasattr(user, "id") else user["id"])  # support dict-like
    items = all_data.get(uid, [])
    return {"user_id": int(uid), "items": items}


@router.post("/unlock", response_model=UserAchievements)
async def unlock_achievement(payload: AchievementIn, user=Depends(get_current_user)):
    from datetime import datetime, timezone

    uid = str(user.id if hasattr(user, "id") else user["id"])  # support dict-like

    with _file_lock:
        data = _load_all()
        user_items: List[Dict[str, Any]] = data.get(uid, [])

        # if already unlocked, return unchanged
        if any(it.get("key") == payload.key for it in user_items):
            return {"user_id": int(uid), "items": user_items}

        new_item = {
            **payload.dict(),
            "unlocked_at": datetime.now(timezone.utc).isoformat(),
        }
        user_items.append(new_item)
        data[uid] = user_items
        _save_all(data)

    await on_achievement_unlocked(
        int(uid),
        payload.key,
        payload.title,
        payload.points,
        new_item["unlocked_at"],
    )

    return {"user_id": int(uid), "items": user_items}
