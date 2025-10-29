from fastapi import APIRouter, Query, Header, HTTPException
from typing import List
from ...schemas.course import CourseItem
from ...core.config import settings
import json, os

router = APIRouter(prefix="/courses", tags=["courses"])

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "courses.json")
DATA_PATH = os.path.normpath(DATA_PATH)

def _load_all():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_all(items):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

@router.get("", response_model=List[CourseItem])
def list_courses(path: str | None = Query(None, description="Optional path slug filter, e.g. python-ai")):
    items = _load_all()
    if path:
        items = [x for x in items if x.get("path") == path]
    return items

@router.post("", response_model=CourseItem)
def add_course(item: CourseItem, x_admin_key: str = Header(None)):
    if x_admin_key != settings.ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    items = _load_all()
    if any(i["id"] == item.id for i in items):
        raise HTTPException(status_code=400, detail="ID already exists")
    items.append(item.model_dump())
    _save_all(items)
    return item
