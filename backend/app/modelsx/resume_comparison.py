"""
Resume Comparison Models
Tracks resume versions and comparison history for analytics
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db import Base
from app.models import User


class ResumeVersion(Base):
    """Stores snapshots of resume versions for comparison"""
    __tablename__ = "resume_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Version metadata
    version_number = Column(Integer, default=1)
    version_name = Column(String(200))  # "Final Draft", "Software Engineer v2", etc.
    description = Column(Text)  # What changed in this version
    
    # Snapshot of resume data at this version
    snapshot_data = Column(JSON)  # Full resume data including all sections
    
    # Metrics for comparison
    ats_score = Column(Float)
    word_count = Column(Integer)
    section_count = Column(Integer)
    skill_count = Column(Integer)
    experience_years = Column(Float)
    
    # Performance metrics (if resume was used for applications)
    applications_sent = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    interviews_secured = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False)  # Currently active version
    
    # Relationships
    resume = relationship("Resume", back_populates="versions")
    user = relationship("User")
    comparisons_as_base = relationship(
        "ResumeComparison",
        foreign_keys="ResumeComparison.base_version_id",
        back_populates="base_version"
    )
    comparisons_as_compared = relationship(
        "ResumeComparison",
        foreign_keys="ResumeComparison.compared_version_id",
        back_populates="compared_version"
    )


class ResumeComparison(Base):
    """Stores comparison results between two resume versions"""
    __tablename__ = "resume_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    
    # Versions being compared
    base_version_id = Column(Integer, ForeignKey("resume_versions.id", ondelete="CASCADE"))
    compared_version_id = Column(Integer, ForeignKey("resume_versions.id", ondelete="CASCADE"))
    
    # Comparison results
    differences = Column(JSON)  # Detailed diff: added, removed, modified sections
    score_change = Column(Float)  # ATS score difference
    metrics_change = Column(JSON)  # Word count, skills, etc. changes
    
    # Recommendations
    recommendations = Column(JSON)  # AI-generated suggestions based on comparison
    better_version = Column(String(20))  # "base" or "compared"
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    resume = relationship("Resume")
    base_version = relationship(
        "ResumeVersion",
        foreign_keys=[base_version_id],
        back_populates="comparisons_as_base"
    )
    compared_version = relationship(
        "ResumeVersion",
        foreign_keys=[compared_version_id],
        back_populates="comparisons_as_compared"
    )


class LinkedInImport(Base):
    """Tracks LinkedIn profile imports and OAuth connections"""
    __tablename__ = "linkedin_imports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # LinkedIn OAuth data
    linkedin_id = Column(String(255), unique=True)  # LinkedIn user ID
    access_token = Column(Text)  # Encrypted OAuth token
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)
    
    # Import metadata
    profile_url = Column(String(500))
    profile_data = Column(JSON)  # Raw LinkedIn profile data
    import_count = Column(Integer, default=0)
    last_import_at = Column(DateTime)
    
    # Import settings
    auto_sync = Column(Boolean, default=False)  # Auto-sync profile changes
    sync_frequency_days = Column(Integer, default=30)
    
    # Mapping preferences (which LinkedIn fields map to resume fields)
    field_mappings = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User")
