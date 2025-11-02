"""
Job Application tracking model for career management
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.db import Base


class ApplicationStatus(str, enum.Enum):
    """Job application status"""
    WISHLIST = "wishlist"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    ASSESSMENT = "assessment"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class JobType(str, enum.Enum):
    """Job type classification"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class JobApplication(Base):
    """Job application tracking model"""
    __tablename__ = "job_application_tracker"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Company and position details
    company_name = Column(String(255), nullable=False, index=True)
    position_title = Column(String(255), nullable=False, index=True)
    job_type = Column(SQLEnum(JobType), default=JobType.FULL_TIME)
    location = Column(String(255))
    work_mode = Column(String(50))  # remote, hybrid, onsite
    job_url = Column(Text)
    description = Column(Text)
    
    # Application status
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.APPLIED, index=True)
    priority = Column(Integer, default=3)  # 1-5 scale
    
    # Salary information
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(10), default="USD")
    
    # Application materials
    resume_id = Column(Integer, nullable=True)  # Link to resume used
    cover_letter_url = Column(Text)  # Could be file path or external URL
    portfolio_url = Column(Text)
    
    # Important dates
    application_date = Column(DateTime, default=datetime.utcnow, index=True)
    deadline = Column(DateTime, nullable=True)
    response_date = Column(DateTime, nullable=True)
    offer_date = Column(DateTime, nullable=True)
    
    # Interview details (stored as JSON array)
    # Format: [{"date": "2025-01-15T10:00:00", "type": "phone", "interviewer": "John Doe", "notes": "..."}]
    interviews = Column(JSON, default=list)
    
    # Contacts (stored as JSON array)
    # Format: [{"name": "Jane Smith", "role": "HR Manager", "email": "jane@company.com", "phone": "...", "linkedin": "..."}]
    contacts = Column(JSON, default=list)
    
    # Skills and requirements
    skills_required = Column(JSON, default=list)  # List of skill names
    skills_matched = Column(JSON, default=list)  # Skills from resume that match
    
    # Notes and tracking
    notes = Column(Text)
    follow_up_date = Column(DateTime, nullable=True)
    
    # Offer details (if applicable)
    offer_details = Column(JSON, nullable=True)
    # Format: {"salary": 120000, "benefits": [...], "start_date": "...", "equity": "...", "bonus": "..."}
    
    # Source tracking
    source = Column(String(100))  # LinkedIn, Indeed, Company Website, Referral, etc.
    referral_name = Column(String(255))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # user = relationship("User", back_populates="job_applications")

    def __repr__(self):
        return f"<JobApplication {self.position_title} at {self.company_name} ({self.status})>"

    @property
    def days_since_applied(self):
        """Calculate days since application"""
        if self.application_date:
            return (datetime.utcnow() - self.application_date).days
        return None

    @property
    def days_until_deadline(self):
        """Calculate days until deadline"""
        if self.deadline:
            return (self.deadline - datetime.utcnow()).days
        return None

    @property
    def is_overdue(self):
        """Check if follow-up is overdue"""
        if self.follow_up_date:
            return datetime.utcnow() > self.follow_up_date
        return False

    @property
    def response_time_days(self):
        """Calculate response time in days"""
        if self.response_date and self.application_date:
            return (self.response_date - self.application_date).days
        return None
