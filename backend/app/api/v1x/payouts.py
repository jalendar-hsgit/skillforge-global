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
