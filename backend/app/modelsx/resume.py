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
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
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
    
    # Professional Summary
    summary = Column(Text)  # AI-generated or custom
    
    # ATS Optimization
    ats_score = Column(Float, default=0.0)  # 0-100 score
    keywords = Column(JSON)  # Extracted keywords
    
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
    achievements = relationship("Achievement", back_populates="resume", cascade="all, delete-orphan")


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


class Achievement(Base):
    """Awards, honors, and achievements"""
    __tablename__ = "achievements"
    
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


class ResumeAnalytics(Base):
    """Track resume performance"""
    __tablename__ = "resume_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    event_type = Column(String(50))  # "view", "download", "share", "edit"
    event_data = Column(JSON)  # Additional context
    
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    referrer = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)


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
