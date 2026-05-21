"""
FastAPI routes for Job Application tracking
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
from typing import List, Optional

from app.core.db import get_db
from app.core.security import get_current_user
from app.modelsx.job_application import JobApplication, ApplicationStatus
from app.schemas.job_application import (
    JobApplicationCreate, JobApplicationUpdate, JobApplicationOut, JobApplicationStats
)

router = APIRouter(prefix="/job-applications", tags=["job-applications"])


@router.post("", response_model=JobApplicationOut)
def create_job_application(
    application: JobApplicationCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job application"""
    db_application = JobApplication(
        **application.model_dump(),
        user_id=current_user.id
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


@router.get("", response_model=List[JobApplicationOut])
def list_job_applications(
    status: Optional[str] = Query(None),
    priority: Optional[int] = Query(None),
    company: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("application_date", description="Field to sort by"),
    order: str = Query("desc", description="asc or desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List job applications with filters and pagination"""
    query = db.query(JobApplication).filter(JobApplication.user_id == current_user.id)
    
    # Apply filters
    if status:
        try:
            status_enum = ApplicationStatus(status)
            query = query.filter(JobApplication.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    if priority:
        query = query.filter(JobApplication.priority == priority)
    
    if company:
        query = query.filter(JobApplication.company_name.ilike(f"%{company}%"))
    
    if search:
        query = query.filter(
            (JobApplication.company_name.ilike(f"%{search}%")) |
            (JobApplication.position_title.ilike(f"%{search}%")) |
            (JobApplication.description.ilike(f"%{search}%"))
        )
    
    # Sort
    sort_column = getattr(JobApplication, sort_by, JobApplication.application_date)
    if order.lower() == "asc":
        query = query.order_by(sort_column)
    else:
        query = query.order_by(desc(sort_column))
    
    # Pagination
    total = query.count()
    applications = query.offset(skip).limit(limit).all()
    
    return applications


@router.get("/stats", response_model=JobApplicationStats)
def get_job_applications_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for job applications"""
    query = db.query(JobApplication).filter(JobApplication.user_id == current_user.id)
    
    total = query.count()
    
    # By status
    by_status = {}
    for status in ApplicationStatus:
        count = query.filter(JobApplication.status == status).count()
        if count > 0:
            by_status[status.value] = count
    
    # Response rate
    responded = query.filter(JobApplication.response_date.isnot(None)).count()
    response_rate = responded / total if total > 0 else 0
    
    # Average response time
    applications_with_response = query.filter(
        JobApplication.response_date.isnot(None)
    ).all()
    
    avg_response_time = None
    if applications_with_response:
        total_days = sum(
            (app.response_date - app.application_date).days
            for app in applications_with_response
        )
        avg_response_time = total_days / len(applications_with_response)
    
    # Salary stats
    salary_query = query.filter(JobApplication.salary_min.isnot(None))
    avg_salary_min = None
    avg_salary_max = None
    
    if salary_query.count() > 0:
        salaries_min = [app.salary_min for app in salary_query.all() if app.salary_min]
        salaries_max = [app.salary_max for app in salary_query.all() if app.salary_max]
        avg_salary_min = sum(salaries_min) / len(salaries_min) if salaries_min else None
        avg_salary_max = sum(salaries_max) / len(salaries_max) if salaries_max else None
    
    # This month
    this_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month = query.filter(JobApplication.application_date >= this_month_start).count()
    
    # Offers
    offers = query.filter(JobApplication.status.in_([ApplicationStatus.OFFER, ApplicationStatus.ACCEPTED])).count()
    
    # Interviews scheduled
    interviews = query.filter(JobApplication.interviews.isnot(None)).count()
    
    # Overdue follow-ups
    now = datetime.utcnow()
    overdue = query.filter(
        and_(
            JobApplication.follow_up_date.isnot(None),
            JobApplication.follow_up_date < now
        )
    ).count()
    
    return JobApplicationStats(
        total_applications=total,
        by_status=by_status,
        response_rate=round(response_rate, 2),
        avg_response_time_days=round(avg_response_time, 1) if avg_response_time else None,
        avg_salary_min=avg_salary_min,
        avg_salary_max=avg_salary_max,
        applications_this_month=this_month,
        offers_received=offers,
        interviews_scheduled=interviews,
        overdue_follow_ups=overdue
    )


@router.get("/{app_id}", response_model=JobApplicationOut)
def get_job_application(
    app_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific job application"""
    application = db.query(JobApplication).filter(
        JobApplication.id == app_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")
    
    return application


@router.patch("/{app_id}", response_model=JobApplicationOut)
def update_job_application(
    app_id: int,
    update_data: JobApplicationUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a job application"""
    application = db.query(JobApplication).filter(
        JobApplication.id == app_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(application, field, value)
    
    application.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(application)
    
    return application


@router.delete("/{app_id}")
def delete_job_application(
    app_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a job application"""
    application = db.query(JobApplication).filter(
        JobApplication.id == app_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")
    
    db.delete(application)
    db.commit()
    
    return {"message": "Job application deleted successfully"}


@router.post("/{app_id}/add-interview")
def add_interview(
    app_id: int,
    interview_date: datetime = Query(...),
    interview_type: str = Query(...),
    interviewer: Optional[str] = Query(None),
    notes: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an interview to a job application"""
    application = db.query(JobApplication).filter(
        JobApplication.id == app_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")
    
    interview = {
        "date": interview_date.isoformat(),
        "type": interview_type,
        "interviewer": interviewer,
        "notes": notes,
        "status": "scheduled"
    }
    
    if application.interviews is None:
        application.interviews = []
    
    application.interviews.append(interview)
    application.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(application)
    
    return application


@router.post("/{app_id}/add-contact")
def add_contact(
    app_id: int,
    name: str = Query(...),
    role: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    linkedin: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a contact to a job application"""
    application = db.query(JobApplication).filter(
        JobApplication.id == app_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")
    
    contact = {
        "name": name,
        "role": role,
        "email": email,
        "phone": phone,
        "linkedin": linkedin
    }
    
    if application.contacts is None:
        application.contacts = []
    
    application.contacts.append(contact)
    application.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(application)
    
    return application
