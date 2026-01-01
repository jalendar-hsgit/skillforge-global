"""
Certificates API Router - Phase 3.4
Certificate generation and verification
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime
import uuid

from app.core.db import get_db
from app.models import User
from app.modelsx.learning_paths import Certificate, LearningPath, UserPathProgress
from app.schemas.learning_paths_schemas import (
    CertificateResponse, CertificateCreate,
    CertificateVerifyRequest, CertificateVerifyResponse
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/certificates", tags=["certificates"])


def generate_certificate_number():
    """Generate unique certificate number"""
    return f"SF-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"


def generate_verification_code():
    """Generate certificate verification code"""
    return uuid.uuid4().hex[:16].upper()


@router.post("", response_model=CertificateResponse, status_code=status.HTTP_201_CREATED)
def issue_certificate(
    cert_data: CertificateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Issue certificate for path completion (admin)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Verify user completed the path
    progress = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == cert_data.user_id,
        UserPathProgress.path_id == cert_data.path_id,
        UserPathProgress.is_completed == True
    ).first()
    
    if not progress:
        raise HTTPException(status_code=400, detail="User has not completed this path")
    
    # Check if already has certificate for this path
    existing = db.query(Certificate).filter(
        Certificate.user_id == cert_data.user_id,
        Certificate.path_id == cert_data.path_id,
        Certificate.status == "earned"
    ).first()
    
    if existing:
        return existing
    
    path = db.query(LearningPath).filter(LearningPath.id == cert_data.path_id).first()
    
    certificate = Certificate(
        user_id=cert_data.user_id,
        path_id=cert_data.path_id,
        certificate_number=generate_certificate_number(),
        title=cert_data.title or f"{path.title} Certificate",
        description=cert_data.description,
        verification_code=generate_verification_code(),
        earned_at=progress.completed_at or datetime.utcnow()
    )
    
    db.add(certificate)
    db.commit()
    db.refresh(certificate)
    return certificate


@router.get("/{user_id}", response_model=List[CertificateResponse])
def get_user_certificates(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's certificates"""
    # Public access - only show earned certificates
    certificates = db.query(Certificate).filter(
        Certificate.user_id == user_id,
        Certificate.status == "earned"
    ).order_by(
        desc(Certificate.earned_at)
    ).all()
    
    return certificates


@router.get("/my-certificates", response_model=List[CertificateResponse])
def get_my_certificates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's certificates"""
    certificates = db.query(Certificate).filter(
        Certificate.user_id == current_user.id,
        Certificate.status == "earned"
    ).order_by(
        desc(Certificate.earned_at)
    ).all()
    
    return certificates


@router.get("/verify/{certificate_number}", response_model=CertificateVerifyResponse)
def verify_certificate(
    certificate_number: str,
    db: Session = Depends(get_db)
):
    """Verify certificate authenticity (public)"""
    certificate = db.query(Certificate).filter(
        Certificate.certificate_number == certificate_number
    ).first()
    
    if not certificate or certificate.status != "earned":
        return {
            "is_valid": False,
            "user_name": None,
            "path_title": None,
            "earned_at": None,
            "expires_at": None
        }
    
    user = db.query(User).filter(User.id == certificate.user_id).first()
    path = db.query(LearningPath).filter(LearningPath.id == certificate.path_id).first()
    
    # Check if expired
    is_valid = True
    if certificate.expires_at and datetime.utcnow() > certificate.expires_at:
        is_valid = False
    
    return {
        "is_valid": is_valid,
        "user_name": user.name if user else None,
        "path_title": path.title if path else None,
        "earned_at": certificate.earned_at,
        "expires_at": certificate.expires_at
    }


@router.post("/verify", response_model=CertificateVerifyResponse)
def verify_certificate_by_code(
    request: CertificateVerifyRequest,
    db: Session = Depends(get_db)
):
    """Verify certificate by number (public endpoint)"""
    certificate = db.query(Certificate).filter(
        Certificate.certificate_number == request.certificate_number
    ).first()
    
    if not certificate or certificate.status != "earned":
        return {
            "is_valid": False,
            "user_name": None,
            "path_title": None,
            "earned_at": None,
            "expires_at": None
        }
    
    user = db.query(User).filter(User.id == certificate.user_id).first()
    path = db.query(LearningPath).filter(LearningPath.id == certificate.path_id).first()
    
    is_valid = True
    if certificate.expires_at and datetime.utcnow() > certificate.expires_at:
        is_valid = False
    
    return {
        "is_valid": is_valid,
        "user_name": user.name if user else None,
        "path_title": path.title if path else None,
        "earned_at": certificate.earned_at,
        "expires_at": certificate.expires_at
    }


@router.patch("/{certificate_id}/revoke", response_model=CertificateResponse)
def revoke_certificate(
    certificate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke certificate (admin only)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    certificate.status = "revoked"
    db.commit()
    db.refresh(certificate)
    return certificate


@router.delete("/{certificate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certificate(
    certificate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete certificate (admin only)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    db.delete(certificate)
    db.commit()


@router.get("/count/user/{user_id}")
def get_user_certificate_count(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get certificate count for user"""
    count = db.query(Certificate).filter(
        Certificate.user_id == user_id,
        Certificate.status == "earned"
    ).count()
    
    return {"user_id": user_id, "certificate_count": count}
