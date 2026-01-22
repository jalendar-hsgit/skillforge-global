"""
Pydantic schemas for Mentor Verification/Document endpoints
Used for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Document type options"""
    CERTIFICATION = "certification"
    ID_VERIFICATION = "id_verification"
    DEGREE = "degree"
    EXPERIENCE = "experience"
    LICENSE = "license"
    PORTFOLIO = "portfolio"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Document status options"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalAction(str, Enum):
    """Admin approval action"""
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUEST_MORE = "request_more_info"


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class DocumentUploadRequest(BaseModel):
    """Request to upload a document"""
    document_type: DocumentType
    # File data will be handled by multipart form data, not JSON


class DocumentApproveRequest(BaseModel):
    """Request to approve a document"""
    action: ApprovalAction = Field(..., description="approval, rejection, or request_more_info")
    reason: Optional[str] = Field(None, description="Reason for decision (required for rejection)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "approved",
                "reason": "Document verified and approved"
            }
        }


class DocumentRejectRequest(BaseModel):
    """Request to reject a document"""
    reason: str = Field(..., min_length=10, description="Must provide reason for rejection")
    
    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Document is blurry and cannot be read clearly"
            }
        }


# ============================================================
# RESPONSE SCHEMAS
# ============================================================

class MentorDocumentResponse(BaseModel):
    """Single document response"""
    id: int
    mentor_id: int
    document_type: DocumentType
    filename: str
    status: DocumentStatus
    rejection_reason: Optional[str] = None
    uploaded_at: datetime
    reviewed_at: Optional[datetime] = None
    file_size: Optional[int] = None
    
    class Config:
        from_attributes = True


class MentorDocumentDetailResponse(MentorDocumentResponse):
    """Detailed document response (includes filepath)"""
    filepath: str
    mime_type: Optional[str] = None
    expires_at: Optional[datetime] = None


class MentorApprovalResponse(BaseModel):
    """Single approval record"""
    id: int
    document_id: int
    reviewer_id: int
    action: ApprovalAction
    reason: Optional[str] = None
    reviewed_at: datetime
    
    class Config:
        from_attributes = True


class MentorDocumentListResponse(BaseModel):
    """List of documents for a mentor"""
    documents: List[MentorDocumentResponse]
    total: int
    pending_count: int
    approved_count: int
    rejected_count: int


class MentorPendingVerificationResponse(BaseModel):
    """Pending mentor verification (for admin dashboard)"""
    mentor_id: int
    mentor_name: str
    email: str
    expertise: str
    documents_count: int
    documents: List[MentorDocumentResponse]
    submitted_at: datetime
    status: str  # "pending", "approved", "rejected"


class MentorPendingListResponse(BaseModel):
    """List of pending mentor verifications"""
    pending_mentors: List[MentorPendingVerificationResponse]
    total_pending: int
    total_approved: int
    total_rejected: int


class UploadSuccessResponse(BaseModel):
    """Response after successful document upload"""
    ok: bool = True
    document_id: int
    message: str = "Document uploaded successfully"
    status: DocumentStatus = DocumentStatus.PENDING


class ApprovalSuccessResponse(BaseModel):
    """Response after successful approval/rejection"""
    ok: bool = True
    message: str
    approval_id: int


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    details: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Unauthorized",
                "details": "Only admins can approve documents"
            }
        }
