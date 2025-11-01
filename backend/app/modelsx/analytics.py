"""
Resume Analytics Models

Tracks views, downloads, ATS score history, and sharing events for resumes.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.core.db import Base


class ResumeView(Base):
    """Track resume views (preview page loads)"""
    __tablename__ = "resume_views"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(String, nullable=False, index=True)  # References resumes in SQLite
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for anonymous views
    viewed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Tracking metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    referrer = Column(String(500), nullable=True)
    device_type = Column(String(50), nullable=True)  # mobile, tablet, desktop
    browser = Column(String(100), nullable=True)
    
    # Session tracking
    session_id = Column(String(100), nullable=True)
    view_duration = Column(Integer, nullable=True)  # seconds spent on page

    user = relationship("User", backref="resume_views")


class ResumeDownload(Base):
    """Track resume downloads/exports (PDF, DOCX, etc.)"""
    __tablename__ = "resume_downloads"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    downloaded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Download metadata
    export_format = Column(String(20), nullable=False)  # pdf, docx, json
    template_used = Column(String(50), nullable=True)  # modern, classic, executive, etc.
    file_size = Column(Integer, nullable=True)  # bytes
    
    # Tracking metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    referrer = Column(String(500), nullable=True)

    user = relationship("User", backref="resume_downloads")


class ATSScoreHistory(Base):
    """Track ATS score changes over time"""
    __tablename__ = "ats_score_history"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scored_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # ATS Score breakdown
    overall_score = Column(Float, nullable=False)
    formatting_score = Column(Float, nullable=True)
    keywords_score = Column(Float, nullable=True)
    experience_score = Column(Float, nullable=True)
    education_score = Column(Float, nullable=True)
    skills_score = Column(Float, nullable=True)
    
    # Score metadata
    total_keywords = Column(Integer, nullable=True)
    matched_keywords = Column(Integer, nullable=True)
    missing_keywords = Column(Text, nullable=True)  # JSON array of missing keywords
    suggestions = Column(Text, nullable=True)  # JSON array of improvement suggestions
    
    # Version tracking
    resume_version = Column(Integer, default=1, nullable=False)

    user = relationship("User", backref="ats_score_history")


class ResumeShare(Base):
    """Track resume sharing events"""
    __tablename__ = "resume_shares"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shared_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Share details
    share_method = Column(String(50), nullable=False)  # email, link, linkedin, twitter
    recipient_email = Column(String(255), nullable=True)
    share_link = Column(String(500), nullable=True)  # unique shareable link
    expires_at = Column(DateTime, nullable=True)
    
    # Share engagement
    link_clicks = Column(Integer, default=0)
    last_accessed_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="resume_shares")


class ResumeAnalyticsSummary(Base):
    """Aggregated analytics summary (updated periodically for performance)"""
    __tablename__ = "resume_analytics_summary"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # View metrics
    total_views = Column(Integer, default=0)
    unique_views = Column(Integer, default=0)
    avg_view_duration = Column(Integer, default=0)  # seconds
    
    # Download metrics
    total_downloads = Column(Integer, default=0)
    pdf_downloads = Column(Integer, default=0)
    docx_downloads = Column(Integer, default=0)
    
    # ATS metrics
    current_ats_score = Column(Float, nullable=True)
    highest_ats_score = Column(Float, nullable=True)
    lowest_ats_score = Column(Float, nullable=True)
    ats_score_trend = Column(String(20), nullable=True)  # improving, declining, stable
    
    # Share metrics
    total_shares = Column(Integer, default=0)
    total_share_clicks = Column(Integer, default=0)
    
    # Engagement metrics
    last_viewed_at = Column(DateTime, nullable=True)
    last_downloaded_at = Column(DateTime, nullable=True)
    last_scored_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="resume_analytics_summaries")
