"""
Email integration for Job Application Tracker
Sends notifications for follow-ups, interviews, and status changes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.db import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.modelsx.job_application import JobApplication, ApplicationStatus

router = APIRouter(prefix="/api/v1x/job-applications-notifications", tags=["job-notifications"])


def send_email(to_email: str, subject: str, body: str, html_body: Optional[str] = None):
    """Send email notification"""
    try:
        # Email settings from environment variables (aligned with core/config.py)
        smtp_server = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        smtp_port = getattr(settings, 'SMTP_PORT', 587)
        smtp_user = getattr(settings, 'SMTP_USER', None)
        smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        from_email = getattr(settings, 'EMAIL_FROM', smtp_user)
        
        if not smtp_user or not smtp_password:
            print("Email not configured. Set SMTP_USER and SMTP_PASSWORD in environment.")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach plain text
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach HTML if provided
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def generate_follow_up_email_template(application: JobApplication) -> tuple:
    """Generate follow-up reminder email"""
    subject = f"⏰ Follow-up Reminder: {application.position_title} at {application.company_name}"
    
    body = f"""
Hi there!

This is a reminder to follow up on your application for {application.position_title} at {application.company_name}.

Application Details:
- Position: {application.position_title}
- Company: {application.company_name}
- Applied: {application.application_date.strftime('%Y-%m-%d')}
- Days since applied: {(datetime.utcnow() - application.application_date).days}
- Current Status: {application.status.value}

Recommended Actions:
1. Send a polite follow-up email to the hiring manager
2. Check the application portal for updates
3. Connect with employees on LinkedIn for insights
4. Update your application status in the tracker

Good luck with your job search!

---
SkillForge Global Job Tracker
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .details {{ background: #f4f4f4; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0; }}
        .actions {{ background: #e3f2fd; padding: 15px; border-radius: 5px; }}
        .actions li {{ margin: 10px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⏰ Follow-up Reminder</h1>
    </div>
    <div class="content">
        <p>Hi there!</p>
        <p>This is a reminder to follow up on your application for <strong>{application.position_title}</strong> at <strong>{application.company_name}</strong>.</p>
        
        <div class="details">
            <h3>Application Details</h3>
            <ul style="list-style: none; padding: 0;">
                <li>📋 <strong>Position:</strong> {application.position_title}</li>
                <li>🏢 <strong>Company:</strong> {application.company_name}</li>
                <li>📅 <strong>Applied:</strong> {application.application_date.strftime('%Y-%m-%d')}</li>
                <li>⏱️ <strong>Days since applied:</strong> {(datetime.utcnow() - application.application_date).days}</li>
                <li>📊 <strong>Current Status:</strong> {application.status.value.capitalize()}</li>
            </ul>
        </div>
        
        <div class="actions">
            <h3>Recommended Actions</h3>
            <ol>
                <li>Send a polite follow-up email to the hiring manager</li>
                <li>Check the application portal for updates</li>
                <li>Connect with employees on LinkedIn for insights</li>
                <li>Update your application status in the tracker</li>
            </ol>
        </div>
        
        <p>Good luck with your job search! 🚀</p>
    </div>
    <div class="footer">
        <p>SkillForge Global Job Tracker</p>
        <p><a href="http://localhost:3001/job-tracker/{application.id}">View Application</a></p>
    </div>
</body>
</html>
"""
    
    return subject, body, html_body


def generate_interview_reminder_email(application: JobApplication, interview: dict) -> tuple:
    """Generate interview reminder email"""
    subject = f"🎯 Interview Reminder: {application.position_title} at {application.company_name}"
    
    interview_date = datetime.fromisoformat(interview['date'].replace('Z', '+00:00'))
    
    body = f"""
Hi there!

You have an upcoming interview for {application.position_title} at {application.company_name}!

Interview Details:
- Position: {application.position_title}
- Company: {application.company_name}
- Interview Type: {interview['type'].upper()}
- Date & Time: {interview_date.strftime('%Y-%m-%d %H:%M')}
- Interviewer: {interview.get('interviewer', 'Not specified')}

Preparation Tips:
1. Research the company and recent news
2. Review the job description and match your skills
3. Prepare STAR method examples
4. Test your tech (camera/microphone) if virtual
5. Prepare thoughtful questions to ask

Good luck! 🍀

---
SkillForge Global Job Tracker
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .details {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
        .tips {{ background: #d1ecf1; padding: 15px; border-radius: 5px; }}
        .tips li {{ margin: 10px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Interview Reminder</h1>
    </div>
    <div class="content">
        <p>Hi there!</p>
        <p>You have an upcoming interview for <strong>{application.position_title}</strong> at <strong>{application.company_name}</strong>!</p>
        
        <div class="details">
            <h3>Interview Details</h3>
            <ul style="list-style: none; padding: 0;">
                <li>📋 <strong>Position:</strong> {application.position_title}</li>
                <li>🏢 <strong>Company:</strong> {application.company_name}</li>
                <li>🎤 <strong>Interview Type:</strong> {interview['type'].upper()}</li>
                <li>📅 <strong>Date & Time:</strong> {interview_date.strftime('%Y-%m-%d %H:%M')}</li>
                <li>👤 <strong>Interviewer:</strong> {interview.get('interviewer', 'Not specified')}</li>
            </ul>
        </div>
        
        <div class="tips">
            <h3>Preparation Tips</h3>
            <ol>
                <li>Research the company and recent news</li>
                <li>Review the job description and match your skills</li>
                <li>Prepare STAR method examples</li>
                <li>Test your tech (camera/microphone) if virtual</li>
                <li>Prepare thoughtful questions to ask</li>
            </ol>
        </div>
        
        <p>Good luck! 🍀</p>
    </div>
    <div class="footer">
        <p>SkillForge Global Job Tracker</p>
        <p><a href="http://localhost:3001/job-tracker/{application.id}">View Application</a></p>
    </div>
</body>
</html>
"""
    
    return subject, body, html_body


@router.post("/send-follow-up-reminders")
async def send_follow_up_reminders(
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send follow-up reminders for overdue applications"""
    now = datetime.utcnow()
    
    # Find applications that need follow-up
    overdue_applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.follow_up_date.isnot(None),
        JobApplication.follow_up_date < now,
        JobApplication.status.in_([ApplicationStatus.APPLIED, ApplicationStatus.SCREENING])
    ).all()
    
    sent_count = 0
    for app in overdue_applications:
        subject, body, html_body = generate_follow_up_email_template(app)
        if send_email(current_user.email, subject, body, html_body):
            sent_count += 1
    
    return {
        "message": f"Sent {sent_count} follow-up reminders",
        "total_overdue": len(overdue_applications)
    }


@router.post("/send-interview-reminders")
async def send_interview_reminders(
    background_tasks: BackgroundTasks,
    hours_before: int = 24,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send interview reminders for upcoming interviews"""
    now = datetime.utcnow()
    reminder_window = now + timedelta(hours=hours_before)
    
    # Find applications with interviews in the next X hours
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.interviews.isnot(None)
    ).all()
    
    sent_count = 0
    for app in applications:
        if not app.interviews:
            continue
        
        for interview in app.interviews:
            try:
                interview_date = datetime.fromisoformat(interview['date'].replace('Z', '+00:00'))
                
                # Check if interview is within reminder window
                if now < interview_date < reminder_window:
                    subject, body, html_body = generate_interview_reminder_email(app, interview)
                    if send_email(current_user.email, subject, body, html_body):
                        sent_count += 1
            except Exception as e:
                print(f"Error processing interview: {e}")
                continue
    
    return {
        "message": f"Sent {sent_count} interview reminders",
        "hours_before": hours_before
    }


@router.post("/{app_id}/send-custom-reminder")
async def send_custom_reminder(
    app_id: int,
    subject: str,
    message: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a custom reminder email for a specific application"""
    application = db.query(JobApplication).filter(
        JobApplication.id == app_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    html_body = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="background: #667eea; color: white; padding: 20px; text-align: center;">
        <h1>{subject}</h1>
    </div>
    <div style="padding: 20px;">
        <p>{message}</p>
        <hr style="margin: 20px 0;">
        <p><strong>Application:</strong> {application.position_title} at {application.company_name}</p>
        <p><a href="http://localhost:3001/job-tracker/{application.id}" style="color: #667eea;">View Application</a></p>
    </div>
</body>
</html>
"""
    
    if send_email(current_user.email, subject, message, html_body):
        return {"message": "Reminder sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send email")


@router.get("/pending-reminders")
async def get_pending_reminders(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of pending reminders"""
    now = datetime.utcnow()
    
    # Overdue follow-ups
    overdue_followups = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.follow_up_date.isnot(None),
        JobApplication.follow_up_date < now,
        JobApplication.status.in_([ApplicationStatus.APPLIED, ApplicationStatus.SCREENING])
    ).count()
    
    # Upcoming interviews (next 48 hours)
    applications_with_interviews = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.interviews.isnot(None)
    ).all()
    
    upcoming_interviews = 0
    for app in applications_with_interviews:
        if not app.interviews:
            continue
        for interview in app.interviews:
            try:
                interview_date = datetime.fromisoformat(interview['date'].replace('Z', '+00:00'))
                if now < interview_date < now + timedelta(hours=48):
                    upcoming_interviews += 1
            except:
                continue
    
    return {
        "overdue_followups": overdue_followups,
        "upcoming_interviews": upcoming_interviews,
        "total_pending": overdue_followups + upcoming_interviews
    }
