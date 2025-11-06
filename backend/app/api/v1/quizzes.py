from fastapi import APIRouter, HTTPException, Query, Header, Depends
from fastapi.responses import StreamingResponse
from ...schemas.quiz import QuizEnvelope, QuizSubmitIn, QuizSubmitOut, QuizSubmitOutItem, QuizQuestion
import os, json, random, time, asyncio
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ...core.db import get_db
from ...core.security import decode_token, get_current_user
from ...models.quiz_attempt import QuizAttempt
from ...modelsx.quiz_template import GeneratedQuiz, QuizSession
from ...services.llm_provider import get_llm_provider
from ...services.adaptive_difficulty import AdaptiveDifficultyEngine
from ...services.rate_limiter import rate_limit

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


# ------------------------
# AI Quiz Generation
# ------------------------
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class QuizGenIn(BaseModel):
    topic: str = Field(..., description="Topic or slug to generate questions about")
    difficulty: Literal["easy", "medium", "hard"] = Field("medium")
    num_questions: int = Field(5, ge=1, le=20)
    options_per_question: int = Field(4, ge=2, le=6)
    time_limit_minutes: Optional[int] = Field(None, description="Optional time limit for the quiz in minutes")


def _generate_mcq_for_topic(topic: str, difficulty: str, options: int, idx: int) -> QuizQuestion:
    """Generate a simple MCQ deterministically based on topic + index.
    This is a placeholder for a real AI generator; produces plausible distractors.
    """
    # deterministic seed for reproducibility
    seed = hash((topic.lower().strip(), difficulty, idx)) & 0xFFFFFFFF
    rnd = random.Random(seed)

    base_terms = [
        f"Fundamentals of {topic}",
        f"Key concept in {topic}",
        f"Best practice for {topic}",
        f"Common pitfall in {topic}",
        f"Advanced {topic} idea",
    ]
    text = rnd.choice(base_terms)
    # Construct a simple Q stem
    prompt_stems = [
        f"Which of the following best describes {topic}?",
        f"What is a recommended approach in {topic}?",
        f"Which option is TRUE regarding {topic}?",
        f"Identify the correct statement about {topic}.",
        f"In {topic}, which is generally preferred?",
    ]
    stem = rnd.choice(prompt_stems)
    question_text = f"{stem}"

    # Make a 'correct' answer and distractors
    correct = f"{topic} — {rnd.choice(['principled method','core definition','standard practice','accurate description','canonical approach'])}"
    distractor_bank = [
        f"{topic} — {rnd.choice(['anti-pattern','misconception','edge-case only','deprecated method','irrelevant detail'])}",
        f"{topic} — {rnd.choice(['performance hazard','security risk','overgeneralization','myth','outdated view'])}",
        f"{topic} — {rnd.choice(['partial truth','non-standard method','unverified claim','implementation quirk','rare scenario'])}",
        f"{topic} — {rnd.choice(['ambiguous guideline','non-recommendation','not industry standard','weak heuristic','non-deterministic idea'])}",
    ]

    # Increase wording complexity by difficulty
    if difficulty == "hard":
        correct += " (context-dependent, but typically validated by empirical evidence)"
        distractor_bank = [d + " (heuristic without robust validation)" for d in distractor_bank]
    elif difficulty == "medium":
        correct += " (commonly accepted)"

    # choose options and position the correct one
    chosen_distractors = rnd.sample(distractor_bank, k=min(options - 1, len(distractor_bank)))
    correct_index = rnd.randrange(0, len(chosen_distractors) + 1)
    opts: List[str] = []
    for i in range(len(chosen_distractors) + 1):
        if i == correct_index:
            opts.append(correct)
        if i < len(chosen_distractors):
            opts.append(chosen_distractors[i])

    qid = f"ai-{topic.replace(' ', '-').lower()}-{idx+1}"
    return QuizQuestion(id=qid, type="mcq", text=question_text, options=opts, answerIndex=correct_index)


@router.post("/generate", response_model=QuizEnvelope)
async def generate_quiz_ai(
    payload: QuizGenIn,
    save: bool = Query(False, description="Save generated quiz to user's library"),
    session_id: Optional[int] = Query(None, description="Quiz session ID for adaptive difficulty"),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI quiz using configured LLM provider with optional adaptive difficulty."""
    # Rate limit: 10 generations per 5 minutes per user
    from ...services.rate_limiter import rate_limit
    rate_limit(user.id, "quizzes:generate", limit=10, window_seconds=300)
    
    topic = payload.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")
    
    # Get adaptive context if session provided
    adaptive_context = None
    if session_id:
        session = db.query(QuizSession).filter(QuizSession.id == session_id, QuizSession.user_id == user.id).first()
        if session and session.answers:
            engine = AdaptiveDifficultyEngine()
            adaptive_context = {"previous_performance": engine.get_performance_context(session.answers)}
    
    try:
        # Use real LLM provider
        provider = get_llm_provider()
        questions_data = await provider.generate_quiz_questions(
            topic=topic,
            difficulty=payload.difficulty,
            num_questions=payload.num_questions,
            options_per_question=payload.options_per_question,
            user_context=adaptive_context
        )
        
        # Normalize IDs
        for i, q in enumerate(questions_data):
            if "id" not in q or not q["id"]:
                q["id"] = f"ai-{topic.replace(' ', '-').lower()}-{i+1}"
        
        quiz_id = f"ai-{topic.replace(' ', '-').lower()}-{int(time.time())}"
        title = f"{topic.title()} — {payload.difficulty.title()} Quiz"
        
        quiz_data = {"id": quiz_id, "title": title, "questions": questions_data}
        
        # Save to database if requested
        if save and user:
            from ...core.config import settings
            generated_quiz = GeneratedQuiz(
                user_id=user.id,
                topic=topic,
                difficulty=payload.difficulty,
                title=title,
                questions=questions_data,
                provider=settings.AI_PROVIDER,
                model=settings.OPENAI_MODEL if settings.AI_PROVIDER == "openai" else settings.ANTHROPIC_MODEL,
                adaptive_context=adaptive_context
            )
            db.add(generated_quiz)
            db.commit()
            db.refresh(generated_quiz)
            quiz_data["saved_id"] = generated_quiz.id
        
        return quiz_data
    
    except Exception as e:
        # Fallback to deterministic generation
        import logging
        logging.warning(f"LLM generation failed, falling back to deterministic: {e}")
        
        questions: List[QuizQuestion] = []
        for i in range(payload.num_questions):
            questions.append(_generate_mcq_for_topic(topic, payload.difficulty, payload.options_per_question, i))

        quiz_id = f"ai-{topic.replace(' ', '-').lower()}-{int(time.time())}"
        title = f"{topic.title()} — {payload.difficulty.title()} Quiz (Offline)"
        return {"id": quiz_id, "title": title, "questions": [q.dict() for q in questions]}


class QuizSubmitAiIn(BaseModel):
    path: str | None = None
    questions: List[QuizQuestion]
    answers: List[dict]  # { id: str, answerIndex: int }


@router.post("/submit-ai", response_model=QuizSubmitOut)
def submit_quiz_ai(
    payload: QuizSubmitAiIn,
    session_id: Optional[int] = Query(None, description="Quiz session ID for tracking"),
    authorization: str | None = Header(None),
    db: Session = Depends(get_db)
):
    """Submit AI-generated quiz with session tracking and adaptive metrics."""
    # Build mapping from provided questions
    provided = {q.id: q.answerIndex for q in payload.questions}
    answers = {a.get("id"): int(a.get("answerIndex")) for a in payload.answers}

    results = []
    score = 0
    for qid, correct_idx in provided.items():
        user_idx = answers.get(qid, -1)
        correct = user_idx == correct_idx
        if correct:
            score += 1
        # We don't have per-question texts here; explanation optional
        results.append(QuizSubmitOutItem(id=qid, correct=correct, correctIndex=correct_idx, explanation=None))

    out = QuizSubmitOut(score=score, total=len(provided), results=results)

    # Store attempt if token present
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        sub = decode_token(authorization.split(" ",1)[1])
        if sub:
            user_id = int(sub)
    
    if user_id:
        path = payload.path or next(iter(provided.keys()), "ai-quiz")
        passed = score >= max(1, len(provided) // 2 + (len(provided) % 2))
        
        # Update or create QuizSession
        if session_id:
            session = db.query(QuizSession).filter(QuizSession.id == session_id, QuizSession.user_id == user_id).first()
            if session:
                session.completed_at = datetime.now(timezone.utc)
                session.score = score
                session.total_questions = len(provided)
                session.passed = passed
                # Update session answers with results
                if not session.answers:
                    session.answers = []
                session.answers.extend([{
                    "question_id": qid,
                    "user_answer": answers.get(qid, -1),
                    "correct": correct_idx == answers.get(qid, -1),
                    "time_ms": None  # Frontend should provide this
                } for qid, correct_idx in provided.items()])
                db.commit()
        
        # Also store in legacy QuizAttempt
        db.add(QuizAttempt(user_id=user_id, path=str(path), score=score, total=len(provided), passed=passed))
        db.commit()
    
    return out

@router.get("/generate-stream")
async def generate_quiz_stream(
    topic: str = Query(...),
    difficulty: str = Query("medium"),
    num_questions: int = Query(5),
    options_per_question: int = Query(4),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Stream AI quiz generation using Server-Sent Events.
    Questions are yielded as they're generated.
    """
    # Rate limit: 10 streaming generations per 5 minutes per user
    from ...services.rate_limiter import rate_limit
    rate_limit(user.id, "quizzes:generate-stream", limit=10, window_seconds=300)
    
    topic = topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")
    
    # Build payload from query params
    payload = QuizGenIn(
        topic=topic,
        difficulty=difficulty,
        num_questions=num_questions,
        options_per_question=options_per_question
    )
    
    async def event_generator():
        try:
            provider = get_llm_provider()
            
            # Send initial metadata
            quiz_id = f"ai-{topic.replace(' ', '-').lower()}-{int(time.time())}"
            title = f"{topic.title()} — {payload.difficulty.title()} Quiz"
            
            yield f"data: {json.dumps({'type': 'metadata', 'id': quiz_id, 'title': title})}\n\n"
            
            # Stream questions
            question_count = 0
            async for question in provider.generate_quiz_questions_stream(
                topic=topic,
                difficulty=payload.difficulty,
                num_questions=payload.num_questions,
                options_per_question=payload.options_per_question
            ):
                question_count += 1
                yield f"data: {json.dumps({'type': 'question', 'data': question})}\n\n"
                await asyncio.sleep(0.1)  # Small delay for client processing
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete', 'total': question_count})}\n\n"
        
        except Exception as e:
            import logging
            logging.error(f"Streaming generation failed: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/saved", response_model=List[dict])
def get_saved_quizzes(
    user = Depends(get_current_user),
    db: Session = Depends(get_db),
    topic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    limit: int = Query(20, le=100)
):
    """Get user's saved AI-generated quizzes."""
    query = db.query(GeneratedQuiz).filter(
        GeneratedQuiz.user_id == user.id,
        GeneratedQuiz.is_archived == False
    )
    
    if topic:
        query = query.filter(GeneratedQuiz.topic.ilike(f"%{topic}%"))
    if difficulty:
        query = query.filter(GeneratedQuiz.difficulty == difficulty)
    
    quizzes = query.order_by(GeneratedQuiz.created_at.desc()).limit(limit).all()
    
    return [{
        "id": q.id,
        "topic": q.topic,
        "difficulty": q.difficulty,
        "title": q.title,
        "num_questions": len(q.questions) if q.questions else 0,
        "times_taken": q.times_taken,
        "best_score": q.best_score,
        "best_score_total": q.best_score_total,
        "is_favorite": q.is_favorite,
        "created_at": q.created_at.isoformat() if q.created_at else None,
        "last_taken_at": q.last_taken_at.isoformat() if q.last_taken_at else None
    } for q in quizzes]


@router.get("/saved/{quiz_id}", response_model=QuizEnvelope)
def get_saved_quiz(
    quiz_id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve a saved AI quiz for retake."""
    quiz = db.query(GeneratedQuiz).filter(
        GeneratedQuiz.id == quiz_id,
        GeneratedQuiz.user_id == user.id
    ).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return {
        "id": f"saved-{quiz.id}",
        "title": quiz.title,
        "questions": quiz.questions
    }


@router.post("/saved/{quiz_id}/favorite")
def toggle_favorite(
    quiz_id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle favorite status on a saved quiz."""
    quiz = db.query(GeneratedQuiz).filter(
        GeneratedQuiz.id == quiz_id,
        GeneratedQuiz.user_id == user.id
    ).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz.is_favorite = not quiz.is_favorite
    db.commit()
    
    return {"is_favorite": quiz.is_favorite}


@router.delete("/saved/{quiz_id}")
def archive_saved_quiz(
    quiz_id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive (soft delete) a saved quiz."""
    quiz = db.query(GeneratedQuiz).filter(
        GeneratedQuiz.id == quiz_id,
        GeneratedQuiz.user_id == user.id
    ).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz.is_archived = True
    db.commit()
    
    return {"archived": True}


@router.post("/session/start")
def start_quiz_session(
    quiz_id: Optional[int] = Query(None, description="Saved quiz ID"),
    path: Optional[str] = Query(None, description="Static quiz path"),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new quiz session for tracking and adaptive difficulty."""
    session = QuizSession(
        user_id=user.id,
        quiz_id=quiz_id,
        quiz_path=path,
        total_questions=0  # Will be updated on submit
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {"session_id": session.id, "started_at": session.started_at.isoformat()}


@router.get("/_debug-path")
def debug_path(path: str = ""):
    return {"received_path": path}
