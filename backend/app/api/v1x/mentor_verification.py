"""
Mentor Verification API endpoints
Handles document uploads, status checking, and admin approval/rejection
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import os
import shutil

from app.core.db import get_db
from app.core.security import get_current_user, get_current_admin
from app.models.user import User, UserRole
from app.modelsx.mentor import Mentor, MentorStatus
from app.modelsx.mentor_verification import MentorVerification, VerificationStatus, DocumentType
from app.schemas.mentor import (
    MentorVerificationResponse, MentorVerificationListResponse, 
    AdminVerificationResponse, AdminVerificationUpdateRequest
)
from app.services.email_service import email_service

router = APIRouter(prefix="/mentor-verification", tags=["mentor-verification"])

# File upload configuration
UPLOAD_DIR = "uploads/mentor-verifications"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============ Mentor Endpoints ============

@router.post("/upload", response_model=MentorVerificationResponse, status_code=status.HTTP_201_CREATED)
async def upload_verification_document(
    file: UploadFile = File(...),
    doc_type: str = Query("government_id", description="Document type: government_id, degree, certification, credential"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a verification document (ID, degree, certification, etc.)
    
    Allowed document types:
    - government_id: Government issued ID, passport, driver's license
    - degree: Bachelor's, Master's degree, etc.
    - certification: Professional certifications
    - credential: Other credentials
    
    Returns the verification record with status 'pending' awaiting admin review
    """
    
    # Get mentor profile
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You must have a mentor profile to upload verification documents"
        )
    
    # Validate document type
    valid_types = ["government_id", "degree", "certification", "credential"]
    if doc_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Must be one of: {valid_types}"
        )
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
        )
    
    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: PDF, JPEG, PNG, WebP, DOC, DOCX"
        )
    
    # Save file
    file_extension = os.path.splitext(file.filename)[1]
    saved_filename = f"mentor_{mentor.id}_{doc_type}_{datetime.utcnow().timestamp()}{file_extension}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    try:
        with open(saved_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )
    
    # Create verification record
    verification = MentorVerification(
        mentor_id=mentor.id,
        document_type=doc_type,
        document_url=saved_path,
        document_name=file.filename,
        file_size=len(content),
        mime_type=file.content_type,
        status=VerificationStatus.PENDING
    )
    
    db.add(verification)
    db.commit()
    db.refresh(verification)
    
    # Send notification to admins
    try:
        email_service.notify_admins_new_verification(
            mentor_id=mentor.id,
            mentor_name=current_user.email,
            document_type=doc_type,
            verification_id=verification.id
        )
    except Exception as e:
        print(f"Failed to send admin notification: {e}")
    
    return MentorVerificationResponse.from_orm(verification)


@router.get("/status", response_model=MentorVerificationListResponse)
def get_verification_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current mentor's verification status and documents
    Returns all uploaded documents and overall verification status
    """
    
    # Get mentor profile
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor profile not found"
        )
    
    # Get all verifications
    verifications = db.query(MentorVerification).filter(
        MentorVerification.mentor_id == mentor.id
    ).all()
    
    # Determine overall status
    if not verifications:
        overall_status = "no_documents"
    elif any(v.status == VerificationStatus.APPROVED for v in verifications):
        overall_status = "verified"
    elif any(v.status == VerificationStatus.PENDING for v in verifications):
        overall_status = "pending_review"
    else:
        overall_status = "rejected"
    
    return MentorVerificationListResponse(
        verifications=[MentorVerificationResponse.from_orm(v) for v in verifications],
        total=len(verifications),
        status=overall_status
    )


# ============ Admin Endpoints ============

@router.get("/admin/pending", response_model=List[AdminVerificationResponse])
def get_pending_verifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all pending mentor verifications (admin only)
    Used by admin to review and approve/reject verifications
    """
    
    pending = db.query(MentorVerification).filter(
        MentorVerification.status == VerificationStatus.PENDING
    ).order_by(MentorVerification.submitted_at.asc()).offset(offset).limit(limit).all()
    
    result = []
    for v in pending:
        mentor = db.query(Mentor).filter(Mentor.id == v.mentor_id).first()
        user = db.query(User).filter(User.id == mentor.user_id).first()
        
        result.append(AdminVerificationResponse(
            id=v.id,
            mentor_id=v.mentor_id,
            mentor_name=user.email if user else "Unknown",
            mentor_email=user.email if user else "Unknown",
            document_type=v.document_type,
            document_url=v.document_url,
            document_name=v.document_name,
            status=v.status,
            submitted_at=v.submitted_at,
            reviewed_at=v.reviewed_at,
            reviewer_notes=v.reviewer_notes
        ))
    
    return result


@router.post("/admin/{verification_id}/approve", response_model=AdminVerificationResponse)
def approve_verification(
    verification_id: int,
    notes: str = Query(None, description="Optional reviewer notes"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Approve a mentor verification document (admin only)
    Updates status to 'approved' and notifies mentor
    """
    
    verification = db.query(MentorVerification).filter(
        MentorVerification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification not found"
        )
    
    # Update verification
    verification.status = VerificationStatus.APPROVED
    verification.reviewed_at = datetime.utcnow()
    verification.reviewer_id = current_admin.id
    if notes:
        verification.reviewer_notes = notes
    
    db.commit()
    db.refresh(verification)
    
    # Get mentor and user for notification
    mentor = db.query(Mentor).filter(Mentor.id == verification.mentor_id).first()
    user = db.query(User).filter(User.id == mentor.user_id).first()
    
    # Send approval email
    try:
        email_service.notify_verification_approved(
            user_email=user.email,
            document_type=verification.document_type
        )
    except Exception as e:
        print(f"Failed to send approval email: {e}")
    
    return AdminVerificationResponse(
        id=verification.id,
        mentor_id=verification.mentor_id,
        mentor_name=user.email,
        mentor_email=user.email,
        document_type=verification.document_type,
        document_url=verification.document_url,
        document_name=verification.document_name,
        status=verification.status,
        submitted_at=verification.submitted_at,
        reviewed_at=verification.reviewed_at,
        reviewer_notes=verification.reviewer_notes
    )


@router.post("/admin/{verification_id}/reject", response_model=AdminVerificationResponse)
def reject_verification(
    verification_id: int,
    request: AdminVerificationUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Reject a mentor verification document (admin only)
    Updates status to 'rejected' with reason and notifies mentor
    """
    
    if request.status != "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use /approve endpoint for approval"
        )
    
    verification = db.query(MentorVerification).filter(
        MentorVerification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification not found"
        )
    
    # Update verification
    verification.status = VerificationStatus.REJECTED
    verification.reviewed_at = datetime.utcnow()
    verification.reviewer_id = current_admin.id
    verification.reviewer_notes = request.reviewer_notes or "Document rejected"
    
    db.commit()
    db.refresh(verification)
    
    # Get mentor and user for notification
    mentor = db.query(Mentor).filter(Mentor.id == verification.mentor_id).first()
    user = db.query(User).filter(User.id == mentor.user_id).first()
    
    # Send rejection email
    try:
        email_service.notify_verification_rejected(
            user_email=user.email,
            document_type=verification.document_type,
            reason=verification.reviewer_notes
        )
    except Exception as e:
        print(f"Failed to send rejection email: {e}")
    
    return AdminVerificationResponse(
        id=verification.id,
        mentor_id=verification.mentor_id,
        mentor_name=user.email,
        mentor_email=user.email,
        document_type=verification.document_type,
        document_url=verification.document_url,
        document_name=verification.document_name,
        status=verification.status,
        submitted_at=verification.submitted_at,
        reviewed_at=verification.reviewed_at,
        reviewer_notes=verification.reviewer_notes
    )

