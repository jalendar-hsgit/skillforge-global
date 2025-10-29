from fastapi import APIRouter, HTTPException, Query, Header, Depends
from ...schemas.quiz import QuizEnvelope, QuizSubmitIn, QuizSubmitOut, QuizSubmitOutItem
import os, json
from sqlalchemy.orm import Session
from ...core.db import get_db
from ...core.security import decode_token
from ...models.quiz_attempt import QuizAttempt

router = APIRouter(prefix="/quizzes", tags=["quizzes"])

DATA_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "quizzes.json"))

def _load_quiz(path: str):
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(path)

@router.get("", response_model=QuizEnvelope)
def get_quiz(path: str = Query(..., description="Path slug, e.g. python-ai")):
    q = _load_quiz(path)
    if not q:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return q

@router.post("/submit", response_model=QuizSubmitOut)
def submit_quiz(payload: QuizSubmitIn, authorization: str | None = Header(None), db: Session = Depends(get_db)):
    q = _load_quiz(payload.path)
    if not q:
        raise HTTPException(status_code=404, detail="Quiz not found")
    answers = {a["id"]: a["answerIndex"] for a in [a.dict() for a in payload.answers]}
    results = []
    score = 0
    for qq in q["questions"]:
        user_idx = answers.get(qq["id"], -1)
        correct = user_idx == qq["answerIndex"]
        if correct: score += 1
        results.append(QuizSubmitOutItem(
            id=qq["id"],
            correct=correct,
            correctIndex=qq["answerIndex"],
            explanation=qq.get("explanation")
        ))
    out = QuizSubmitOut(score=score, total=len(q["questions"]), results=results)
    # Optional: store attempt if token present
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        sub = decode_token(authorization.split(" ",1)[1])
        if sub:
            user_id = int(sub)
    if user_id:
        passed = score >= max(1, len(q["questions"]) // 2 + (len(q["questions"]) % 2))  # >= 50% rounding up
        db.add(QuizAttempt(user_id=user_id, path=payload.path, score=score, total=len(q["questions"]), passed=passed))
        db.commit()
    return out

@router.get("/_debug-path")
def debug_path(path: str = ""):
    return {"received_path": path}
