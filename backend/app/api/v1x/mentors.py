"""
Mentor System API endpoints.
Handles mentor applications, sessions, availability, reviews, and messaging.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.mentor import (
    Mentor, MentorSession, MentorAvailability, 
    MentorMessage, MentorReview, MentorStatus, SessionStatus
)
from app.schemas.mentor import (
    MentorApplicationRequest, MentorProfileResponse, MentorProfileUpdate,
    MentorEligibilityResponse, SessionBookingRequest, SessionResponse,
    SessionListResponse, SessionUpdateRequest, AvailabilitySlotRequest,
    AvailabilitySlotResponse, AvailabilityListResponse, MessageSendRequest,
    MessageResponse, MessageListResponse, ReviewSubmitRequest, ReviewResponse,
    ReviewListResponse, MentorDashboardStats, StudentDashboardStats
)
from app.services.mentor_service import (
    MentorEligibilityService, MentorSearchService, SessionManagementService
)
from app.services.email_service import email_service

router = APIRouter(prefix="/mentors", tags=["mentors"])


# ============ Mentor Application & Profile ============

@router.get("/eligibility", response_model=MentorEligibilityResponse)
def check_mentor_eligibility(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if current user is eligible to become a mentor.
    
    Requirements:
    - Completed at least 1 learning path
    - Average quiz score of 80%+
    """
    eligible, reasons, completed_paths, avg_score = MentorEligibilityService.check_eligibility(
        current_user.id, db
    )
    
    return MentorEligibilityResponse(
        eligible=eligible,
        reasons=reasons,
        completed_paths=completed_paths,
        average_quiz_score=avg_score
    )


@router.post("/apply", response_model=MentorProfileResponse, status_code=status.HTTP_201_CREATED)
def apply_to_become_mentor(
    application: MentorApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply to become a mentor.
    User must be eligible (completed paths + good quiz scores).
    """
    # Check if already a mentor
    existing = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to become a mentor"
        )
    
    # Check eligibility
    eligible, reasons, _, _ = MentorEligibilityService.check_eligibility(current_user.id, db)
    if not eligible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not eligible to become a mentor: {'; '.join(reasons)}"
        )
    
    # Create mentor profile
    mentor = Mentor(
        user_id=current_user.id,
        bio=application.bio,
        expertise=application.expertise,
        hourly_rate=application.hourly_rate,
        status=MentorStatus.PENDING
    )
    
    db.add(mentor)
    db.commit()
    db.refresh(mentor)
    
    # Build response with user email
    response = MentorProfileResponse(
        id=mentor.id,
        user_id=mentor.user_id,
        email=current_user.email,
        bio=mentor.bio,
        expertise=mentor.expertise,
        hourly_rate=mentor.hourly_rate,
        status=mentor.status,
        total_sessions=mentor.total_sessions,
        average_rating=mentor.average_rating,
        created_at=mentor.created_at
    )
    
    return response


@router.get("/me", response_model=MentorProfileResponse)
def get_my_mentor_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's mentor profile."""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a mentor"
        )
    
    return MentorProfileResponse(
        id=mentor.id,
        user_id=mentor.user_id,
        email=current_user.email,
        bio=mentor.bio,
        expertise=mentor.expertise,
        hourly_rate=mentor.hourly_rate,
        status=mentor.status,
        total_sessions=mentor.total_sessions,
        average_rating=mentor.average_rating,
        created_at=mentor.created_at
    )


@router.patch("/me", response_model=MentorProfileResponse)
def update_my_mentor_profile(
    updates: MentorProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's mentor profile."""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a mentor"
        )
    
    # Update fields
    if updates.bio:
        mentor.bio = updates.bio
    if updates.expertise:
        mentor.expertise = updates.expertise
    if updates.hourly_rate is not None:
        mentor.hourly_rate = updates.hourly_rate
    
    mentor.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(mentor)
    
    return MentorProfileResponse(
        id=mentor.id,
        user_id=mentor.user_id,
        email=current_user.email,
        bio=mentor.bio,
        expertise=mentor.expertise,
        hourly_rate=mentor.hourly_rate,
        status=mentor.status,
        total_sessions=mentor.total_sessions,
        average_rating=mentor.average_rating,
        created_at=mentor.created_at
    )


@router.get("/search", response_model=List[MentorProfileResponse])
def search_mentors(
    expertise: Optional[str] = Query(None, description="Filter by expertise (e.g., 'python-ai')"),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    max_rate: Optional[float] = Query(None, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search for available mentors with filters.
    Only returns approved mentors.
    """
    mentors = MentorSearchService.search_mentors(
        db, expertise=expertise, min_rating=min_rating, 
        max_rate=max_rate, limit=limit
    )
    
    # Build responses
    results = []
    for mentor in mentors:
        user = db.query(User).filter(User.id == mentor.user_id).first()
        results.append(MentorProfileResponse(
            id=mentor.id,
            user_id=mentor.user_id,
            email=user.email if user else "unknown@example.com",
            bio=mentor.bio,
            expertise=mentor.expertise,
            hourly_rate=mentor.hourly_rate,
            status=mentor.status,
            total_sessions=mentor.total_sessions,
            average_rating=mentor.average_rating,
            created_at=mentor.created_at
        ))
    
    return results


@router.get("/{mentor_id}", response_model=MentorProfileResponse)
def get_mentor_profile(mentor_id: int, db: Session = Depends(get_db)):
    """Get a specific mentor's profile."""
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found"
        )
    
    user = db.query(User).filter(User.id == mentor.user_id).first()
    
    return MentorProfileResponse(
        id=mentor.id,
        user_id=mentor.user_id,
        email=user.email if user else "unknown@example.com",
        bio=mentor.bio,
        expertise=mentor.expertise,
        hourly_rate=mentor.hourly_rate,
        status=mentor.status,
        total_sessions=mentor.total_sessions,
        average_rating=mentor.average_rating,
        created_at=mentor.created_at
    )


# ============ Session Booking & Management ============

@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def book_session(
    booking: SessionBookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Book a mentoring session."""
    # Check if can book
    can_book, reason = SessionManagementService.can_book_session(
        current_user.id, booking.mentor_id, booking.scheduled_at, db
    )
    
    if not can_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reason
        )
    
    # Get mentor to get price
    mentor = db.query(Mentor).filter(Mentor.id == booking.mentor_id).first()
    price = mentor.hourly_rate * (booking.duration_minutes / 60)
    
    # Create session
    session = MentorSession(
        mentor_id=booking.mentor_id,
        student_id=current_user.id,
        topic=booking.topic,
        description=booking.description,
        scheduled_at=booking.scheduled_at,
        duration_minutes=booking.duration_minutes,
        status=SessionStatus.PENDING,
        price=price
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Send booking notification to mentor
    mentor_user = db.query(User).filter(User.id == mentor.user_id).first()
    if mentor_user and mentor_user.email:
        # Note: In production, send this asynchronously using Celery/background tasks
        try:
            import asyncio
            asyncio.create_task(
                email_service.send_session_confirmation(
                    to_email=mentor_user.email,
                    mentor_name=mentor_user.name,
                    student_name=current_user.name,
                    session_date=session.scheduled_at,
                    session_duration=session.duration_minutes,
                    meeting_url=session.meeting_url or "TBD (will be provided when confirmed)",
                    session_id=session.id
                )
            )
        except Exception as e:
            # Log error but don't fail the booking
            print(f"Failed to send email: {e}")
    
    return SessionResponse(
        id=session.id,
        mentor_id=session.mentor_id,
        student_id=session.student_id,
        topic=session.topic,
        description=session.description,
        scheduled_at=session.scheduled_at,
        duration_minutes=session.duration_minutes,
        status=session.status,
        meeting_url=session.meeting_url,
        price=session.price,
        payment_status=session.payment_status,
        created_at=session.created_at
    )


@router.get("/sessions/my", response_model=SessionListResponse)
def get_my_sessions(
    as_mentor: bool = Query(False, description="Get sessions where you are the mentor"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's sessions (as student or mentor)."""
    if as_mentor:
        # Get mentor profile
        mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
        if not mentor:
            return SessionListResponse(sessions=[], total=0)
        
        query = db.query(MentorSession).filter(MentorSession.mentor_id == mentor.id)
    else:
        query = db.query(MentorSession).filter(MentorSession.student_id == current_user.id)
    
    if status_filter:
        query = query.filter(MentorSession.status == status_filter)
    
    sessions = query.order_by(MentorSession.scheduled_at.desc()).all()
    
    session_responses = [
        SessionResponse(
            id=s.id,
            mentor_id=s.mentor_id,
            student_id=s.student_id,
            topic=s.topic,
            description=s.description,
            scheduled_at=s.scheduled_at,
            duration_minutes=s.duration_minutes,
            status=s.status,
            meeting_url=s.meeting_url,
            price=s.price,
            payment_status=s.payment_status,
            created_at=s.created_at
        )
        for s in sessions
    ]
    
    return SessionListResponse(sessions=session_responses, total=len(session_responses))


@router.patch("/sessions/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    updates: SessionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a session (mentor or student can update based on permissions)."""
    session = db.query(MentorSession).filter(MentorSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check permissions
    mentor = db.query(Mentor).filter(Mentor.id == session.mentor_id).first()
    is_mentor = mentor and mentor.user_id == current_user.id
    is_student = session.student_id == current_user.id
    
    if not (is_mentor or is_student):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this session"
        )
    
    # Track status change for emails
    old_status = session.status
    status_changed = False
    
    # Update fields
    if updates.status and is_mentor:
        if session.status != updates.status:
            status_changed = True
        session.status = updates.status
        if updates.status == SessionStatus.CONFIRMED and not session.meeting_url:
            # Generate meeting URL when confirming
            session.meeting_url = SessionManagementService.generate_meeting_url(session_id)
        if updates.status == SessionStatus.COMPLETED:
            session.completed_at = datetime.utcnow()
    
    if updates.meeting_url and is_mentor:
        session.meeting_url = updates.meeting_url
    
    if updates.mentor_notes and is_mentor:
        session.mentor_notes = updates.mentor_notes
    
    if updates.student_feedback and is_student:
        session.student_feedback = updates.student_feedback
    
    db.commit()
    db.refresh(session)
    
    # Send email notifications on status change
    if status_changed:
        mentor_user = db.query(User).join(Mentor).filter(Mentor.id == session.mentor_id).first()
        student_user = db.query(User).filter(User.id == session.student_id).first()
        
        try:
            import asyncio
            if session.status == SessionStatus.CONFIRMED and student_user and student_user.email:
                # Notify student that session is confirmed
                asyncio.create_task(
                    email_service.send_session_confirmation(
                        to_email=student_user.email,
                        mentor_name=mentor_user.name if mentor_user else "Mentor",
                        student_name=student_user.name,
                        session_date=session.scheduled_at,
                        session_duration=session.duration_minutes,
                        meeting_url=session.meeting_url or "TBD",
                        session_id=session.id
                    )
                )
            elif session.status == SessionStatus.CANCELLED:
                # Notify both parties about cancellation
                if student_user and student_user.email:
                    asyncio.create_task(
                        email_service.send_session_cancellation(
                            to_email=student_user.email,
                            recipient_name=student_user.name,
                            other_person_name=mentor_user.name if mentor_user else "Mentor",
                            session_date=session.scheduled_at,
                            reason=updates.mentor_notes or "Cancelled by mentor",
                            session_id=session.id
                        )
                    )
                if mentor_user and mentor_user.email:
                    asyncio.create_task(
                        email_service.send_session_cancellation(
                            to_email=mentor_user.email,
                            recipient_name=mentor_user.name,
                            other_person_name=student_user.name if student_user else "Student",
                            session_date=session.scheduled_at,
                            reason="Cancelled",
                            session_id=session.id
                        )
                    )
        except Exception as e:
            # Log error but don't fail the update
            print(f"Failed to send email: {e}")
    
    return SessionResponse(
        id=session.id,
        mentor_id=session.mentor_id,
        student_id=session.student_id,
        topic=session.topic,
        description=session.description,
        scheduled_at=session.scheduled_at,
        duration_minutes=session.duration_minutes,
        status=session.status,
        meeting_url=session.meeting_url,
        price=session.price,
        payment_status=session.payment_status,
        created_at=session.created_at
    )


# ============ Availability Management ============

@router.post("/availability", response_model=AvailabilitySlotResponse, status_code=status.HTTP_201_CREATED)
def add_availability_slot(
    slot: AvailabilitySlotRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an availability slot (mentor only)."""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a mentor to add availability"
        )
    
    availability = MentorAvailability(
        mentor_id=mentor.id,
        day_of_week=slot.day_of_week,
        date=slot.date,
        start_time=slot.start_time,
        end_time=slot.end_time,
        timezone=slot.timezone
    )
    
    db.add(availability)
    db.commit()
    db.refresh(availability)
    
    return AvailabilitySlotResponse(
        id=availability.id,
        mentor_id=availability.mentor_id,
        day_of_week=availability.day_of_week,
        date=availability.date,
        start_time=availability.start_time,
        end_time=availability.end_time,
        is_available=availability.is_available,
        is_booked=availability.is_booked,
        timezone=availability.timezone
    )


@router.get("/availability/{mentor_id}", response_model=AvailabilityListResponse)
def get_mentor_availability(mentor_id: int, db: Session = Depends(get_db)):
    """Get a mentor's availability slots."""
    slots = db.query(MentorAvailability).filter(
        MentorAvailability.mentor_id == mentor_id,
        MentorAvailability.is_available == True
    ).all()
    
    slot_responses = [
        AvailabilitySlotResponse(
            id=s.id,
            mentor_id=s.mentor_id,
            day_of_week=s.day_of_week,
            date=s.date,
            start_time=s.start_time,
            end_time=s.end_time,
            is_available=s.is_available,
            is_booked=s.is_booked,
            timezone=s.timezone
        )
        for s in slots
    ]
    
    return AvailabilityListResponse(slots=slot_responses)


# ============ Reviews ============

@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def submit_review(
    review: ReviewSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a review for a completed session."""
    # Check session exists and is completed
    session = db.query(MentorSession).filter(MentorSession.id == review.session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review your own sessions"
        )
    
    if session.status != SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only review completed sessions"
        )
    
    # Check if already reviewed
    existing = db.query(MentorReview).filter(MentorReview.session_id == review.session_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already reviewed"
        )
    
    # Create review
    mentor_review = MentorReview(
        mentor_id=session.mentor_id,
        session_id=review.session_id,
        student_id=current_user.id,
        rating=review.rating,
        review_text=review.review_text,
        tags=review.tags
    )
    
    db.add(mentor_review)
    
    # Update mentor's average rating
    mentor = db.query(Mentor).filter(Mentor.id == session.mentor_id).first()
    all_reviews = db.query(MentorReview).filter(MentorReview.mentor_id == session.mentor_id).all()
    total_rating = sum(r.rating for r in all_reviews) + review.rating
    mentor.average_rating = total_rating / (len(all_reviews) + 1)
    
    db.commit()
    db.refresh(mentor_review)
    
    return ReviewResponse(
        id=mentor_review.id,
        mentor_id=mentor_review.mentor_id,
        session_id=mentor_review.session_id,
        student_id=mentor_review.student_id,
        rating=mentor_review.rating,
        review_text=mentor_review.review_text,
        tags=mentor_review.tags,
        created_at=mentor_review.created_at
    )


@router.get("/reviews/{mentor_id}", response_model=ReviewListResponse)
def get_mentor_reviews(mentor_id: int, limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    """Get reviews for a mentor."""
    reviews = db.query(MentorReview).filter(
        MentorReview.mentor_id == mentor_id
    ).order_by(MentorReview.created_at.desc()).limit(limit).all()
    
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    
    review_responses = [
        ReviewResponse(
            id=r.id,
            mentor_id=r.mentor_id,
            session_id=r.session_id,
            student_id=r.student_id,
            rating=r.rating,
            review_text=r.review_text,
            tags=r.tags,
            created_at=r.created_at
        )
        for r in reviews
    ]
    
    return ReviewListResponse(
        reviews=review_responses,
        total=len(review_responses),
        average_rating=mentor.average_rating if mentor else 0.0
    )
