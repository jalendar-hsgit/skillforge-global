"""
Mentor Document Upload & Verification API Routes
Handles document uploads, approvals, and status tracking
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.modelsx.mentor_documents import MentorDocument, MentorApproval, DocumentStatus, DocumentType, ApprovalAction
from app.modelsx.mentor import Mentor
from app.schemas.mentor_documents import (
    DocumentUploadRequest,
    MentorDocumentResponse,
    MentorDocumentDetailResponse,
    MentorDocumentListResponse,
    MentorPendingListResponse,
    MentorPendingVerificationResponse,
    DocumentApproveRequest,
    DocumentRejectRequest,
    UploadSuccessResponse,
    ApprovalSuccessResponse,
    ErrorResponse
)

router = APIRouter(prefix="/mentor-documents", tags=["mentor-documents"])

# File upload configuration
UPLOAD_DIR = "backend/app/data/mentor_documents"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx"
}


def ensure_upload_dir():
    """Ensure upload directory exists"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# MENTOR ENDPOINTS
# ============================================================

@router.post("/upload", response_model=UploadSuccessResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a verification document as a mentor
    
    Allowed document types:
    - certification, id_verification, degree, experience, license, portfolio, other
    
    Allowed file types:
    - PDF, JPG, PNG, DOC, DOCX
    
    Max file size: 10MB
    """
    # Check user is a mentor
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=403, detail="Only mentors can upload verification documents")
    
    # Validate document type
    try:
        doc_type = DocumentType(document_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {document_type}")
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a filename")
    
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_MIME_TYPES.keys())}"
        )
    
    # Read and validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit")
    
    # Save file
    ensure_upload_dir()
    file_ext = ALLOWED_MIME_TYPES[file.content_type]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{mentor.id}_{doc_type.value}_{timestamp}{file_ext}"
    filepath = os.path.join(UPLOAD_DIR, safe_filename)
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Create database record
    document = MentorDocument(
        mentor_id=mentor.id,
        document_type=doc_type,
        filename=file.filename,
        filepath=filepath,
        file_size=len(content),
        mime_type=file.content_type,
        status=DocumentStatus.PENDING
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return UploadSuccessResponse(
        document_id=document.id,
        message=f"Document uploaded successfully and is awaiting review"
    )


@router.get("/my-documents", response_model=MentorDocumentListResponse)
async def get_my_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents uploaded by the current mentor"""
    # Check user is a mentor
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=403, detail="Only mentors can view their documents")
    
    # Get documents
    documents = db.query(MentorDocument).filter(
        MentorDocument.mentor_id == mentor.id
    ).order_by(MentorDocument.uploaded_at.desc()).all()
    
    # Count by status
    pending = sum(1 for d in documents if d.status == DocumentStatus.PENDING)
    approved = sum(1 for d in documents if d.status == DocumentStatus.APPROVED)
    rejected = sum(1 for d in documents if d.status == DocumentStatus.REJECTED)
    
    return MentorDocumentListResponse(
        documents=[MentorDocumentResponse.from_orm(d) for d in documents],
        total=len(documents),
        pending_count=pending,
        approved_count=approved,
        rejected_count=rejected
    )


@router.delete("/my-documents/{document_id}")
async def delete_my_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document (mentor can only delete their own pending documents)"""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=403, detail="Only mentors can delete documents")
    
    document = db.query(MentorDocument).filter(MentorDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.mentor_id != mentor.id:
        raise HTTPException(status_code=403, detail="Cannot delete another mentor's documents")
    
    if document.status != DocumentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Can only delete pending documents")
    
    # Delete file
    if os.path.exists(document.filepath):
        os.remove(document.filepath)
    
    db.delete(document)
    db.commit()
    
    return {"ok": True, "message": "Document deleted successfully"}


# ============================================================
# ADMIN ENDPOINTS
# ============================================================

@router.get("/pending", response_model=MentorPendingListResponse)
async def get_pending_verifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all pending mentor verifications (admin only)"""
    # Check user is admin
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Only admins can view pending verifications")
    
    # Get mentors with pending documents
    mentors = db.query(Mentor).all()
    pending_mentors = []
    
    for mentor in mentors:
        documents = db.query(MentorDocument).filter(
            MentorDocument.mentor_id == mentor.id,
            MentorDocument.status == DocumentStatus.PENDING
        ).all()
        
        if documents:
            mentor_user = db.query(User).filter(User.id == mentor.user_id).first()
            pending_mentors.append(MentorPendingVerificationResponse(
                mentor_id=mentor.id,
                mentor_name=mentor_user.name or "Unknown",
                email=mentor_user.email,
                expertise=mentor.expertise,
                documents_count=len(documents),
                documents=[MentorDocumentResponse.from_orm(d) for d in documents],
                submitted_at=min(d.uploaded_at for d in documents),
                status="pending"
            ))
    
    # Count by status
    all_documents = db.query(MentorDocument).all()
    approved = sum(1 for d in all_documents if d.status == DocumentStatus.APPROVED)
    rejected = sum(1 for d in all_documents if d.status == DocumentStatus.REJECTED)
    
    return MentorPendingListResponse(
        pending_mentors=pending_mentors,
        total_pending=len(pending_mentors),
        total_approved=approved,
        total_rejected=rejected
    )


@router.get("/details/{document_id}", response_model=MentorDocumentDetailResponse)
async def get_document_details(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed document info (mentor can view own, admin can view any)"""
    document = db.query(MentorDocument).filter(MentorDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    is_own_doc = mentor and mentor.id == document.mentor_id
    is_admin = current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]
    
    if not (is_own_doc or is_admin):
        raise HTTPException(status_code=403, detail="Cannot view this document")
    
    return MentorDocumentDetailResponse.from_orm(document)


@router.patch("/{document_id}/approve", response_model=ApprovalSuccessResponse)
async def approve_document(
    document_id: int,
    request: DocumentApproveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a document (admin only)"""
    # Check admin
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Only admins can approve documents")
    
    document = db.query(MentorDocument).filter(MentorDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update document
    document.status = DocumentStatus.APPROVED
    document.reviewed_at = datetime.utcnow()
    
    # Create approval record
    approval = MentorApproval(
        document_id=document.id,
        reviewer_id=current_user.id,
        action=ApprovalAction.APPROVED,
        reason=request.reason
    )
    
    db.add(approval)
    db.commit()
    db.refresh(approval)
    
    return ApprovalSuccessResponse(
        message=f"Document {document_id} approved successfully",
        approval_id=approval.id
    )


@router.patch("/{document_id}/reject", response_model=ApprovalSuccessResponse)
async def reject_document(
    document_id: int,
    request: DocumentRejectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a document with reason (admin only)"""
    # Check admin
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Only admins can reject documents")
    
    document = db.query(MentorDocument).filter(MentorDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update document
    document.status = DocumentStatus.REJECTED
    document.rejection_reason = request.reason
    document.reviewed_at = datetime.utcnow()
    
    # Create approval record
    approval = MentorApproval(
        document_id=document.id,
        reviewer_id=current_user.id,
        action=ApprovalAction.REJECTED,
        reason=request.reason
    )
    
    db.add(approval)
    db.commit()
    db.refresh(approval)
    
    return ApprovalSuccessResponse(
        message=f"Document {document_id} rejected. Reason: {request.reason}",
        approval_id=approval.id
    )
