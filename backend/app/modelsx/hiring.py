"""
Recruiting and Hiring Platform Models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db import Base
import enum


class ApplicationStatus(str, enum.Enum):
    """Application lifecycle stages"""
    APPLIED = "applied"
    SCREENING = "screening"
    PHONE_SCREEN = "phone_screen"
    TECHNICAL_TEST = "technical_test"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWING = "interviewing"
    BACKGROUND_CHECK = "background_check"
    OFFER_SENT = "offer_sent"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"
    HIRED = "hired"
    REJECTED = "rejected"


class VerificationStatus(str, enum.Enum):
    """Verification check status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    FAILED = "failed"
    DISPUTED = "disputed"


# ==================== Company & Job Management ====================

class Company(Base):
    """Companies hiring on platform"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), unique=True, index=True)
    
    # Company Info
    description = Column(Text)
    industry = Column(String(100))
    size = Column(String(50))  # "1-10", "11-50", "51-200", etc.
    website = Column(String(500))
    logo_url = Column(String(500))
    
    # Contact
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    
    # Location
    headquarters = Column(String(255))
    locations = Column(JSON)  # Multiple office locations
    
    # Settings
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Subscription
    plan_type = Column(String(50), default="free")  # free, basic, pro, enterprise
    jobs_limit = Column(Integer, default=3)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    jobs = relationship("JobPosting", back_populates="company", cascade="all, delete-orphan")
    team_members = relationship("CompanyTeamMember", back_populates="company")


class CompanyTeamMember(Base):
    """Company team members (recruiters, hiring managers)"""
    __tablename__ = "company_team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    role = Column(String(50), nullable=False)  # "admin", "recruiter", "hiring_manager", "interviewer"
    permissions = Column(JSON)  # Granular permissions
    
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="team_members")


class JobPosting(Base):
    """Job listings"""
    __tablename__ = "job_postings"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Job Details
    title = Column(String(255), nullable=False)
    slug = Column(String(255), index=True)
    description = Column(Text, nullable=False)
    requirements = Column(JSON)  # List of requirements
    responsibilities = Column(JSON)
    
    # Classification
    department = Column(String(100))
    employment_type = Column(String(50))  # "full_time", "part_time", "contract", "intern"
    experience_level = Column(String(50))  # "entry", "mid", "senior", "lead", "executive"
    
    # Location & Remote
    location = Column(String(255))
    is_remote = Column(Boolean, default=False)
    remote_type = Column(String(50))  # "fully_remote", "hybrid", "office"
    
    # Compensation
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(String(10), default="USD")
    equity_offered = Column(Boolean, default=False)
    
    # Skills & Keywords
    required_skills = Column(JSON)  # ["Python", "React", "AWS"]
    nice_to_have_skills = Column(JSON)
    keywords = Column(JSON)  # For matching algorithm
    
    # Application Settings
    application_deadline = Column(DateTime)
    positions_available = Column(Integer, default=1)
    
    # Status
    status = Column(String(50), default="draft")  # draft, published, closed, filled
    is_featured = Column(Boolean, default=False)
    
    # Analytics
    views = Column(Integer, default=0)
    applications_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Relationships
    company = relationship("Company", back_populates="jobs")
    applications = relationship("app.modelsx.hiring.HiringJobApplication", back_populates="job")


# ==================== Application & Screening ====================

class HiringJobApplication(Base):
    """Candidate applications to jobs"""
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Application Details
    cover_letter = Column(Text)
    status = Column(String(50), default=ApplicationStatus.APPLIED)
    
    # AI Screening
    match_score = Column(Float, default=0.0)  # 0-100 AI compatibility score
    screening_notes = Column(JSON)  # AI-generated insights
    
    # Skills Match
    matching_skills = Column(JSON)  # Skills that match job
    missing_skills = Column(JSON)  # Skills candidate lacks
    
    # Recruiter Actions
    recruiter_rating = Column(Integer)  # 1-5 stars
    recruiter_notes = Column(Text)
    flagged = Column(Boolean, default=False)
    
    # Timeline
    applied_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    rejected_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Relationships (using fully-qualified paths to avoid registry conflicts)
    job = relationship("JobPosting", back_populates="applications")
    interviews = relationship("Interview", back_populates="application")
    assessments = relationship("TechnicalAssessment", back_populates="application")
    background_checks = relationship("BackgroundCheck", back_populates="application")


# ==================== Interview Management ====================

class Interview(Base):
    """Interview scheduling and management"""
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)
    
    # Interview Details
    type = Column(String(50), nullable=False)  # "phone", "technical", "behavioral", "panel", "final"
    round_number = Column(Integer, default=1)
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50))
    
    # Meeting Info
    meeting_link = Column(String(500))  # Zoom, Google Meet, etc.
    location = Column(String(500))  # For in-person
    
    # Interviewers
    interviewer_ids = Column(JSON)  # List of user IDs
    
    # Status
    status = Column(String(50), default="scheduled")  # scheduled, completed, cancelled, no_show
    
    # Recording & Notes
    recording_url = Column(String(500))
    transcript = Column(Text)
    interviewer_notes = Column(Text)
    
    # AI Analysis
    ai_sentiment_score = Column(Float)  # -1 to 1 (negative to positive)
    ai_confidence_level = Column(Float)  # 0-100
    ai_key_insights = Column(JSON)
    
    # Scoring
    technical_score = Column(Integer)  # 1-10
    communication_score = Column(Integer)
    cultural_fit_score = Column(Integer)
    overall_score = Column(Integer)
    
    # Recommendation
    recommendation = Column(String(50))  # "strong_yes", "yes", "maybe", "no", "strong_no"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    application = relationship("app.modelsx.hiring.HiringJobApplication", back_populates="interviews")


# ==================== Technical Assessment ====================

class TechnicalAssessment(Base):
    """Coding tests and technical evaluations"""
    __tablename__ = "technical_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)
    
    # Assessment Type
    type = Column(String(50), nullable=False)  # "coding_test", "take_home", "live_coding", "quiz"
    difficulty = Column(String(50))  # "easy", "medium", "hard"
    
    # Assignment
    title = Column(String(255))
    description = Column(Text)
    instructions = Column(Text)
    problems = Column(JSON)  # List of problems/questions
    
    # Timing
    time_limit_minutes = Column(Integer)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    submitted_at = Column(DateTime)
    deadline = Column(DateTime)
    
    # Submission
    submission_url = Column(String(500))  # GitHub repo, code sandbox, etc.
    submission_code = Column(Text)
    submission_notes = Column(Text)
    
    # Scoring
    auto_score = Column(Float)  # Automated test results
    manual_score = Column(Float)  # Human review
    final_score = Column(Float)  # Combined score
    
    # Analysis
    test_cases_passed = Column(Integer)
    test_cases_total = Column(Integer)
    code_quality_score = Column(Float)
    time_complexity_score = Column(Float)
    
    # Plagiarism Detection
    plagiarism_detected = Column(Boolean, default=False)
    similarity_score = Column(Float)
    
    # Review
    reviewer_notes = Column(Text)
    feedback = Column(Text)
    
    status = Column(String(50), default="pending")  # pending, in_progress, submitted, graded
    
    application = relationship("app.modelsx.hiring.HiringJobApplication", back_populates="assessments")


# ==================== Background Verification ====================

class BackgroundCheck(Base):
    """Background verification and checks"""
    __tablename__ = "background_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)
    
    # Check Type
    check_type = Column(String(50), nullable=False)  # "education", "employment", "criminal", "identity", "credit"
    
    # Provider
    provider = Column(String(100))  # "internal", "checkr", "truework", "sterling", etc.
    provider_request_id = Column(String(255))
    
    # Status
    status = Column(String(50), default=VerificationStatus.PENDING)
    
    # Details
    details = Column(JSON)  # Check-specific details
    verification_data = Column(JSON)  # Results from provider
    
    # Results
    result = Column(String(50))  # "clear", "consider", "suspended", "dispute"
    findings = Column(JSON)  # Issues found
    
    # Timing
    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Cost
    cost = Column(Float)
    currency = Column(String(10), default="USD")
    
    application = relationship("app.modelsx.hiring.HiringJobApplication", back_populates="background_checks")


class EducationVerification(Base):
    """Education credential verification"""
    __tablename__ = "education_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    field_of_study = Column(String(255))
    graduation_date = Column(String(50))
    
    # Verification
    status = Column(String(50), default=VerificationStatus.PENDING)
    verified_by = Column(String(100))  # Institution contact or service
    verified_at = Column(DateTime)
    
    # Documents
    transcript_url = Column(String(500))
    certificate_url = Column(String(500))
    
    # Details
    verification_notes = Column(Text)
    gpa_verified = Column(String(20))
    honors = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class EmploymentVerification(Base):
    """Employment history verification"""
    __tablename__ = "employment_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    start_date = Column(String(50))
    end_date = Column(String(50))
    
    # Verification
    status = Column(String(50), default=VerificationStatus.PENDING)
    verified_by = Column(String(255))  # HR contact
    verified_at = Column(DateTime)
    
    # Details
    employment_type = Column(String(50))  # full_time, part_time, contract
    salary_verified = Column(Boolean, default=False)
    reason_for_leaving = Column(Text)
    eligible_for_rehire = Column(Boolean)
    
    # Contact
    hr_contact_name = Column(String(255))
    hr_contact_email = Column(String(255))
    hr_contact_phone = Column(String(50))
    
    verification_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReferenceCheck(Base):
    """Professional reference checks"""
    __tablename__ = "reference_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)
    
    # Reference Contact
    name = Column(String(255), nullable=False)
    relationship = Column(String(100))  # "manager", "colleague", "client"
    company = Column(String(255))
    position = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    
    # Request
    requested_at = Column(DateTime, default=datetime.utcnow)
    reminder_sent_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Response
    status = Column(String(50), default="pending")  # pending, completed, declined, expired
    responses = Column(JSON)  # Questionnaire answers
    rating = Column(Integer)  # 1-5 overall rating
    
    # AI Analysis
    sentiment = Column(String(50))  # positive, neutral, negative
    red_flags = Column(JSON)  # Potential concerns
    
    # Verification
    verified = Column(Boolean, default=False)
    verification_method = Column(String(50))  # email, phone, linkedin
    
    notes = Column(Text)


# ==================== Offer Management ====================

class JobOffer(Base):
    """Job offer management"""
    __tablename__ = "job_offers"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)
    
    # Offer Details
    position_title = Column(String(255), nullable=False)
    start_date = Column(DateTime)
    
    # Compensation
    base_salary = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    signing_bonus = Column(Float, default=0)
    equity_percentage = Column(Float)
    equity_shares = Column(Integer)
    
    # Benefits
    benefits = Column(JSON)  # Health, dental, 401k, etc.
    pto_days = Column(Integer)
    remote_policy = Column(String(100))
    
    # Documents
    offer_letter_url = Column(String(500))
    contract_url = Column(String(500))
    
    # Status
    status = Column(String(50), default="draft")  # draft, sent, viewed, accepted, declined, expired
    
    # Timeline
    sent_at = Column(DateTime)
    viewed_at = Column(DateTime)
    response_deadline = Column(DateTime)
    responded_at = Column(DateTime)
    
    # Negotiation
    is_negotiable = Column(Boolean, default=True)
    candidate_counter_offer = Column(JSON)
    negotiation_notes = Column(Text)
    
    # E-Signature
    esignature_url = Column(String(500))
    signed = Column(Boolean, default=False)
    signed_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== Analytics ====================

class HiringMetrics(Base):
    """Hiring funnel analytics"""
    __tablename__ = "hiring_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_postings.id"))
    
    metric_date = Column(DateTime, default=datetime.utcnow)
    
    # Funnel Metrics
    applications_received = Column(Integer, default=0)
    applications_screened = Column(Integer, default=0)
    phone_screens = Column(Integer, default=0)
    technical_tests = Column(Integer, default=0)
    interviews_conducted = Column(Integer, default=0)
    offers_sent = Column(Integer, default=0)
    offers_accepted = Column(Integer, default=0)
    hires = Column(Integer, default=0)
    
    # Time Metrics
    avg_time_to_screen_days = Column(Float)
    avg_time_to_interview_days = Column(Float)
    avg_time_to_offer_days = Column(Float)
    avg_time_to_hire_days = Column(Float)
    
    # Cost Metrics
    cost_per_hire = Column(Float)
    recruiter_hours_spent = Column(Float)
    
    # Quality Metrics
    acceptance_rate = Column(Float)  # % of offers accepted
    quality_of_hire_score = Column(Float)  # 1-10
