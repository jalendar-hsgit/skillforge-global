from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text
from typing import Dict, Any, List
from app.core.db import SessionLocal
from app.core.security import get_current_user
from app.services.realtime_events import (
    on_quiz_started,
    on_quiz_submitted,
    on_quiz_graded,
)

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
async def attempt_quiz(data: AttemptIn, user = Depends(get_current_user)):
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

        await on_quiz_submitted(
            user.id,
            data.quiz_id,
            total_questions=total,
            answered=len(data.answers),
        )
        await on_quiz_graded(
            user.id,
            data.quiz_id,
            score=correct,
            total_questions=total,
        )
        return {"ok": True, "score": correct, "total": total, "details": details}
    finally:
        db.close()

# ==================== TIME TRACKING ENHANCEMENTS ====================
# NEW FEATURE: Track time spent on quizzes for better analytics

from datetime import datetime
import json

class AttemptWithTimingIn(BaseModel):
    """Enhanced attempt submission with time tracking"""
    quiz_id: int
    answers: Dict[str, str]  # question_id -> selected answer
    started_at: str  # ISO format datetime
    completed_at: str  # ISO format datetime
    question_times: Dict[str, int]  # question_id -> time_in_seconds
    
@router.post("/attempt-with-timing")
async def attempt_quiz_with_timing(data: AttemptWithTimingIn, user=Depends(get_current_user)):
    """
    Submit quiz attempt with detailed time tracking.
    Stores time spent per question for analytics.
    """
    db = SessionLocal()
    try:
        user_id = user.id
        
        # Parse timestamps
        start = None
        end = None
        try:
            start = datetime.fromisoformat(data.started_at.replace('Z', '+00:00'))
            end = datetime.fromisoformat(data.completed_at.replace('Z', '+00:00'))
            total_seconds = int((end - start).total_seconds())
        except:
            total_seconds = 0
        
        # Score the quiz
        rows = db.execute(text("""
            SELECT id, answer
            FROM quiz_questions
            WHERE quiz_id=:qid
        """), {"qid": data.quiz_id}).mappings().all()
        
        if not rows:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        total = len(rows)
        correct = 0
        details = []
        
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
                "time_spent": data.question_times.get(qid, 0)
            })
        
        score = int((correct / total * 100)) if total > 0 else 0
        
        # Store attempt with timing (if table exists)
        try:
            db.execute(text("""
                INSERT INTO quiz_attempts (
                    user_id, quiz_id, score, started_at, completed_at,
                    time_spent_seconds, question_times, answers
                ) VALUES (
                    :user_id, :quiz_id, :score, :started_at, :completed_at,
                    :time_spent, :q_times, :answers
                )
            """), {
                "user_id": user_id,
                "quiz_id": data.quiz_id,
                "score": score,
                "started_at": start,
                "completed_at": end,
                "time_spent": total_seconds,
                "q_times": json.dumps(data.question_times),
                "answers": json.dumps(data.answers)
            })
            db.commit()
        except Exception as e:
            # If table doesn't support new columns, just continue
            db.rollback()

        await on_quiz_started(user_id, data.quiz_id, started_at=start)
        await on_quiz_submitted(
            user_id,
            data.quiz_id,
            total_questions=total,
            answered=len(data.answers),
            submitted_at=end,
        )
        await on_quiz_graded(
            user_id,
            data.quiz_id,
            score=score,
            total_questions=total,
        )

        return {
            "ok": True,
            "score": score,
            "total": total,
            "correct": correct,
            "time_spent_seconds": total_seconds,
            "details": details
        }
    finally:
        db.close()

@router.get("/attempt/{attempt_id}/details")
def get_attempt_details(attempt_id: int, user=Depends(get_current_user)):
    """
    Retrieve detailed attempt results including time breakdown per question.
    """
    db = SessionLocal()
    try:
        attempt = db.execute(text("""
            SELECT id, user_id, quiz_id, score, started_at, completed_at,
                   time_spent_seconds, question_times, answers
            FROM quiz_attempts
            WHERE id=:aid
        """), {"aid": attempt_id}).mappings().first()
        
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        
        # Security: verify user owns this attempt
        if attempt["user_id"] != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Parse JSON fields safely
        question_times = {}
        answers = {}
        try:
            if attempt.get("question_times"):
                question_times = json.loads(attempt["question_times"])
            if attempt.get("answers"):
                answers = json.loads(attempt["answers"])
        except:
            pass
        
        return {
            "id": attempt["id"],
            "quiz_id": attempt["quiz_id"],
            "score": attempt["score"],
            "started_at": attempt["started_at"],
            "completed_at": attempt["completed_at"],
            "time_spent_seconds": attempt.get("time_spent_seconds", 0),
            "question_times": question_times,
            "answers": answers
        }
    finally:
        db.close()

@router.get("/user/history")
def get_quiz_history(user=Depends(get_current_user)):
    """
    Get user's quiz attempt history with time analytics.
    """
    db = SessionLocal()
    try:
        attempts = db.execute(text("""
            SELECT id, quiz_id, score, started_at, completed_at, time_spent_seconds
            FROM quiz_attempts
            WHERE user_id=:uid
            ORDER BY completed_at DESC
            LIMIT 50
        """), {"uid": user.id}).mappings().all()
        
        history = []
        for att in attempts:
            history.append({
                "id": att["id"],
                "quiz_id": att["quiz_id"],
                "score": att["score"],
                "completed_at": att.get("completed_at"),
                "time_spent_seconds": att.get("time_spent_seconds", 0)
            })
        
        return {"attempts": history}
    finally:
        db.close()

@router.get("/analytics/time-per-quiz")
def get_time_analytics(user=Depends(get_current_user)):
    """
    Get average time spent per quiz for the user.
    Useful for identifying areas where user spends more time.
    """
    db = SessionLocal()
    try:
        stats = db.execute(text("""
            SELECT 
                quiz_id,
                COUNT(*) as attempts,
                AVG(time_spent_seconds) as avg_time,
                MIN(time_spent_seconds) as min_time,
                MAX(time_spent_seconds) as max_time,
                AVG(score) as avg_score
            FROM quiz_attempts
            WHERE user_id=:uid
            GROUP BY quiz_id
            ORDER BY avg_time DESC
        """), {"uid": user.id}).mappings().all()
        
        analytics = []
        for stat in stats:
            analytics.append({
                "quiz_id": stat["quiz_id"],
                "attempts": stat.get("attempts", 0),
                "avg_time_seconds": int(stat.get("avg_time") or 0),
                "min_time_seconds": stat.get("min_time", 0),
                "max_time_seconds": stat.get("max_time", 0),
                "avg_score": float(stat.get("avg_score") or 0)
            })
        
        return {"analytics": analytics}
    finally:
        db.close()