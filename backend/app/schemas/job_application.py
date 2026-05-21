"""
Pydantic schemas for Job Application API
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ApplicationStatus(str, Enum):
    WISHLIST = "wishlist"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    ASSESSMENT = "assessment"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class InterviewDetail(BaseModel):
    """Interview details"""
    date: datetime
    type: str = Field(..., description="phone, video, in-person, etc.")
    interviewer: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None  # pending, completed, etc.

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-01-15T10:00:00",
                "type": "phone",
                "interviewer": "Jane Smith",
                "notes": "Technical interview with focus on Python",
                "status": "scheduled"
            }
        }


class ContactDetail(BaseModel):
    """Contact details"""
    name: str
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "role": "Hiring Manager",
                "email": "john@company.com",
                "phone": "+1-555-123-4567",
                "linkedin": "linkedin.com/in/johndoe"
            }
        }


class OfferDetails(BaseModel):
    """Offer details"""
    salary: Optional[float] = None
    signing_bonus: Optional[float] = None
    equity_percent: Optional[float] = None
    equity_vesting_years: Optional[int] = None
    benefits: List[str] = Field(default_factory=list)
    start_date: Optional[datetime] = None
    negotiated: Optional[bool] = False
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "salary": 150000,
                "signing_bonus": 20000,
                "equity_percent": 0.5,
                "equity_vesting_years": 4,
                "benefits": ["Health Insurance", "401k", "Remote Work"],
                "start_date": "2025-03-01T00:00:00"
            }
        }


class JobApplicationBase(BaseModel):
    """Base job application schema"""
    company_name: str
    position_title: str
    job_type: JobType = JobType.FULL_TIME
    location: Optional[str] = None
    work_mode: Optional[str] = None
    job_url: Optional[str] = None
    description: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.APPLIED
    priority: int = Field(default=3, ge=1, le=5)
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    resume_id: Optional[int] = None
    cover_letter_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    application_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    response_date: Optional[datetime] = None
    offer_date: Optional[datetime] = None
    interviews: List[InterviewDetail] = Field(default_factory=list)
    contacts: List[ContactDetail] = Field(default_factory=list)
    skills_required: List[str] = Field(default_factory=list)
    skills_matched: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    offer_details: Optional[OfferDetails] = None
    source: Optional[str] = None
    referral_name: Optional[str] = None


class JobApplicationCreate(JobApplicationBase):
    """Create job application"""
    pass


class JobApplicationUpdate(BaseModel):
    """Update job application (all fields optional)"""
    company_name: Optional[str] = None
    position_title: Optional[str] = None
    job_type: Optional[JobType] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    job_url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    resume_id: Optional[int] = None
    cover_letter_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    deadline: Optional[datetime] = None
    response_date: Optional[datetime] = None
    offer_date: Optional[datetime] = None
    interviews: Optional[List[InterviewDetail]] = None
    contacts: Optional[List[ContactDetail]] = None
    skills_required: Optional[List[str]] = None
    skills_matched: Optional[List[str]] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    offer_details: Optional[OfferDetails] = None


class JobApplicationOut(JobApplicationBase):
    """Job application response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    days_since_applied: Optional[int] = None
    days_until_deadline: Optional[int] = None
    is_overdue: bool = False
    response_time_days: Optional[int] = None

    class Config:
        from_attributes = True


class JobApplicationStats(BaseModel):
    """Job application statistics"""
    total_applications: int
    by_status: Dict[str, int]
    response_rate: float
    avg_response_time_days: Optional[float] = None
    avg_salary_min: Optional[float] = None
    avg_salary_max: Optional[float] = None
    applications_this_month: int
    offers_received: int
    interviews_scheduled: int
    overdue_follow_ups: int

    class Config:
        json_schema_extra = {
            "example": {
                "total_applications": 25,
                "by_status": {
                    "applied": 10,
                    "screening": 5,
                    "interview": 3,
                    "offer": 2,
                    "rejected": 5
                },
                "response_rate": 0.68,
                "avg_response_time_days": 7,
                "avg_salary_min": 100000,
                "avg_salary_max": 150000,
                "applications_this_month": 8,
                "offers_received": 2,
                "interviews_scheduled": 3,
                "overdue_follow_ups": 1
            }
        }
