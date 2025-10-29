from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.quiz_attempt import QuizAttempt

router = APIRouter(prefix="/quizzes", tags=["quizzes"])

@router.get("/status")
def quiz_status(path: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    last = (
        db.query(QuizAttempt)
          .filter(QuizAttempt.user_id == user.id, QuizAttempt.path == path)
          .order_by(QuizAttempt.created_at.desc())
          .first()
    )
    return {"passed": bool(last and last.passed)}
