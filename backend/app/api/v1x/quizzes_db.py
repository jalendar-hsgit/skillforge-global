from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text
from typing import Dict, Any, List
from app.core.db import SessionLocal
from app.core.security import get_current_user

router = APIRouter(prefix="/quizzes-db", tags=["quizzes-db"])

def _parse_options(val: Any):
    # options might be JSON string or already a list
    import json
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        try:
            x = json.loads(val)
            if isinstance(x, list):
                return x
        except Exception:
            pass
        # fallback: split by |
        return [s.strip() for s in val.split("|") if s.strip()]
    return []

@router.get("/{quiz_id}")
def get_quiz(quiz_id: str):
    """Get quiz by ID (numeric) or slug (string)"""
    db = SessionLocal()
    try:
        # Try as numeric ID first
        if quiz_id.isdigit():
            quiz = db.execute(text("SELECT id, course_id, title FROM quizzes WHERE id=:qid"), {"qid": int(quiz_id)}).mappings().first()
        else:
            # Try as slug
            quiz = db.execute(text("SELECT id, course_id, title FROM quizzes WHERE path_slug=:slug"), {"slug": quiz_id}).mappings().first()
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        qs = db.execute(text("""
            SELECT id, question, options
            FROM quiz_questions
            WHERE quiz_id=:qid
            ORDER BY id
        """), {"qid": quiz["id"]}).mappings().all()
        questions = []
        for r in qs:
            questions.append({
                "id": r["id"],
                "question": r["question"],
                "options": _parse_options(r["options"]),
            })
        return {"id": quiz["id"], "title": quiz["title"], "questions": questions}
    finally:
        db.close()

class AttemptIn(BaseModel):
    quiz_id: int
    answers: Dict[str, str]  # question_id -> selected option text

@router.post("/attempt")
def attempt_quiz(data: AttemptIn, user = Depends(get_current_user)):
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT id, answer
            FROM quiz_questions
            WHERE quiz_id=:qid
        """), {"qid": data.quiz_id}).mappings().all()
        if not rows:
            raise HTTPException(status_code=404, detail="Quiz not found")

        total = len(rows)
        correct = 0
        details: List[dict] = []
        for r in rows:
            qid = str(r["id"])
            user_ans = data.answers.get(qid)
            correct_ans = r["answer"]
            is_ok = (user_ans == correct_ans)
            if is_ok:
                correct += 1
            details.append({
                "question_id": r["id"],
                "correct_answer": correct_ans,
                "your_answer": user_ans,
                "is_correct": is_ok,
            })

        return {"ok": True, "score": correct, "total": total, "details": details}
    finally:
        db.close()
