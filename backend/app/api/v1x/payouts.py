"""
Mentor payout and earnings tracking endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.mentor import Mentor, MentorSession, SessionStatus
from app.modelsx.payout import MentorPayout, MentorEarning, PayoutStatus, PayoutMethod
from app.modelsx.payment_method import PaymentMethod, PaymentMethodStatus, PaymentMethodType, PayoutRequest as PayoutRequestModel
from pydantic import BaseModel, Field


router = APIRouter(prefix="/mentors/payouts", tags=["mentor-payouts"])


# Schemas
class EarningsSummary(BaseModel):
    total_earnings: float
    available_balance: float  # Not yet paid out
    pending_payouts: float
    completed_payouts: float
    total_sessions: int
    completed_sessions: int
    average_session_price: float
    platform_fee_percentage: float = 20.0  # Default 20% fee


class EarningDetail(BaseModel):
    id: int
    session_id: int
    student_name: str
    topic: str
    gross_amount: float
    platform_fee: float
    net_amount: float
    earned_at: datetime
    is_paid_out: bool
    payout_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class PayoutRequest(BaseModel):
    amount: float = Field(gt=0, description="Amount to request (must be > 0)")
    method: PayoutMethod = PayoutMethod.STRIPE
    notes: Optional[str] = None


class PayoutDetail(BaseModel):
    id: int
    amount: float
    platform_fee: float
    net_amount: float
    method: PayoutMethod
    status: PayoutStatus
    requested_at: datetime
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    earnings_count: int = 0  # Number of earnings in this payout
    
    class Config:
        from_attributes = True


class SessionEarningDetail(BaseModel):
    session_id: int
    student_name: str
    topic: str
    scheduled_at: datetime
    duration_minutes: int
    price: float
    payment_status: str
    status: str
    
    class Config:
        from_attributes = True


# ========== NEW SCHEMAS FOR PAYMENT METHODS ==========

class PaymentMethodCreate(BaseModel):
    """Create payment method"""
    payment_type: PaymentMethodType = PaymentMethodType.BANK_ACCOUNT
    account_holder_name: str = Field(min_length=2, max_length=255)
    bank_name: str = Field(min_length=2, max_length=255)
    account_number: str = Field(min_length=8, max_length=17)
    routing_number: str = Field(min_length=9, max_length=9)
    is_default: bool = False


class PaymentMethodUpdate(BaseModel):
    """Update payment method"""
    account_holder_name: Optional[str] = None
    bank_name: Optional[str] = None
    is_default: Optional[bool] = None


class PaymentMethodResponse(BaseModel):
    """Payment method response (no sensitive data)"""
    id: int
    payment_type: PaymentMethodType
    account_holder_name: str
    bank_name: str
    # Masked account number (last 4 digits only)
    account_last_four: str
    status: PaymentMethodStatus
    is_default: bool
    verified_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PayoutRequestCreate(BaseModel):
    """Create payout request"""
    amount: float = Field(gt=0, le=100000, description="Amount in USD")
    payment_method_id: Optional[int] = None
    notes: Optional[str] = None


class PayoutRequestResponse(BaseModel):
    """Payout request response"""
    id: int
    amount: float
    status: str
    payment_method_id: Optional[int]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Helper Functions
def get_mentor_or_404(user: User, db: Session) -> Mentor:
    """Get mentor profile or raise 404"""
    mentor = db.query(Mentor).filter(Mentor.user_id == user.id).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor profile not found"
        )
    return mentor


def calculate_platform_fee(amount: float, fee_percentage: float = 20.0) -> float:
    """Calculate platform fee"""
    return round(amount * (fee_percentage / 100), 2)


# Endpoints

@router.get("/summary", response_model=EarningsSummary)
def get_earnings_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get earnings summary for the mentor.
    Shows total earnings, available balance, and session statistics.
    """
    mentor = get_mentor_or_404(current_user, db)
    
    # Total earnings from all completed sessions
    total_earnings_result = db.query(
        func.sum(MentorEarning.net_amount)
    ).filter(
        MentorEarning.mentor_id == mentor.id
    ).scalar() or 0.0
    
    # Available balance (not yet paid out)
    available_balance = db.query(
        func.sum(MentorEarning.net_amount)
    ).filter(
        and_(
            MentorEarning.mentor_id == mentor.id,
            MentorEarning.is_paid_out == False
        )
    ).scalar() or 0.0
    
    # Pending payouts
    pending_payouts = db.query(
        func.sum(MentorPayout.net_amount)
    ).filter(
        and_(
            MentorPayout.mentor_id == mentor.id,
            MentorPayout.status.in_([PayoutStatus.PENDING, PayoutStatus.PROCESSING])
        )
    ).scalar() or 0.0
    
    # Completed payouts
    completed_payouts = db.query(
        func.sum(MentorPayout.net_amount)
    ).filter(
        and_(
            MentorPayout.mentor_id == mentor.id,
            MentorPayout.status == PayoutStatus.COMPLETED
        )
    ).scalar() or 0.0
    
    # Session counts
    total_sessions = db.query(func.count(MentorSession.id)).filter(
        MentorSession.mentor_id == mentor.id
    ).scalar() or 0
    
    completed_sessions = db.query(func.count(MentorSession.id)).filter(
        and_(
            MentorSession.mentor_id == mentor.id,
            MentorSession.status == SessionStatus.COMPLETED
        )
    ).scalar() or 0
    
    # Average session price
    avg_price = db.query(
        func.avg(MentorSession.price)
    ).filter(
        and_(
            MentorSession.mentor_id == mentor.id,
            MentorSession.status == SessionStatus.COMPLETED
        )
    ).scalar() or 0.0
    
    return EarningsSummary(
        total_earnings=round(total_earnings_result, 2),
        available_balance=round(available_balance, 2),
        pending_payouts=round(pending_payouts, 2),
        completed_payouts=round(completed_payouts, 2),
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        average_session_price=round(avg_price, 2)
    )


@router.get("/earnings", response_model=List[EarningDetail])
def get_earnings_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed earnings history for the mentor.
    Shows all earnings from completed sessions.
    """
    mentor = get_mentor_or_404(current_user, db)
    
    earnings = db.query(MentorEarning).filter(
        MentorEarning.mentor_id == mentor.id
    ).order_by(MentorEarning.earned_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for earning in earnings:
        session = earning.session
        student = session.student
        result.append(EarningDetail(
            id=earning.id,
            session_id=earning.session_id,
            student_name=student.name if student else "Unknown",
            topic=session.topic,
            gross_amount=earning.gross_amount,
            platform_fee=earning.platform_fee,
            net_amount=earning.net_amount,
            earned_at=earning.earned_at,
            is_paid_out=earning.is_paid_out,
            payout_id=earning.payout_id
        ))
    
    return result


@router.post("/request", response_model=PayoutDetail, status_code=status.HTTP_201_CREATED)
def request_payout(
    payout_request: PayoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request a payout for available earnings.
    Minimum payout amount is $10.
    """
    mentor = get_mentor_or_404(current_user, db)
    
    # Check available balance
    available_balance = db.query(
        func.sum(MentorEarning.net_amount)
    ).filter(
        and_(
            MentorEarning.mentor_id == mentor.id,
            MentorEarning.is_paid_out == False
        )
    ).scalar() or 0.0
    
    if available_balance < 10.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum payout amount is $10. Available balance: ${available_balance:.2f}"
        )
    
    if payout_request.amount > available_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested amount (${payout_request.amount:.2f}) exceeds available balance (${available_balance:.2f})"
        )
    
    # Calculate platform fee (already deducted from earnings, but track for transparency)
    # Since net_amount already has fee deducted, we don't deduct again
    gross_amount = payout_request.amount
    platform_fee = 0.0  # Already deducted at earning time
    net_amount = payout_request.amount
    
    # Create payout request
    payout = MentorPayout(
        mentor_id=mentor.id,
        amount=gross_amount,
        platform_fee=platform_fee,
        net_amount=net_amount,
        method=payout_request.method,
        status=PayoutStatus.PENDING,
        notes=payout_request.notes
    )
    db.add(payout)
    db.commit()
    db.refresh(payout)
    
    # Mark earnings as paid out (up to requested amount)
    unpaid_earnings = db.query(MentorEarning).filter(
        and_(
            MentorEarning.mentor_id == mentor.id,
            MentorEarning.is_paid_out == False
        )
    ).order_by(MentorEarning.earned_at.asc()).all()
    
    remaining_amount = payout_request.amount
    earnings_count = 0
    for earning in unpaid_earnings:
        if remaining_amount <= 0:
            break
        
        if earning.net_amount <= remaining_amount:
            earning.is_paid_out = True
            earning.payout_id = payout.id
            earning.paid_out_at = datetime.utcnow()
            remaining_amount -= earning.net_amount
            earnings_count += 1
        else:
            # Partial earning (shouldn't happen with our logic, but handle it)
            break
    
    db.commit()
    
    return PayoutDetail(
        id=payout.id,
        amount=payout.amount,
        platform_fee=payout.platform_fee,
        net_amount=payout.net_amount,
        method=payout.method,
        status=payout.status,
        requested_at=payout.requested_at,
        earnings_count=earnings_count
    )


@router.get("/history", response_model=List[PayoutDetail])
def get_payout_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payout request history for the mentor.
    """
    mentor = get_mentor_or_404(current_user, db)
    
    payouts = db.query(MentorPayout).filter(
        MentorPayout.mentor_id == mentor.id
    ).order_by(MentorPayout.requested_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for payout in payouts:
        # Count earnings in this payout
        earnings_count = db.query(func.count(MentorEarning.id)).filter(
            MentorEarning.payout_id == payout.id
        ).scalar() or 0
        
        result.append(PayoutDetail(
            id=payout.id,
            amount=payout.amount,
            platform_fee=payout.platform_fee,
            net_amount=payout.net_amount,
            method=payout.method,
            status=payout.status,
            requested_at=payout.requested_at,
            processed_at=payout.processed_at,
            completed_at=payout.completed_at,
            failure_reason=payout.failure_reason,
            earnings_count=earnings_count
        ))
    
    return result


@router.get("/sessions/completed", response_model=List[SessionEarningDetail])
def get_completed_sessions(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all completed sessions with payment information.
    """
    mentor = get_mentor_or_404(current_user, db)
    
    sessions = db.query(MentorSession).filter(
        and_(
            MentorSession.mentor_id == mentor.id,
            MentorSession.status == SessionStatus.COMPLETED
        )
    ).order_by(MentorSession.completed_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for session in sessions:
        student = session.student
        result.append(SessionEarningDetail(
            session_id=session.id,
            student_name=student.name if student else "Unknown",
            topic=session.topic,
            scheduled_at=session.scheduled_at,
            duration_minutes=session.duration_minutes,
            price=session.price,
            payment_status=session.payment_status,
            status=session.status.value
        ))
    
    return result


# ========== PAYMENT METHODS ENDPOINTS ==========

@router.post("/payment-methods", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
def create_payment_method(
    payment_method: PaymentMethodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new payment method (bank account) for payouts.
    Account numbers and routing numbers are encrypted before storage.
    """
    mentor = get_mentor_or_404(current_user, db)
    
    # Check if account already exists
    existing = db.query(PaymentMethod).filter(
        and_(
            PaymentMethod.mentor_id == mentor.id,
            PaymentMethod.account_number_encrypted == payment_method.account_number[-4:]  # Check last 4 digits
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account is already registered"
        )
    
    # If setting as default, unset other defaults
    if payment_method.is_default:
        db.query(PaymentMethod).filter(
            PaymentMethod.mentor_id == mentor.id
        ).update({"is_default": False})
    
    # Create payment method (encryption will be done in crypto utility)
    # For now, store encrypted version (would use cryptography.fernet in production)
    from cryptography.fernet import Fernet
    import os
    
    # Get encryption key from environment
    encryption_key = os.getenv("ENCRYPTION_KEY")
    if not encryption_key:
        encryption_key = Fernet.generate_key()
    
    cipher = Fernet(encryption_key)
    
    # Encrypt sensitive fields
    account_encrypted = cipher.encrypt(payment_method.account_number.encode()).decode()
    routing_encrypted = cipher.encrypt(payment_method.routing_number.encode()).decode()
    
    new_payment_method = PaymentMethod(
        mentor_id=mentor.id,
        payment_type=payment_method.payment_type,
        account_holder_name=payment_method.account_holder_name,
        bank_name=payment_method.bank_name,
        account_number_encrypted=account_encrypted,
        routing_number_encrypted=routing_encrypted,
        status=PaymentMethodStatus.PENDING,
        is_default=payment_method.is_default
    )
    
    db.add(new_payment_method)
    db.commit()
    db.refresh(new_payment_method)
    
    return PaymentMethodResponse(
        id=new_payment_method.id,
        payment_type=new_payment_method.payment_type,
        account_holder_name=new_payment_method.account_holder_name,
        bank_name=new_payment_method.bank_name,
        account_last_four=payment_method.account_number[-4:],
        status=new_payment_method.status,
        is_default=new_payment_method.is_default,
        verified_at=new_payment_method.verified_at,
        created_at=new_payment_method.created_at
    )


@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
def list_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all payment methods for the mentor.
    """
    mentor = get_mentor_or_404(current_user, db)
    
    payment_methods = db.query(PaymentMethod).filter(
        PaymentMethod.mentor_id == mentor.id
    ).order_by(PaymentMethod.is_default.desc(), PaymentMethod.created_at.desc()).all()
    
    result = []
    for pm in payment_methods:
        # Extract last 4 digits from encrypted account (would decrypt in production)
        account_last_four = "****" if pm.account_number_encrypted else "****"
        
        result.append(PaymentMethodResponse(
            id=pm.id,
            payment_type=pm.payment_type,
            account_holder_name=pm.account_holder_name,
            bank_name=pm.bank_name,
            account_last_four=account_last_four,
            status=pm.status,
            is_default=pm.is_default,
            verified_at=pm.verified_at,
            created_at=pm.created_at
        ))
    
    return result


@router.put("/payment-methods/{payment_method_id}", response_model=PaymentMethodResponse)
def update_payment_method(
    payment_method_id: int,
    update_data: PaymentMethodUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update payment method details.
    Can update name, bank, and default status.
    """
    mentor = get_mentor_or_404(current_user, db)
    
    payment_method = db.query(PaymentMethod).filter(
        and_(
            PaymentMethod.id == payment_method_id,
            PaymentMethod.mentor_id == mentor.id
        )
    ).first()
    
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    if update_data.account_holder_name:
        payment_method.account_holder_name = update_data.account_holder_name
    
    if update_data.bank_name:
        payment_method.bank_name = update_data.bank_name
    
    if update_data.is_default is not None:
        if update_data.is_default:
            # Unset other defaults
            db.query(PaymentMethod).filter(
                and_(
                    PaymentMethod.mentor_id == mentor.id,
                    PaymentMethod.id != payment_method_id
                )
            ).update({"is_default": False})
        
        payment_method.is_default = update_data.is_default
    
    db.commit()
    db.refresh(payment_method)
    
    return PaymentMethodResponse(
        id=payment_method.id,
        payment_type=payment_method.payment_type,
        account_holder_name=payment_method.account_holder_name,
        bank_name=payment_method.bank_name,
        account_last_four="****",
        status=payment_method.status,
        is_default=payment_method.is_default,
        verified_at=payment_method.verified_at,
        created_at=payment_method.created_at
    )


@router.delete("/payment-methods/{payment_method_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_method(
    payment_method_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a payment method.
    Cannot delete if there are pending payouts using this method.
    """
    mentor = get_mentor_or_404(current_user, db)
    
    payment_method = db.query(PaymentMethod).filter(
        and_(
            PaymentMethod.id == payment_method_id,
            PaymentMethod.mentor_id == mentor.id
        )
    ).first()
    
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    # Check for pending payouts
    pending_payouts = db.query(PayoutRequestModel).filter(
        and_(
            PayoutRequestModel.payment_method_id == payment_method_id,
            PayoutRequestModel.status.in_(["PENDING", "PROCESSING"])
        )
    ).first()
    
    if pending_payouts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete payment method with pending payouts"
        )
    
    db.delete(payment_method)
    db.commit()
    
    return None


@router.post("/payout-request", response_model=PayoutRequestResponse, status_code=status.HTTP_201_CREATED)
def create_payout_request(
    payout_request: PayoutRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request a payout from available earnings.
    Minimum payout: $10.
    Maximum payout: $100,000 per request.
    """
    mentor = get_mentor_or_404(current_user, db)
    
    # Check available balance
    available_balance = db.query(
        func.sum(MentorEarning.net_amount)
    ).filter(
        and_(
            MentorEarning.mentor_id == mentor.id,
            MentorEarning.is_paid_out == False
        )
    ).scalar() or 0.0
    
    if available_balance < 10.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum payout is $10. Available: ${available_balance:.2f}"
        )
    
    if payout_request.amount > available_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested ${payout_request.amount:.2f} exceeds available ${available_balance:.2f}"
        )
    
    # Verify payment method if provided
    if payout_request.payment_method_id:
        payment_method = db.query(PaymentMethod).filter(
            and_(
                PaymentMethod.id == payout_request.payment_method_id,
                PaymentMethod.mentor_id == mentor.id
            )
        ).first()
        
        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        
        if payment_method.status != PaymentMethodStatus.VERIFIED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment method not verified"
            )
    
    # Create payout request
    new_payout = PayoutRequestModel(
        mentor_id=mentor.id,
        payment_method_id=payout_request.payment_method_id,
        amount=int(payout_request.amount * 100),  # Store in cents
        status="PENDING"
    )
    
    db.add(new_payout)
    db.commit()
    db.refresh(new_payout)
    
    return PayoutRequestResponse(
        id=new_payout.id,
        amount=new_payout.amount / 100,  # Convert back to dollars
        status=new_payout.status,
        payment_method_id=new_payout.payment_method_id,
        rejection_reason=new_payout.rejection_reason,
        created_at=new_payout.created_at,
        updated_at=new_payout.updated_at,
        approved_at=new_payout.approved_at,
        completed_at=new_payout.completed_at
    )