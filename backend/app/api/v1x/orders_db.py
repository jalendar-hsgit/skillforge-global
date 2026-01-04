from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.modelsx import Order, Course
from app.api.v1.auth import get_current_user
from app.services.realtime_events import on_course_enrolled

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/checkout")
async def checkout(course_path: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    c = db.query(Course).filter(Course.path == course_path).first()
    if not c or not c.is_paid:
        raise HTTPException(404, "Paid course not found")
    amount = c.price or 0
    o = Order(user_id=user.id, course_id=c.id, amount=amount, currency="USD", status="paid")
    db.add(o); db.commit(); db.refresh(o)

    await on_course_enrolled(
        user.id,
        c.id,
        c.title,
        course_path=c.path,
    )

    return {"ok": True, "order_id": o.id, "status": o.status}
