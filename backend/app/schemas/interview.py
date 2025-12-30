"""
Pydantic schemas for interview preparation endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# QuestionCategory Schemas
class QuestionCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    icon_emoji: Optional[str]
    question_count: int
    average_difficulty: float
    
    class Config:
        from_attributes = True


# InterviewQuestion Schemas
class InterviewQuestionCreate(BaseModel):
    category_id: int
    title: str = Field(..., min_length=5, max_length=300)
    description: str = Field(..., min_length=10)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    interview_type: str = Field(default="technical")
    tags: List[str] = Field(default=[])
    company_tags: List[str] = Field(default=[])
    expected_answer: Optional[str] = None
    solution_explanation: Optional[str] = None
    solution_code: Optional[str] = None
    solution_language: str = Field(default="python")
    time_limit_minutes: int = Field(default=30, ge=5, le=120)


class InterviewQuestionResponse(BaseModel):
    id: int
    category_id: int
    title: str
    description: str
    difficulty: str
    interview_type: str
    tags: List[str]
    company_tags: List[str]
    expected_answer: Optional[str]
    solution_explanation: Optional[str]
    solution_code: Optional[str]
    solution_language: str
    time_limit_minutes: int
    attempt_count: int
    success_count: int
    average_rating: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# MockInterview Schemas
class MockInterviewCreate(BaseModel):
    interview_type: str = Field(..., pattern="^(behavioral|technical|system_design|data_structures|coding|mixed)$")
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard|expert)$")
    duration_minutes: int = Field(default=60, ge=30, le=120)
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    target_level: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class MockInterviewStart(BaseModel):
    interview_type: str
    difficulty: str
    question_ids: List[int]
    duration_minutes: int = Field(default=60)
    target_company: Optional[str] = None


class MockInterviewResponse(BaseModel):
    id: int
    user_id: int
    interview_type: str
    difficulty: str
    duration_minutes: int
    target_company: Optional[str]
    target_role: Optional[str]
    status: str
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    total_questions: int
    questions_answered: int
    total_score: float
    correctness_score: float
    clarity_score: float
    efficiency_score: float
    completion_percentage: float
    time_spent_minutes: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# InterviewAnswer Schemas
class InterviewAnswerSubmit(BaseModel):
    question_id: int
    user_answer: str = Field(..., min_length=1)
    answer_language: str = Field(default="python")
    time_spent_seconds: int = Field(default=0, ge=0)


class InterviewAnswerResponse(BaseModel):
    id: int
    mock_interview_id: int
    question_id: int
    user_answer: str
    is_correct: bool
    points_earned: float
    max_points: float
    accuracy_percentage: float
    feedback: Optional[str]
    answered_at: datetime
    
    class Config:
        from_attributes = True


# InterviewSchedule Schemas
class InterviewScheduleCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = None
    interview_type: str = Field(default="mixed")
    difficulty: str = Field(default="medium")
    company_name: Optional[str] = None
    role: Optional[str] = None
    scheduled_date: datetime
    duration_minutes: int = Field(default=60, ge=30, le=120)
    timezone: str = Field(default="UTC")


class InterviewScheduleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class InterviewScheduleResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    interview_type: str
    difficulty: str
    company_name: Optional[str]
    role: Optional[str]
    scheduled_date: datetime
    duration_minutes: int
    status: str
    preparation_status: str
    preparation_percentage: float
    timezone: str
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# InterviewPerformance Schemas
class InterviewPerformanceResponse(BaseModel):
    user_id: int
    total_interviews: int
    completed_interviews: int
    average_score: float
    average_correctness: float
    average_clarity: float
    average_efficiency: float
    by_type_stats: Dict[str, Any]
    by_difficulty_stats: Dict[str, Any]
    best_score: float
    worst_score: float
    average_time_per_question: float
    time_management_score: float
    weak_categories: List[str]
    strong_categories: List[str]
    last_interview_date: Optional[datetime]
    
    class Config:
        from_attributes = True


# InterviewFeedback Schemas
class InterviewFeedbackResponse(BaseModel):
    id: int
    mock_interview_id: int
    overall_feedback: Optional[str]
    technical_feedback: Optional[str]
    communication_feedback: Optional[str]
    problem_solving_feedback: Optional[str]
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    recommended_resources: List[Dict[str, str]]  # {title, url}
    next_practice_areas: List[str]
    score_breakdown: Dict[str, float]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Interview Statistics Schemas
class InterviewSessionStats(BaseModel):
    session_id: int
    total_questions: int
    correct_answers: int
    skipped: int
    accuracy: float
    average_time_per_question: float
    total_time_minutes: float
    score: float
    score_breakdown: Dict[str, float]


class InterviewProgressResponse(BaseModel):
    total_interviews: int
    completed_interviews: int
    average_score: float
    score_trend: List[float]
    interviews_this_month: int
    improvement_percentage: float
    next_scheduled_interview: Optional[InterviewScheduleResponse]


class QuestionBankResponse(BaseModel):
    total_questions: int
    by_difficulty: Dict[str, int]  # {easy: 10, medium: 20, hard: 15}
    by_type: Dict[str, int]  # {technical: 30, behavioral: 10, system_design: 5}
    by_category: Dict[str, int]  # {arrays: 8, trees: 7, ...}
    categories: List[QuestionCategoryResponse]
