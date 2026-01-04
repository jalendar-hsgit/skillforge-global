"""
Mentor Verification Model - For document-based mentor verification
Allows mentors to upload verification documents (ID, degree, certification)
Admin can approve or reject verifications
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.db import Base
from datetime import datetime
import enum


class VerificationStatus(str, enum.Enum):
    """Verification status enumeration"""
    PENDING = "pending"      # Awaiting admin review
    APPROVED = "approved"    # Verified and approved
    REJECTED = "rejected"    # Verification rejected
    EXPIRED = "expired"      # Verification expired


class DocumentType(str, enum.Enum):
    """Types of documents that can be verified"""
    GOVERNMENT_ID = "government_id"      # Passport, Driver's License, National ID
    DEGREE = "degree"                    # Bachelor's, Master's degree
    CERTIFICATION = "certification"      # Professional certifications
    CREDENTIAL = "credential"            # Other credentials


class MentorVerification(Base):
    """
    Mentor verification document tracking.
    Mentors upload documents, admins review and approve/reject.
    """
    __tablename__ = "mentor_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Document Information
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    document_url = Column(String, nullable=False)  # S3 or local file path
    document_name = Column(String, nullable=False)  # Original filename
    file_size = Column(Integer, nullable=False)  # Bytes
    mime_type = Column(String, nullable=True)  # application/pdf, image/jpeg, etc.
    
    # Verification Status
    status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False, index=True)
    
    # Review Information
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # Admin who reviewed
    reviewer_notes = Column(Text, nullable=True)  # Admin's notes (reason for rejection, etc.)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)  # Optional expiration date
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    mentor = relationship("Mentor", foreign_keys=[mentor_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id], viewonly=True)
    
    def __repr__(self):
        return f"<MentorVerification(id={self.id}, mentor_id={self.mentor_id}, status={self.status}, type={self.document_type})>"
