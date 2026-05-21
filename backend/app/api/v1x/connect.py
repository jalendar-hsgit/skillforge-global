"""
Stripe Connect onboarding and account management for mentors
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.mentor import Mentor
from app.modelsx.stripe_connect import MentorStripeAccount
from app.services.stripe_service import stripe_service
from app.core.config import settings

router = APIRouter(prefix="/connect", tags=["stripe-connect"])


class ConnectStatus(BaseModel):
    account_id: Optional[str]
    onboarding_complete: bool
    payouts_enabled: bool
    details_submitted: bool
    requirements_due: Optional[str] = None

    class Config:
        from_attributes = True


class CreateAccountResponse(BaseModel):
    account_id: str


class OnboardingLinkResponse(BaseModel):
    url: str


class LoginLinkResponse(BaseModel):
    url: str


def _get_or_create_mentor(user: User, db: Session) -> Mentor:
    mentor = db.query(Mentor).filter(Mentor.user_id == user.id).first()
    if not mentor:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a mentor")
    return mentor


def _get_or_create_account(mentor: Mentor, db: Session) -> MentorStripeAccount:
    record = db.query(MentorStripeAccount).filter(MentorStripeAccount.mentor_id == mentor.id).first()
    if not record:
        record = MentorStripeAccount(mentor_id=mentor.id)
        db.add(record)
        db.commit()
        db.refresh(record)
    return record


@router.post("/create-account", response_model=CreateAccountResponse)
def create_connect_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mentor = _get_or_create_mentor(current_user, db)
    record = _get_or_create_account(mentor, db)

    if record.account_id:
        return {"account_id": record.account_id}

    try:
        acct = stripe_service.create_connect_account(
            email=current_user.email,
            user_id=current_user.id
        )
        record.account_id = acct['id']
        record.payouts_enabled = bool(acct.get('payouts_enabled'))
        record.details_submitted = bool(acct.get('details_submitted'))
        db.commit()
        return {"account_id": record.account_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/onboarding-link", response_model=OnboardingLinkResponse)
def get_onboarding_link(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mentor = _get_or_create_mentor(current_user, db)
    record = _get_or_create_account(mentor, db)

    if not record.account_id:
        raise HTTPException(status_code=400, detail="No Stripe account. Create one first.")

    refresh_url = f"{settings.FRONTEND_ORIGIN}/mentors/settings?onboarding=retry"
    return_url = f"{settings.FRONTEND_ORIGIN}/mentors/settings?onboarding=done"

    try:
        link = stripe_service.create_connect_onboarding_link(
            account_id=record.account_id,
            refresh_url=refresh_url,
            return_url=return_url
        )
        return {"url": link['url']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=ConnectStatus)
def get_connect_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mentor = _get_or_create_mentor(current_user, db)
    record = _get_or_create_account(mentor, db)

    if not record.account_id:
        return ConnectStatus(account_id=None, onboarding_complete=False, payouts_enabled=False, details_submitted=False)

    try:
        acct = stripe_service.get_connect_account(record.account_id)
        record.payouts_enabled = bool(acct.get('payouts_enabled'))
        record.details_submitted = bool(acct.get('details_submitted'))
        # Capture any outstanding requirements for display
        requirements = acct.get('requirements', {})
        due = requirements.get('currently_due') or []
        record.requirements_due = ",".join(due) if isinstance(due, list) else None
        # Onboarding complete when details submitted
        record.onboarding_complete = record.details_submitted and record.payouts_enabled
        db.commit()

        return ConnectStatus(
            account_id=record.account_id,
            onboarding_complete=record.onboarding_complete,
            payouts_enabled=record.payouts_enabled,
            details_submitted=record.details_submitted,
            requirements_due=record.requirements_due,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/login-link", response_model=LoginLinkResponse)
def get_connect_login_link(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mentor = _get_or_create_mentor(current_user, db)
    record = _get_or_create_account(mentor, db)

    if not record.account_id:
        raise HTTPException(status_code=400, detail="No Stripe account.")

    try:
        link = stripe_service.create_connect_login_link(record.account_id)
        return {"url": link['url']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
