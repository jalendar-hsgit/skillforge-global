"""
Admin Payout Approval and Management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import asyncio

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.modelsx.payment_method import PayoutRequest as PayoutRequestModel, PaymentMethod
from app.modelsx.mentor import Mentor
from app.modelsx.payout import MentorEarning, MentorPayout, PayoutStatus
from app.services.email_service import email_service

router = APIRouter(prefix="/admin/payouts", tags=["admin-payouts"])


# Schemas
class PaymentMethodDetailResponse(BaseModel):
    id: int
    mentor_id: int
    mentor_name: str
    account_holder_name: str
    bank_name: str
    account_last_four: str
    status: str
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PayoutRequestDetailResponse(BaseModel):
    id: int
    mentor_id: int
    mentor_name: str
    mentor_email: str
    amount: float
    status: str
    payment_method_id: Optional[int]
    payment_method_info: Optional[str]
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime]
    completed_at: Optional[datetime]
    rejection_reason: Optional[str]
    admin_notes: Optional[str]

    class Config:
        from_attributes = True


class ApprovePayoutRequest(BaseModel):
    admin_notes: Optional[str] = None


class RejectPayoutRequest(BaseModel):
    rejection_reason: str
    admin_notes: Optional[str] = None


class VerifyPaymentMethodRequest(BaseModel):
    status: str  # VERIFIED, REJECTED


# Helper Functions
def require_admin(user: User = Depends(get_current_user)) -> User:
    """Verify user is admin"""
    if user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


# Endpoints - Define specific routes BEFORE generic /{payout_id}

@router.get("/stats", response_model=dict)
def get_payout_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for payouts.
    """
    total_pending = db.query(func.count(PayoutRequestModel.id)).filter(
        PayoutRequestModel.status == "PENDING"
    ).scalar() or 0

    total_processing = db.query(func.count(PayoutRequestModel.id)).filter(
        PayoutRequestModel.status == "PROCESSING"
    ).scalar() or 0

    pending_amount_sum = db.query(func.sum(PayoutRequestModel.amount)).filter(
        PayoutRequestModel.status.in_(["PENDING", "PROCESSING"])
    ).scalar()
    pending_amount = (pending_amount_sum / 100) if pending_amount_sum else 0

    total_approved_sum = db.query(func.sum(PayoutRequestModel.amount)).filter(
        PayoutRequestModel.status == "APPROVED"
    ).scalar()
    total_approved = (total_approved_sum / 100) if total_approved_sum else 0

    total_completed_sum = db.query(func.sum(PayoutRequestModel.amount)).filter(
        PayoutRequestModel.status == "COMPLETED"
    ).scalar()
    total_completed = (total_completed_sum / 100) if total_completed_sum else 0

    unverified_methods = db.query(func.count(PaymentMethod.id)).filter(
        PaymentMethod.status == "PENDING"
    ).scalar() or 0

    return {
        "pending_requests": total_pending,
        "processing_requests": total_processing,
        "pending_amount": pending_amount,
        "approved_amount": total_approved,
        "completed_amount": total_completed,
        "unverified_payment_methods": unverified_methods
    }


@router.get("/pending", response_model=List[PayoutRequestDetailResponse])
def get_pending_payout_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all pending payout requests.
    Admin only endpoint.
    """
    payouts = db.query(PayoutRequestModel).filter(
        PayoutRequestModel.status.in_(["PENDING", "PROCESSING"])
    ).order_by(PayoutRequestModel.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for payout in payouts:
        mentor = db.query(Mentor).filter(Mentor.id == payout.mentor_id).first()
        mentor_user = db.query(User).filter(User.id == mentor.user_id).first() if mentor else None

        payment_method_info = None
        if payout.payment_method_id:
            pm = db.query(PaymentMethod).filter(
                PaymentMethod.id == payout.payment_method_id
            ).first()
            if pm:
                payment_method_info = f"{pm.bank_name} ••••{pm.account_number_encrypted[-4:]}"

        result.append(PayoutRequestDetailResponse(
            id=payout.id,
            mentor_id=payout.mentor_id,
            mentor_name=mentor_user.name if mentor_user else "Unknown",
            mentor_email=mentor_user.email if mentor_user else "Unknown",
            amount=payout.amount / 100,  # Convert from cents
            status=payout.status,
            payment_method_id=payout.payment_method_id,
            payment_method_info=payment_method_info,
            created_at=payout.created_at,
            updated_at=payout.updated_at,
            approved_at=payout.approved_at,
            completed_at=payout.completed_at,
            rejection_reason=payout.rejection_reason,
            admin_notes=payout.admin_notes
        ))

    return result


@router.get("/payment-methods/unverified", response_model=List[PaymentMethodDetailResponse])
def get_unverified_payment_methods(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all unverified payment methods awaiting admin review.
    """
    payment_methods = db.query(PaymentMethod).filter(
        PaymentMethod.status == "PENDING"
    ).order_by(PaymentMethod.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for pm in payment_methods:
        mentor = db.query(Mentor).filter(Mentor.id == pm.mentor_id).first()
        mentor_user = db.query(User).filter(User.id == mentor.user_id).first() if mentor else None

        result.append(PaymentMethodDetailResponse(
            id=pm.id,
            mentor_id=pm.mentor_id,
            mentor_name=mentor_user.name if mentor_user else "Unknown",
            account_holder_name=pm.account_holder_name,
            bank_name=pm.bank_name,
            account_last_four="****",
            status=pm.status,
            is_default=pm.is_default,
            created_at=pm.created_at
        ))

    return result


@router.get("/all", response_model=List[PayoutRequestDetailResponse])
def get_all_payout_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all payout requests with optional status filter.
    Admin only endpoint.
    """
    query = db.query(PayoutRequestModel)

    if status_filter:
        query = query.filter(PayoutRequestModel.status == status_filter)

    payouts = query.order_by(
        PayoutRequestModel.created_at.desc()
    ).offset(skip).limit(limit).all()

    result = []
    for payout in payouts:
        mentor = db.query(Mentor).filter(Mentor.id == payout.mentor_id).first()
        mentor_user = db.query(User).filter(User.id == mentor.user_id).first() if mentor else None

        payment_method_info = None
        if payout.payment_method_id:
            pm = db.query(PaymentMethod).filter(
                PaymentMethod.id == payout.payment_method_id
            ).first()
            if pm:
                payment_method_info = f"{pm.bank_name} ••••{pm.account_number_encrypted[-4:]}"

        result.append(PayoutRequestDetailResponse(
            id=payout.id,
            mentor_id=payout.mentor_id,
            mentor_name=mentor_user.name if mentor_user else "Unknown",
            mentor_email=mentor_user.email if mentor_user else "Unknown",
            amount=payout.amount / 100,
            status=payout.status,
            payment_method_id=payout.payment_method_id,
            payment_method_info=payment_method_info,
            created_at=payout.created_at,
            updated_at=payout.updated_at,
            approved_at=payout.approved_at,
            completed_at=payout.completed_at,
            rejection_reason=payout.rejection_reason,
            admin_notes=payout.admin_notes
        ))

    return result


@router.get("/{payout_id}", response_model=PayoutRequestDetailResponse)
def get_payout_request_detail(
    payout_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed info about a specific payout request.
    """
    payout = db.query(PayoutRequestModel).filter(
        PayoutRequestModel.id == payout_id
    ).first()

    if not payout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payout request not found"
        )

    mentor = db.query(Mentor).filter(Mentor.id == payout.mentor_id).first()
    mentor_user = db.query(User).filter(User.id == mentor.user_id).first() if mentor else None

    payment_method_info = None
    if payout.payment_method_id:
        pm = db.query(PaymentMethod).filter(
            PaymentMethod.id == payout.payment_method_id
        ).first()
        if pm:
            payment_method_info = f"{pm.bank_name} ••••{pm.account_number_encrypted[-4:]}"

    return PayoutRequestDetailResponse(
        id=payout.id,
        mentor_id=payout.mentor_id,
        mentor_name=mentor_user.name if mentor_user else "Unknown",
        mentor_email=mentor_user.email if mentor_user else "Unknown",
        amount=payout.amount / 100,
        status=payout.status,
        payment_method_id=payout.payment_method_id,
        payment_method_info=payment_method_info,
        created_at=payout.created_at,
        updated_at=payout.updated_at,
        approved_at=payout.approved_at,
        completed_at=payout.completed_at,
        rejection_reason=payout.rejection_reason,
        admin_notes=payout.admin_notes
    )


@router.post("/{payout_id}/approve", response_model=PayoutRequestDetailResponse)
def approve_payout_request(
    payout_id: int,
    request: ApprovePayoutRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Approve a pending payout request.
    Admin only endpoint.
    """
    payout = db.query(PayoutRequestModel).filter(
        PayoutRequestModel.id == payout_id
    ).first()

    if not payout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payout request not found"
        )

    if payout.status not in ["PENDING", "PROCESSING"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve payout with status: {payout.status}"
        )

    # Verify payment method is verified
    if payout.payment_method_id:
        pm = db.query(PaymentMethod).filter(
            PaymentMethod.id == payout.payment_method_id
        ).first()

        if not pm or pm.status != "VERIFIED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment method must be verified before approval"
            )

    # Update payout
    payout.status = "APPROVED"
    payout.approved_at = datetime.utcnow()
    payout.admin_notes = request.admin_notes

    db.commit()
    db.refresh(payout)

    mentor = db.query(Mentor).filter(Mentor.id == payout.mentor_id).first()
    mentor_user = db.query(User).filter(User.id == mentor.user_id).first() if mentor else None

    # Send approval notification email
    try:
        if mentor_user:
            # Run email send asynchronously (don't wait for it)
            asyncio.create_task(
                email_service.send_seller_payout_notification(
                    to_email=mentor_user.email,
                    seller_name=mentor_user.name or "Mentor",
                    amount=payout.amount / 100,
                    payout_date=datetime.utcnow(),
                    payout_method=payout.payment_method or "bank_transfer",
                    payout_id=payout.id
                )
            )
    except Exception as e:
        print(f"Failed to send payout approval email: {e}")
        # Continue regardless - email failure doesn't block approval

    payment_method_info = None
    if payout.payment_method_id:
        pm = db.query(PaymentMethod).filter(
            PaymentMethod.id == payout.payment_method_id
        ).first()
        if pm:
            payment_method_info = f"{pm.bank_name} ••••{pm.account_number_encrypted[-4:]}"

    return PayoutRequestDetailResponse(
        id=payout.id,
        mentor_id=payout.mentor_id,
        mentor_name=mentor_user.name if mentor_user else "Unknown",
        mentor_email=mentor_user.email if mentor_user else "Unknown",
        amount=payout.amount / 100,
        status=payout.status,
        payment_method_id=payout.payment_method_id,
        payment_method_info=payment_method_info,
        created_at=payout.created_at,
        updated_at=payout.updated_at,
        approved_at=payout.approved_at,
        completed_at=payout.completed_at,
        rejection_reason=payout.rejection_reason,
        admin_notes=payout.admin_notes
    )


@router.post("/{payout_id}/reject", response_model=PayoutRequestDetailResponse)
def reject_payout_request(
    payout_id: int,
    request: RejectPayoutRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Reject a pending payout request.
    Admin only endpoint.
    """
    payout = db.query(PayoutRequestModel).filter(
        PayoutRequestModel.id == payout_id
    ).first()

    if not payout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payout request not found"
        )

    if payout.status not in ["PENDING", "PROCESSING"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject payout with status: {payout.status}"
        )

    # Update payout
    payout.status = "REJECTED"
    payout.rejection_reason = request.rejection_reason
    payout.admin_notes = request.admin_notes
    payout.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(payout)

    mentor = db.query(Mentor).filter(Mentor.id == payout.mentor_id).first()
    mentor_user = db.query(User).filter(User.id == mentor.user_id).first() if mentor else None

    payment_method_info = None
    if payout.payment_method_id:
        pm = db.query(PaymentMethod).filter(
            PaymentMethod.id == payout.payment_method_id
        ).first()
        if pm:
            payment_method_info = f"{pm.bank_name} ••••{pm.account_number_encrypted[-4:]}"

    return PayoutRequestDetailResponse(
        id=payout.id,
        mentor_id=payout.mentor_id,
        mentor_name=mentor_user.name if mentor_user else "Unknown",
        mentor_email=mentor_user.email if mentor_user else "Unknown",
        amount=payout.amount / 100,
        status=payout.status,
        payment_method_id=payout.payment_method_id,
        payment_method_info=payment_method_info,
        created_at=payout.created_at,
        updated_at=payout.updated_at,
        approved_at=payout.approved_at,
        completed_at=payout.completed_at,
        rejection_reason=payout.rejection_reason,
        admin_notes=payout.admin_notes
    )


@router.post("/payment-methods/{payment_method_id}/verify")
def verify_payment_method(
    payment_method_id: int,
    request: VerifyPaymentMethodRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Verify or reject a payment method.
    Admin only endpoint.
    """
    payment_method = db.query(PaymentMethod).filter(
        PaymentMethod.id == payment_method_id
    ).first()

    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )

    if request.status not in ["VERIFIED", "REJECTED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be VERIFIED or REJECTED"
        )

    payment_method.status = request.status
    if request.status == "VERIFIED":
        payment_method.verified_at = datetime.utcnow()

    db.commit()
    db.refresh(payment_method)

    return {
        "id": payment_method.id,
        "status": payment_method.status,
        "verified_at": payment_method.verified_at,
        "updated_at": payment_method.updated_at
    }

# ============================================================
# MENTOR PAYOUT APPROVAL (for MentorPayout model)
# ============================================================

class MentorPayoutDetailResponse(BaseModel):
    """Response model for mentor payout details"""
    id: int
    mentor_id: int
    mentor_name: str
    mentor_email: str
    amount: float
    net_amount: float
    platform_fee: float
    method: str
    status: str
    stripe_transfer_id: Optional[str]
    requested_at: datetime
    processed_at: Optional[datetime]
    completed_at: Optional[datetime]
    failure_reason: Optional[str]
    notes: Optional[str]
    
    class Config:
        from_attributes = True


@router.get("/mentor-payouts/pending", response_model=List[MentorPayoutDetailResponse])
def get_pending_mentor_payouts(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get all pending mentor payout requests.
    Admin only endpoint.
    """
    payouts = db.query(MentorPayout).filter(
        MentorPayout.status == PayoutStatus.PENDING
    ).order_by(
        MentorPayout.requested_at.desc()
    ).offset(skip).limit(limit).all()
    
    result = []
    for payout in payouts:
        mentor = db.query(Mentor).filter(Mentor.id == payout.mentor_id).first()
        mentor_user = db.query(User).filter(User.id == mentor.user_id).first() if mentor else None
        
        result.append(MentorPayoutDetailResponse(
            id=payout.id,
            mentor_id=payout.mentor_id,
            mentor_name=mentor_user.name if mentor_user else "Unknown",
            mentor_email=mentor_user.email if mentor_user else "Unknown",
            amount=payout.amount,
            net_amount=payout.net_amount,
            platform_fee=payout.platform_fee,
            method=payout.method.value if hasattr(payout.method, 'value') else str(payout.method),
            status=payout.status.value if hasattr(payout.status, 'value') else str(payout.status),
            stripe_transfer_id=payout.stripe_transfer_id,
            requested_at=payout.requested_at,
            processed_at=payout.processed_at,
            completed_at=payout.completed_at,
            failure_reason=payout.failure_reason,
            notes=payout.notes
        ))
    
    return result


@router.post("/mentor-payouts/{payout_id}/approve", response_model=MentorPayoutDetailResponse)
def approve_mentor_payout(
    payout_id: int,
    request: ApprovePayoutRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Approve and process a mentor payout request.
    Initiates payment transfer based on payout method.
    Admin only endpoint.
    """
    payout = db.query(MentorPayout).filter(
        MentorPayout.id == payout_id
    ).first()
    
    if not payout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payout not found"
        )
    
    if payout.status != PayoutStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payout already {payout.status.value if hasattr(payout.status, 'value') else payout.status}"
        )
    
    try:
        # Update status to processing
        payout.status = PayoutStatus.PROCESSING
        payout.processed_at = datetime.utcnow()
        if request.admin_notes:
            payout.notes = request.admin_notes
        
        # Mark related earnings as paid out
        earnings = db.query(MentorEarning).filter(
            MentorEarning.payout_id == payout.id
        ).all()
        
        for earning in earnings:
            earning.is_paid_out = True
            earning.paid_out_at = datetime.utcnow()
        
        db.commit()
        db.refresh(payout)
        
        # Send approval email to mentor
        mentor = db.query(Mentor).filter(Mentor.id == payout.mentor_id).first()
        mentor_user = db.query(User).filter(User.id == mentor.user_id).first() if mentor else None
        
        if mentor_user and mentor_user.email:
            try:
                from app.services.email_service import email_service
                email_service.send_payout_approved(
                    to_email=mentor_user.email,
                    payout_id=payout.id,
                    amount=payout.net_amount,
                    method=payout.method.value if hasattr(payout.method, 'value') else str(payout.method)
                )
            except Exception as e:
                print(f"Failed to send approval email: {e}")
        
        return MentorPayoutDetailResponse(
            id=payout.id,
            mentor_id=payout.mentor_id,
            mentor_name=mentor_user.name if mentor_user else "Unknown",
            mentor_email=mentor_user.email if mentor_user else "Unknown",
            amount=payout.amount,
            net_amount=payout.net_amount,
            platform_fee=payout.platform_fee,
            method=payout.method.value if hasattr(payout.method, 'value') else str(payout.method),
            status=payout.status.value if hasattr(payout.status, 'value') else str(payout.status),
            stripe_transfer_id=payout.stripe_transfer_id,
            requested_at=payout.requested_at,
            processed_at=payout.processed_at,
            completed_at=payout.completed_at,
            failure_reason=payout.failure_reason,
            notes=payout.notes
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mentor-payouts/{payout_id}/reject", response_model=MentorPayoutDetailResponse)
def reject_mentor_payout(
    payout_id: int,
    request: RejectPayoutRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Reject a mentor payout request.
    Funds return to mentor's available balance.
    Admin only endpoint.
    """
    payout = db.query(MentorPayout).filter(
        MentorPayout.id == payout_id
    ).first()
    
    if not payout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payout not found"
        )
    
    if payout.status != PayoutStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject {payout.status.value if hasattr(payout.status, 'value') else payout.status} payout"
        )
    
    try:
        # Update payout status
        payout.status = PayoutStatus.FAILED
        payout.failure_reason = request.rejection_reason
        payout.processed_at = datetime.utcnow()
        if request.admin_notes:
            payout.notes = request.admin_notes
        
        # Reset earnings as not paid out
        earnings = db.query(MentorEarning).filter(
            MentorEarning.payout_id == payout.id
        ).all()
        
        for earning in earnings:
            earning.is_paid_out = False
            earning.payout_id = None
        
        db.commit()
        db.refresh(payout)
        
        # Send rejection email
        mentor = db.query(Mentor).filter(Mentor.id == payout.mentor_id).first()
        mentor_user = db.query(User).filter(User.id == mentor.user_id).first() if mentor else None
        
        if mentor_user and mentor_user.email:
            try:
                from app.services.email_service import email_service
                email_service.send_payout_rejected(
                    to_email=mentor_user.email,
                    payout_id=payout.id,
                    reason=request.rejection_reason
                )
            except Exception as e:
                print(f"Failed to send rejection email: {e}")
        
        return MentorPayoutDetailResponse(
            id=payout.id,
            mentor_id=payout.mentor_id,
            mentor_name=mentor_user.name if mentor_user else "Unknown",
            mentor_email=mentor_user.email if mentor_user else "Unknown",
            amount=payout.amount,
            net_amount=payout.net_amount,
            platform_fee=payout.platform_fee,
            method=payout.method.value if hasattr(payout.method, 'value') else str(payout.method),
            status=payout.status.value if hasattr(payout.status, 'value') else str(payout.status),
            stripe_transfer_id=payout.stripe_transfer_id,
            requested_at=payout.requested_at,
            processed_at=payout.processed_at,
            completed_at=payout.completed_at,
            failure_reason=payout.failure_reason,
            notes=payout.notes
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mentor-payouts/stats", response_model=dict)
def get_mentor_payout_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get mentor payout statistics.
    Admin only endpoint.
    """
    pending_count = db.query(func.count(MentorPayout.id)).filter(
        MentorPayout.status == PayoutStatus.PENDING
    ).scalar() or 0
    
    processing_count = db.query(func.count(MentorPayout.id)).filter(
        MentorPayout.status == PayoutStatus.PROCESSING
    ).scalar() or 0
    
    completed_count = db.query(func.count(MentorPayout.id)).filter(
        MentorPayout.status == PayoutStatus.COMPLETED
    ).scalar() or 0
    
    pending_amount = db.query(func.sum(MentorPayout.net_amount)).filter(
        MentorPayout.status == PayoutStatus.PENDING
    ).scalar() or 0
    
    completed_amount = db.query(func.sum(MentorPayout.net_amount)).filter(
        MentorPayout.status == PayoutStatus.COMPLETED
    ).scalar() or 0
    
    return {
        "pending_requests": pending_count,
        "processing_requests": processing_count,
        "completed_requests": completed_count,
        "total_pending_amount": float(pending_amount),
        "total_completed_amount": float(completed_amount)
    }