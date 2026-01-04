"""
Interview Preparation API endpoints
Supports mock interviews, question banks, scheduling, and performance tracking
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.core.security import get_current_user
from app.core.db import get_db
from app.modelsx.interview import (
    QuestionCategory, InterviewQuestion, MockInterview, InterviewAnswer,
    InterviewSchedule, InterviewPerformance, InterviewFeedback,
    InterviewType, InterviewDifficulty, QuestionDifficulty
)
from app.models.user import User
from app.schemas.interview import (
    QuestionCategoryResponse, InterviewQuestionCreate, InterviewQuestionResponse,
    MockInterviewCreate, MockInterviewStart, MockInterviewResponse,
    InterviewAnswerSubmit, InterviewAnswerResponse,
    InterviewScheduleCreate, InterviewScheduleUpdate, InterviewScheduleResponse,
    InterviewPerformanceResponse, InterviewFeedbackResponse,
    InterviewSessionStats, InterviewProgressResponse, QuestionBankResponse
)

router = APIRouter(prefix="/interview", tags=["interview"])


# Question Bank Endpoints
@router.get("/categories", response_model=List[QuestionCategoryResponse])
def get_question_categories(
    db: Session = Depends(get_db)
):
    """Get all question categories"""
    categories = db.query(QuestionCategory).all()
    return categories


@router.get("/questions", response_model=List[InterviewQuestionResponse])
def get_interview_questions(
    category_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    interview_type: Optional[str] = None,
    company: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get interview questions with filters"""
    query = db.query(InterviewQuestion)
    
    if category_id:
        query = query.filter(InterviewQuestion.category_id == category_id)
    
    if difficulty:
        query = query.filter(InterviewQuestion.difficulty == difficulty)
    
    if interview_type:
        query = query.filter(InterviewQuestion.interview_type == interview_type)
    
    if company:
        query = query.filter(InterviewQuestion.company_tags.contains([company]))
    
    questions = query.order_by(
        desc(InterviewQuestion.created_at)
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return questions


@router.get("/questions/{question_id}", response_model=InterviewQuestionResponse)
def get_interview_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific interview question with solution"""
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question


@router.get("/bank-stats", response_model=QuestionBankResponse)
def get_question_bank_stats(
    db: Session = Depends(get_db)
):
    """Get statistics about the question bank"""
    total = db.query(func.count(InterviewQuestion.id)).scalar()
    
    by_difficulty = {}
    for diff in QuestionDifficulty:
        count = db.query(func.count(InterviewQuestion.id)).filter(
            InterviewQuestion.difficulty == diff
        ).scalar()
        by_difficulty[diff.value] = count
    
    by_type = {}
    for itype in InterviewType:
        count = db.query(func.count(InterviewQuestion.id)).filter(
            InterviewQuestion.interview_type == itype
        ).scalar()
        by_type[itype.value] = count
    
    categories = db.query(QuestionCategory).all()
    by_category = {}
    for cat in categories:
        count = db.query(func.count(InterviewQuestion.id)).filter(
            InterviewQuestion.category_id == cat.id
        ).scalar()
        by_category[cat.name] = count
    
    return QuestionBankResponse(
        total_questions=total,
        by_difficulty=by_difficulty,
        by_type=by_type,
        by_category=by_category,
        categories=categories
    )


# Mock Interview Endpoints
@router.post("/mock", response_model=MockInterviewResponse)
def create_mock_interview(
    interview_req: MockInterviewStart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create and start a new mock interview"""
    mock_interview = MockInterview(
        user_id=current_user.id,
        interview_type=interview_req.interview_type,
        difficulty=interview_req.difficulty,
        duration_minutes=interview_req.duration_minutes,
        target_company=interview_req.target_company,
        question_ids=interview_req.question_ids,
        total_questions=len(interview_req.question_ids),
        status="in_progress",
        started_at=datetime.utcnow()
    )
    
    db.add(mock_interview)
    db.commit()
    db.refresh(mock_interview)
    
    return mock_interview


@router.get("/mock/{interview_id}", response_model=MockInterviewResponse)
def get_mock_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mock interview details"""
    interview = db.query(MockInterview).filter(
        MockInterview.id == interview_id,
        MockInterview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    return interview


@router.post("/mock/{interview_id}/answer", response_model=InterviewAnswerResponse)
def submit_interview_answer(
    interview_id: int,
    answer_data: InterviewAnswerSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit answer to interview question"""
    interview = db.query(MockInterview).filter(
        MockInterview.id == interview_id,
        MockInterview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if interview.status != "in_progress":
        raise HTTPException(status_code=400, detail="Interview not in progress")
    
    # Create answer record
    answer = InterviewAnswer(
        mock_interview_id=interview_id,
        question_id=answer_data.question_id,
        user_answer=answer_data.user_answer,
        answer_language=answer_data.answer_language,
        time_spent_seconds=answer_data.time_spent_seconds,
        answered_at=datetime.utcnow()
    )
    
    # Update interview progress
    interview.questions_answered += 1
    interview.time_spent_minutes = int(
        (datetime.utcnow() - interview.started_at).total_seconds() / 60
    )
    
    db.add(answer)
    db.commit()
    db.refresh(answer)
    
    return answer


@router.post("/mock/{interview_id}/complete", response_model=MockInterviewResponse)
def complete_mock_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete a mock interview and generate feedback"""
    interview = db.query(MockInterview).filter(
        MockInterview.id == interview_id,
        MockInterview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Mark as completed
    interview.status = "completed"
    interview.ended_at = datetime.utcnow()
    interview.completion_percentage = (
        (interview.questions_answered / interview.total_questions * 100)
        if interview.total_questions > 0 else 0
    )
    
    # Calculate scores (simplified)
    answers = db.query(InterviewAnswer).filter(
        InterviewAnswer.mock_interview_id == interview_id
    ).all()
    
    if answers:
        correct_count = sum(1 for a in answers if a.is_correct)
        interview.total_score = (correct_count / len(answers) * 100)
        interview.correctness_score = interview.total_score
    
    # Update user performance
    perf = db.query(InterviewPerformance).filter(
        InterviewPerformance.user_id == current_user.id
    ).first()
    
    if not perf:
        perf = InterviewPerformance(user_id=current_user.id)
        db.add(perf)
    
    perf.total_interviews += 1
    perf.completed_interviews += 1
    perf.last_interview_date = datetime.utcnow()
    
    db.commit()
    db.refresh(interview)
    
    return interview


# Interview Schedule Endpoints
@router.post("/schedule", response_model=InterviewScheduleResponse)
def create_interview_schedule(
    schedule_data: InterviewScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedule an interview session"""
    interview_schedule = InterviewSchedule(
        user_id=current_user.id,
        title=schedule_data.title,
        description=schedule_data.description,
        interview_type=schedule_data.interview_type,
        difficulty=schedule_data.difficulty,
        company_name=schedule_data.company_name,
        role=schedule_data.role,
        scheduled_date=schedule_data.scheduled_date,
        duration_minutes=schedule_data.duration_minutes,
        timezone=schedule_data.timezone
    )
    
    db.add(interview_schedule)
    db.commit()
    db.refresh(interview_schedule)
    
    return interview_schedule


@router.get("/schedule", response_model=List[InterviewScheduleResponse])
def get_interview_schedules(
    status: Optional[str] = None,
    upcoming_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's interview schedules"""
    query = db.query(InterviewSchedule).filter(
        InterviewSchedule.user_id == current_user.id
    )
    
    if status:
        query = query.filter(InterviewSchedule.status == status)
    
    if upcoming_only:
        query = query.filter(
            InterviewSchedule.scheduled_date > datetime.utcnow()
        )
    
    schedules = query.order_by(
        InterviewSchedule.scheduled_date
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return schedules


@router.put("/schedule/{schedule_id}", response_model=InterviewScheduleResponse)
def update_interview_schedule(
    schedule_id: int,
    schedule_data: InterviewScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an interview schedule"""
    schedule = db.query(InterviewSchedule).filter(
        InterviewSchedule.id == schedule_id,
        InterviewSchedule.user_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    update_fields = schedule_data.dict(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(schedule, field, value)
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


# Interview Performance Endpoints
@router.get("/performance", response_model=InterviewPerformanceResponse)
def get_interview_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's interview performance statistics"""
    perf = db.query(InterviewPerformance).filter(
        InterviewPerformance.user_id == current_user.id
    ).first()
    
    if not perf:
        raise HTTPException(status_code=404, detail="No performance data")
    
    return perf


@router.get("/progress", response_model=InterviewProgressResponse)
def get_interview_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's interview progress and upcoming interviews"""
    # Get performance stats
    perf = db.query(InterviewPerformance).filter(
        InterviewPerformance.user_id == current_user.id
    ).first()
    
    # Get interviews this month
    month_ago = datetime.utcnow() - timedelta(days=30)
    interviews_month = db.query(func.count(MockInterview.id)).filter(
        MockInterview.user_id == current_user.id,
        MockInterview.created_at >= month_ago
    ).scalar()
    
    # Get next scheduled interview
    next_schedule = db.query(InterviewSchedule).filter(
        InterviewSchedule.user_id == current_user.id,
        InterviewSchedule.scheduled_date > datetime.utcnow()
    ).order_by(InterviewSchedule.scheduled_date).first()
    
    if perf:
        return InterviewProgressResponse(
            total_interviews=perf.total_interviews,
            completed_interviews=perf.completed_interviews,
            average_score=perf.average_score,
            score_trend=perf.score_trend,
            interviews_this_month=interviews_month,
            improvement_percentage=0.0,
            next_scheduled_interview=next_schedule
        )
    else:
        return InterviewProgressResponse(
            total_interviews=0,
            completed_interviews=0,
            average_score=0.0,
            score_trend=[],
            interviews_this_month=0,
            improvement_percentage=0.0,
            next_scheduled_interview=next_schedule
        )


# Interview Feedback Endpoints
@router.get("/feedback/{interview_id}", response_model=InterviewFeedbackResponse)
def get_interview_feedback(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback for a completed interview"""
    interview = db.query(MockInterview).filter(
        MockInterview.id == interview_id,
        MockInterview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    feedback = db.query(InterviewFeedback).filter(
        InterviewFeedback.mock_interview_id == interview_id
    ).first()
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return feedback
