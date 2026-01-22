"""
Resume and Career Development Models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db import Base


class Resume(Base):
    """User's resume with versioning"""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)  # e.g., "Software Engineer Resume"
    template_id = Column(String(50), default="modern")  # Template style
    is_primary = Column(Boolean, default=False)  # Primary resume
    
    # Personal Info
    full_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    location = Column(String(255))
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))
    website_url = Column(String(500))
    photo_url = Column(String(500))  # Profile picture
    
    # Professional Summary
    summary = Column(Text)  # AI-generated or custom
    
    # Customization Settings (74 color themes, 12 fonts, 4 picture styles, etc.)
    font_family = Column(String(100), default="Roboto")  # 12 font options
    color_theme = Column(String(50), default="blue")  # 74 color themes
    background_type = Column(String(50), default="none")  # Creative backgrounds
    picture_style = Column(String(50), default="circle")  # 4 picture styles: circle, square, rounded, none
    rating_style = Column(String(50), default="bars")  # bars, dots, stars, circles
    layout = Column(String(50), default="single-column")  # single-column, two-column, sidebar
    
    # Advanced Customization
    accent_color = Column(String(20), default="#2563eb")  # Hex color for accents
    text_color = Column(String(20), default="#000000")
    heading_color = Column(String(20), default="#1f2937")
    line_spacing = Column(Float, default=1.2)
    font_size = Column(Integer, default=11)  # Base font size in pt
    heading_size = Column(Integer, default=14)  # Heading font size in pt
    
    # Sections Configuration
    show_icons = Column(Boolean, default=True)  # Show icons for interests & causes
    sections_order = Column(JSON)  # Custom section ordering
    enabled_sections = Column(JSON)  # Which sections are enabled
    custom_sections = Column(JSON)  # User-defined specialized sections
    extra_content = Column(Text)  # Additional content area (textarea)
    
    # Page Settings
    max_pages = Column(Integer, default=10)  # Up to 10-page CV
    page_margins = Column(JSON, default=dict)  # {"top": 20, "bottom": 20, "left": 20, "right": 20} in mm
    page_size = Column(String(20), default="A4")  # A4, Letter, Legal
    
    # ATS Optimization
    ats_score = Column(Float, default=0.0)  # 0-100 score
    keywords = Column(JSON)  # Extracted keywords
    
    # Style Settings Tracking (for DB tracking)
    style_settings_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    style_settings_history = Column(JSON)  # Track all style changes
    
    # Analytics
    views = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    # Status
    is_public = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    work_experiences = relationship("WorkExperience", back_populates="resume", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="resume", cascade="all, delete-orphan")
    projects = relationship("ResumeProject", back_populates="resume", cascade="all, delete-orphan")
    skills = relationship("ResumeSkill", back_populates="resume", cascade="all, delete-orphan")
    certificates = relationship("ResumeCertificate", back_populates="resume", cascade="all, delete-orphan")
    achievements = relationship("ResumeAchievement", back_populates="resume", cascade="all, delete-orphan")
    versions = relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan", lazy="dynamic")


class WorkExperience(Base):
    """Work experience entries"""
    __tablename__ = "work_experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    location = Column(String(255))
    start_date = Column(String(50))  # e.g., "Jan 2023"
    end_date = Column(String(50))  # e.g., "Present"
    is_current = Column(Boolean, default=False)
    
    description = Column(Text)  # AI-enhanced description
    bullet_points = Column(JSON)  # List of achievements
    
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="work_experiences")


class Education(Base):
    """Education entries"""
    __tablename__ = "education"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)  # e.g., "Bachelor of Science"
    field_of_study = Column(String(255))  # e.g., "Computer Science"
    location = Column(String(255))
    start_date = Column(String(50))
    end_date = Column(String(50))
    gpa = Column(String(20))
    
    description = Column(Text)
    achievements = Column(JSON)  # List of academic achievements
    
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="education")


class ResumeProject(Base):
    """Projects section - AI-generated or custom"""
    __tablename__ = "resume_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    tech_stack = Column(JSON)  # ["React", "Node.js", "MongoDB"]
    
    github_url = Column(String(500))
    demo_url = Column(String(500))
    
    is_ai_generated = Column(Boolean, default=False)
    impact_metrics = Column(JSON)  # {"users": "10k+", "performance": "40% faster"}
    
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="projects")


class ResumeSkill(Base):
    """Skills section with categorization"""
    __tablename__ = "resume_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    category = Column(String(100))  # "Programming", "Frameworks", "Tools", "Soft Skills"
    proficiency = Column(String(50))  # "Beginner", "Intermediate", "Advanced", "Expert"
    
    years_of_experience = Column(Integer)
    is_verified = Column(Boolean, default=False)  # Verified through courses/certifications
    
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="skills")


class ResumeCertificate(Base):
    """Certificates and certifications"""
    __tablename__ = "resume_certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    issuing_organization = Column(String(255), nullable=False)
    issue_date = Column(String(50))
    expiry_date = Column(String(50))
    credential_id = Column(String(255))
    credential_url = Column(String(500))
    
    # Link to our quiz system
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    
    is_verified = Column(Boolean, default=True)
    verification_qr_code = Column(String(500))  # QR code URL
    
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="certificates")


class ResumeAchievement(Base):
    """Awards, honors, and achievements"""
    __tablename__ = "resume_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    date = Column(String(50))
    issuer = Column(String(255))
    
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="achievements")


class ResumeTemplate(Base):
    """Resume templates"""
    __tablename__ = "resume_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # "Modern", "ATS-Friendly", "Creative"
    description = Column(Text)
    category = Column(String(100))  # "Professional", "Technical", "Creative", "Executive"
    
    thumbnail_url = Column(String(500))
    config = Column(JSON)  # Template styling configuration
    
    is_ats_friendly = Column(Boolean, default=True)
    popularity = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AIProjectTemplate(Base):
    """AI-generated project templates"""
    __tablename__ = "ai_project_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100))  # "Web Development", "Data Science", "Mobile", etc.
    difficulty = Column(String(50))  # "Beginner", "Intermediate", "Advanced"
    
    description_template = Column(Text)
    tech_stack = Column(JSON)
    features = Column(JSON)  # List of project features
    impact_metrics_template = Column(JSON)
    
    estimated_hours = Column(Integer)
    popularity = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# Note: ResumeAnalytics is defined in app.modelsx.resume_analytics


class ATSReport(Base):
    """ATS optimization reports"""
    __tablename__ = "ats_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    score = Column(Float, nullable=False)  # 0-100
    
    # Detailed analysis
    formatting_score = Column(Float)
    keywords_score = Column(Float)
    content_score = Column(Float)
    
    suggestions = Column(JSON)  # List of improvement suggestions
    missing_keywords = Column(JSON)
    flagged_issues = Column(JSON)
    
    job_description = Column(Text)  # If matched against a job posting
    
    created_at = Column(DateTime, default=datetime.utcnow)


class CoverLetter(Base):
    """Cover letter with template support"""
    __tablename__ = "cover_letters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)  # Optional link to resume
    title = Column(String(255), nullable=False)
    template_id = Column(String(50), default="modern")
    
    # Header (uses resume personal info if linked)
    full_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    location = Column(String(255))
    
    # Recipient Info
    recipient_name = Column(String(255))
    recipient_title = Column(String(255))
    company_name = Column(String(255))
    company_address = Column(Text)
    
    # Date
    date = Column(String(50))  # "November 4, 2025"
    
    # Salutation
    salutation = Column(String(100), default="Dear Hiring Manager")  # AI-enhanced
    
    # Body Paragraphs (AI-generated or custom)
    opening_paragraph = Column(Text)  # Hook + interest
    body_paragraph_1 = Column(Text)  # Qualifications
    body_paragraph_2 = Column(Text)  # Achievements
    body_paragraph_3 = Column(Text)  # Optional: Why company
    closing_paragraph = Column(Text)  # Call to action
    
    # Closing
    closing_signature = Column(String(100), default="Sincerely")
    
    # Customization
    font_family = Column(String(100), default="Roboto")
    color_theme = Column(String(50), default="blue")
    accent_color = Column(String(20), default="#2563eb")
    
    # Metadata
    job_title = Column(String(255))  # Target job title
    job_description = Column(Text)  # For AI optimization
    
    is_ai_generated = Column(Boolean, default=False)
    ats_score = Column(Float, default=0.0)
    
    views = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Language(Base):
    """Languages - specialized section"""
    __tablename__ = "resume_languages"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    name = Column(String(100), nullable=False)  # "English", "Spanish", etc.
    proficiency = Column(String(50))  # "Native", "Fluent", "Intermediate", "Basic"
    proficiency_level = Column(String(10))  # "C2", "C1", "B2", "B1", "A2", "A1" (CEFR)
    
    is_native = Column(Boolean, default=False)
    certifications = Column(JSON)  # Language certificates
    
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Publication(Base):
    """Publications - specialized section"""
    __tablename__ = "resume_publications"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    title = Column(String(500), nullable=False)
    authors = Column(String(500))  # "Smith, J., Doe, A."
    publisher = Column(String(255))
    publication_date = Column(String(50))
    
    doi = Column(String(255))  # Digital Object Identifier
    url = Column(String(500))
    description = Column(Text)
    
    citations = Column(Integer, default=0)
    type = Column(String(50))  # "Journal", "Conference", "Book", "Preprint"
    
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Patent(Base):
    """Patents - specialized section"""
    __tablename__ = "resume_patents"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    title = Column(String(500), nullable=False)
    patent_number = Column(String(100))
    inventors = Column(String(500))
    filing_date = Column(String(50))
    issue_date = Column(String(50))
    
    status = Column(String(50))  # "Granted", "Pending", "Filed"
    url = Column(String(500))
    description = Column(Text)
    
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class VolunteerWork(Base):
    """Volunteer experience - specialized section"""
    __tablename__ = "resume_volunteer"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    organization = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    location = Column(String(255))
    start_date = Column(String(50))
    end_date = Column(String(50))
    is_current = Column(Boolean, default=False)
    
    description = Column(Text)
    achievements = Column(JSON)  # Bullet points
    
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Reference(Base):
    """References - specialized section"""
    __tablename__ = "resume_references"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    title = Column(String(255))
    company = Column(String(255))
    relationship = Column(String(100))  # "Manager", "Colleague", "Professor"
    
    email = Column(String(255))
    phone = Column(String(50))
    
    permission_granted = Column(Boolean, default=True)
    last_contacted = Column(DateTime)
    
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ResumeContent(Base):
    """Pre-written professional content library"""
    __tablename__ = "resume_content_library"
    
    id = Column(Integer, primary_key=True, index=True)
    
    content_type = Column(String(50))  # "summary", "bullet", "skill_description"
    job_title = Column(String(255))  # "Software Engineer", "Product Manager"
    industry = Column(String(100))  # "Technology", "Healthcare", "Finance"
    seniority = Column(String(50))  # "Entry", "Mid", "Senior", "Executive"
    
    content = Column(Text, nullable=False)  # The actual content
    keywords = Column(JSON)  # Associated keywords
    
    category = Column(String(100))  # "Technical", "Leadership", "Communication"
    popularity = Column(Integer, default=0)
    ai_generated = Column(Boolean, default=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ResumeReview(Base):
    """Professional resume review system"""
    __tablename__ = "resume_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Professional reviewer
    
    status = Column(String(50), default="pending")  # pending, in_progress, completed
    
    # Review Results
    overall_score = Column(Float)  # 1-10
    content_score = Column(Float)
    formatting_score = Column(Float)
    ats_compatibility = Column(Float)
    
    comments = Column(Text)  # General feedback
    suggestions = Column(JSON)  # Specific improvements
    strengths = Column(JSON)  # What's good
    weaknesses = Column(JSON)  # What needs work
    
    # Tracking
    requested_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    turnaround_hours = Column(Integer)  # How long it took
    
    is_paid = Column(Boolean, default=False)
    amount_paid = Column(Float)


class InterviewTracker(Base):
    """Track interviews for money-back guarantee"""
    __tablename__ = "interview_tracker"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    company_name = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    interview_date = Column(DateTime)
    interview_type = Column(String(50))  # "phone", "video", "in-person", "technical"
    
    status = Column(String(50))  # "scheduled", "completed", "cancelled", "offer_received"
    outcome = Column(String(50))  # "passed", "rejected", "offer", "no_response"
    
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Import at end to avoid circular dependency
from app.modelsx.resume_comparison import ResumeVersion
