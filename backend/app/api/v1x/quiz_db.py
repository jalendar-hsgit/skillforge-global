from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.modelsx import Quiz, QuizQuestion, QuizAttempt
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/quizzes-db", tags=["quizzes-db"])

@router.get("/{course_id}")
def get_quiz(course_id: int, db: Session = Depends(get_db)):
    q = db.query(Quiz).filter(Quiz.course_id == course_id).first()
    if not q:
        raise HTTPException(404, "Quiz not found")
    qs = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == q.id).all()
    return {
        "quiz_id": q.id,
        "title": q.title,
        "questions": [
            {"id": x.id, "question": x.question, "options": x.options} for x in qs
        ],
    }

@router.post("/attempt")
def submit_attempt(quiz_id: int, answers: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    qs = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
    total = len(qs)
    correct = 0
    for q in qs:
        if str(answers.get(str(q.id))) == str(q.answer):
            correct += 1
    score = int(round(correct/total*100)) if total else 0
    attempt = QuizAttempt(user_id=user.id, quiz_id=quiz_id, score=score)
    db.add(attempt); db.commit(); db.refresh(attempt)
    return {"ok": True, "score": attempt.score, "attempt_id": attempt.id}
