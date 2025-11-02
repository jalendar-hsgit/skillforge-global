from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.modelsx.job_application import JobApplication, ApplicationStatus
from app.models.user import User
from app.api.v1x.job_application_notifications import (
    send_email,
    generate_follow_up_email_template,
    generate_interview_reminder_email,
)

scheduler = AsyncIOScheduler()


def _with_db(fn):
    def wrapper(*args, **kwargs):
        db: Session = SessionLocal()
        try:
            return fn(db, *args, **kwargs)
        except Exception as e:
            print(f"Scheduler job error: {e}")
        finally:
            db.close()
    return wrapper


@_with_db
def job_send_follow_ups(db: Session):
    now = datetime.utcnow()
    overdue_apps = (
        db.query(JobApplication)
        .filter(
            JobApplication.follow_up_date.isnot(None),
            JobApplication.follow_up_date < now,
            JobApplication.status.in_([ApplicationStatus.APPLIED, ApplicationStatus.SCREENING]),
        )
        .all()
    )

    for app in overdue_apps:
        try:
            user = db.query(User).filter(User.id == app.user_id).first()
            if not user or not getattr(user, 'email', None):
                continue
            subject, body, html = generate_follow_up_email_template(app)
            ok = send_email(user.email, subject, body, html)
            if not ok:
                print(f"Follow-up email not sent (SMTP not configured or failed) for user {user.email}")
        except Exception as e:
            print(f"Error sending follow-up reminder: {e}")


@_with_db
def job_send_interview_reminders(db: Session, hours_before: int = 24):
    now = datetime.utcnow()
    window = now + timedelta(hours=hours_before)

    apps = db.query(JobApplication).filter(JobApplication.interviews.isnot(None)).all()
    for app in apps:
        try:
            user = db.query(User).filter(User.id == app.user_id).first()
            if not user or not getattr(user, 'email', None):
                continue
            for interview in app.interviews or []:
                try:
                    interview_date = datetime.fromisoformat(str(interview.get('date', '')).replace('Z', '+00:00'))
                    if now < interview_date < window:
                        subject, body, html = generate_interview_reminder_email(app, interview)
                        ok = send_email(user.email, subject, body, html)
                        if not ok:
                            print(f"Interview email not sent (SMTP not configured or failed) for user {user.email}")
                except Exception as e:
                    print(f"Interview parse/send error: {e}")
        except Exception as e:
            print(f"Error in interview reminders loop: {e}")


def start_scheduler():
    try:
        # Every 30 minutes: check follow-ups
        scheduler.add_job(job_send_follow_ups, 'interval', minutes=30, id='job_followups', replace_existing=True)
        # Every 15 minutes: check interviews within next 24 hours
        scheduler.add_job(job_send_interview_reminders, 'interval', minutes=15, id='job_interviews', replace_existing=True)
        scheduler.start()
        print("APScheduler started: follow-ups(30m), interviews(15m)")
    except Exception as e:
        print(f"Failed to start scheduler: {e}")


def shutdown_scheduler():
    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)
            print("APScheduler shut down")
    except Exception as e:
        print(f"Failed to shutdown scheduler: {e}")
