"""
Mentor Verification System Models
Handles mentor document uploads and approval workflow
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.db import Base
from datetime import datetime
import enum


class DocumentType(str, enum.Enum):
    """Types of documents mentors can upload for verification"""
    CERTIFICATION = "certification"       # Professional certifications
    ID_VERIFICATION = "id_verification"   # Government ID
    DEGREE = "degree"                     # University degree
    EXPERIENCE = "experience"             # Experience letter
    LICENSE = "license"                   # Professional license
    PORTFOLIO = "portfolio"               # Work portfolio
    OTHER = "other"                       # Other documents


class DocumentStatus(str, enum.Enum):
    """Status of uploaded document"""
    PENDING = "pending"                   # Awaiting review
    APPROVED = "approved"                 # Approved by admin
    REJECTED = "rejected"                 # Rejected with reason
    EXPIRED = "expired"                   # Document expired


class ApprovalAction(str, enum.Enum):
    """Action taken by admin reviewer"""
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUEST_MORE = "request_more_info"


class MentorDocument(Base):
    """
    Stores documents uploaded by mentors for verification
    One mentor can upload multiple documents
    """
    __tablename__ = "mentor_documents"

    id = Column(Integer, primary_key=True, index=True)
    
    # References
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False, index=True)
    
    # Document info
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    filename = Column(String, nullable=False)  # Original filename
    filepath = Column(String, nullable=False)  # Storage path on server/S3
    file_size = Column(Integer, nullable=True)  # File size in bytes
    mime_type = Column(String, nullable=True)  # e.g., application/pdf
    
    # Status tracking
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False, index=True)
    rejection_reason = Column(Text, nullable=True)  # Why document was rejected
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    reviewed_at = Column(DateTime, nullable=True)  # When admin reviewed it
    expires_at = Column(DateTime, nullable=True)  # Optional expiration date
    
    # Relationships
    mentor = relationship("Mentor", back_populates="documents")
    approvals = relationship("MentorApproval", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MentorDocument {self.id}: {self.document_type.value} - {self.status.value}>"


class MentorApproval(Base):
    """
    Audit trail for document approvals
    Records who reviewed each document and what action they took
    """
    __tablename__ = "mentor_approvals"

    id = Column(Integer, primary_key=True, index=True)
    
    # References
    document_id = Column(Integer, ForeignKey("mentor_documents.id"), nullable=False, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Admin/reviewer who approved/rejected
    
    # Action taken
    action = Column(SQLEnum(ApprovalAction), nullable=False, index=True)
    reason = Column(Text, nullable=True)  # Detailed reason for decision
    
    # Timestamp
    reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    document = relationship("MentorDocument", back_populates="approvals")
    # Note: User relationship would be: reviewer = relationship("User")
    
    def __repr__(self):
        return f"<MentorApproval {self.id}: {self.action.value} by user {self.reviewer_id}>"
