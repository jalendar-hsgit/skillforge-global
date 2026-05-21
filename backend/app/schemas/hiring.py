"""
Pydantic schemas for Hiring Platform
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class ApplicationStatusEnum(str, Enum):
    APPLIED = "applied"
    UNDER_REVIEW = "under_review"
    PHONE_SCREEN = "phone_screen"
    TECHNICAL_TEST = "technical_test"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWING = "interviewing"
    OFFER_SENT = "offer_sent"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    HIRED = "hired"


class VerificationStatusEnum(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


# ==================== COMPANY ====================

class CompanyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    industry: Optional[str] = None
    size: Optional[str] = Field(None, description="e.g., '1-10', '11-50', '51-200', etc.")
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyOut(CompanyBase):
    id: int
    subscription_plan: str
    active_jobs: int
    total_applications: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== JOB POSTING ====================

class JobPostingBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    location: Optional[str] = None
    remote_option: Optional[str] = Field(None, description="on_site, remote, hybrid")
    employment_type: Optional[str] = Field(None, description="full_time, part_time, contract, internship")
    experience_level: Optional[str] = Field(None, description="entry, mid, senior, lead, executive")
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    required_skills: Optional[List[str]] = []
    keywords: Optional[List[str]] = []


class JobPostingCreate(JobPostingBase):
    company_id: int


class JobPostingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, description="draft, published, closed")
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None


class JobPostingOut(JobPostingBase):
    id: int
    company_id: int
    company_name: str
    status: str
    applications_count: int
    posted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== APPLICATION ====================

class JobApplicationCreate(BaseModel):
    job_id: int
    resume_id: int
    cover_letter: Optional[str] = None


class JobApplicationOut(BaseModel):
    id: int
    job_id: int
    job_title: str
    company_name: str
    user_id: int
    resume_id: int
    status: str
    match_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    applied_at: datetime
    reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ApplicationAnalysis(BaseModel):
    job_title: str
    company: str
    match_score: float
    recommendation: str  # strong_match, good_match, potential_match, weak_match
    matching_skills: List[str]
    missing_skills: List[str]
    suggestions: List[str]
    experience_assessment: str


# ==================== INTERVIEW ====================

class InterviewCreate(BaseModel):
    application_id: int
    type: str = Field(..., description="phone, technical, behavioral, final")
    scheduled_at: datetime
    duration_minutes: int = Field(60, ge=15, le=240)
    interviewer_ids: List[int] = []
    notes: Optional[str] = None


class InterviewUpdate(BaseModel):
    status: Optional[str] = Field(None, description="scheduled, completed, cancelled, no_show")
    notes: Optional[str] = None
    recommendation: Optional[str] = Field(None, description="strong_yes, yes, maybe, no, strong_no")
    sentiment_score: Optional[float] = Field(None, ge=0, le=1)


class InterviewOut(BaseModel):
    id: int
    application_id: int
    type: str
    status: str
    scheduled_at: datetime
    duration_minutes: int
    meeting_link: Optional[str] = None
    sentiment_score: Optional[float] = None
    recommendation: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==================== TECHNICAL ASSESSMENT ====================

class AssessmentCreate(BaseModel):
    application_id: int
    type: str = Field(..., description="coding, system_design, quiz, take_home")
    title: str
    description: str
    time_limit_minutes: Optional[int] = None
    deadline: Optional[datetime] = None
    problems: Optional[List[Dict[str, Any]]] = []


class AssessmentSubmit(BaseModel):
    response: Dict[str, Any]
    code_submitted: Optional[str] = None
    submission_url: Optional[str] = None


class AssessmentOut(BaseModel):
    id: int
    application_id: int
    type: str
    title: str
    status: str
    auto_score: Optional[float] = None
    manual_score: Optional[float] = None
    plagiarism_detected: bool
    submitted_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== BACKGROUND CHECK ====================

class BackgroundCheckCreate(BaseModel):
    application_id: int
    check_type: str = Field(..., description="education, employment, criminal, identity, credit")
    provider: Optional[str] = Field("internal", description="internal, checkr, truework, sterling")


class BackgroundCheckOut(BaseModel):
    id: int
    application_id: int
    check_type: str
    provider: str
    status: str
    result: Optional[str] = None
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    cost: Optional[float] = None
    
    class Config:
        from_attributes = True


class BackgroundCheckSummary(BaseModel):
    application_id: int
    total_checks: int
    checks: List[BackgroundCheckOut]
    all_complete: bool
    total_cost: float


# ==================== REFERENCE CHECK ====================

class ReferenceCheckCreate(BaseModel):
    name: str
    email: EmailStr
    relationship: str = Field(..., description="manager, colleague, peer, mentor")
    company: Optional[str] = None
    position: Optional[str] = None


class ReferenceCheckOut(BaseModel):
    id: int
    name: str
    email: str
    relationship: str
    status: str
    sentiment_score: Optional[float] = None
    recommendation: Optional[str] = None
    requested_at: datetime
    responded_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== JOB OFFER ====================

class JobOfferCreate(BaseModel):
    application_id: int
    position_title: str
    base_salary: float = Field(..., gt=0)
    signing_bonus: Optional[float] = Field(0, ge=0)
    equity_amount: Optional[float] = None
    start_date: Optional[datetime] = None
    response_deadline: Optional[datetime] = None
    benefits: Optional[List[str]] = []
    pto_days: Optional[int] = Field(None, ge=0)


class JobOfferUpdate(BaseModel):
    status: Optional[str] = Field(None, description="draft, sent, accepted, declined, expired, withdrawn")
    candidate_counter_offer: Optional[Dict[str, Any]] = None


class JobOfferOut(BaseModel):
    id: int
    application_id: int
    position_title: str
    base_salary: float
    signing_bonus: float
    status: str
    sent_at: Optional[datetime] = None
    response_deadline: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== METRICS ====================

class HiringFunnel(BaseModel):
    applications: int
    phone_screens: int
    interviews: int
    offers_sent: int
    hires: int


class ConversionRates(BaseModel):
    application_to_phone: str
    phone_to_interview: str
    interview_to_offer: str
    offer_to_hire: str


class HiringMetricsOut(BaseModel):
    period: str
    funnel: HiringFunnel
    conversion_rates: ConversionRates
    avg_match_score: float
    avg_time_to_hire_days: Optional[float] = None
    cost_per_hire: Optional[float] = None


# ==================== CANDIDATES LIST ====================

class CandidateListItem(BaseModel):
    id: int
    candidate_name: str
    match_score: float
    status: str
    applied_at: datetime
    matching_skills: List[str]
    interviews_completed: int
    background_checks_complete: bool = False


class CandidatesListOut(BaseModel):
    job_id: int
    total_candidates: int
    candidates: List[CandidateListItem]


# ==================== SKILL VERIFICATION ====================

class SkillVerificationRequest(BaseModel):
    application_id: int
    skills_to_verify: List[str] = Field(..., min_items=1, max_items=10)


class SkillVerificationOut(BaseModel):
    assessment_id: int
    skills_being_verified: List[str]
    time_limit: str
    deadline: datetime
    message: str
    assessment_url: str


# ==================== REFERENCES REQUEST ====================

class ReferenceRequest(BaseModel):
    application_id: int
    references: List[ReferenceCheckCreate] = Field(..., min_items=1, max_items=5)


class ReferenceRequestOut(BaseModel):
    message: str
    references_contacted: int
    response_deadline: datetime
    automated_reminders: bool
