"""
Calendar integration for Job Application Tracker
Export interviews to Google Calendar, Outlook, and iCal formats
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import io

from app.core.db import get_db
from app.core.security import get_current_user
from app.modelsx.job_application import JobApplication

router = APIRouter(prefix="/job-applications-calendar", tags=["job-calendar"])


def generate_ical_event(application: JobApplication, interview: dict) -> str:
    """Generate iCal format event for an interview"""
    try:
        interview_date = datetime.fromisoformat(interview['date'].replace('Z', '+00:00'))
        end_date = interview_date + timedelta(hours=1)  # Default 1 hour duration
        
        # Format dates for iCal (YYYYMMDDTHHMMSSZ)
        dtstart = interview_date.strftime('%Y%m%dT%H%M%SZ')
        dtend = end_date.strftime('%Y%m%dT%H%M%SZ')
        dtstamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        
        summary = f"Interview: {application.position_title} at {application.company_name}"
        description = f"""Interview for {application.position_title} position at {application.company_name}

Interview Type: {interview['type'].upper()}
Interviewer: {interview.get('interviewer', 'Not specified')}

Notes: {interview.get('notes', 'No additional notes')}

Application Link: http://localhost:3001/job-tracker/{application.id}
"""
        
        location = application.location or "Virtual"
        
        # Generate unique UID
        uid = f"interview-{application.id}-{interview_date.timestamp()}@skillforge.com"
        
        # Replace newlines for iCal format (outside f-string)
        escaped_description = description.replace('\n', '\\n')
        
        ical = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//SkillForge Global//Job Tracker//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{summary}
DESCRIPTION:{escaped_description}
LOCATION:{location}
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT1H
DESCRIPTION:Interview reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR"""
        
        return ical
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate iCal: {str(e)}")


def generate_google_calendar_url(application: JobApplication, interview: dict) -> str:
    """Generate Google Calendar add event URL"""
    try:
        interview_date = datetime.fromisoformat(interview['date'].replace('Z', '+00:00'))
        end_date = interview_date + timedelta(hours=1)
        
        # Format dates for Google Calendar (YYYYMMDDTHHmmssZ)
        start = interview_date.strftime('%Y%m%dT%H%M%SZ')
        end = end_date.strftime('%Y%m%dT%H%M%SZ')
        
        title = f"Interview: {application.position_title} at {application.company_name}"
        details = f"Interview for {application.position_title}\nType: {interview['type'].upper()}\nInterviewer: {interview.get('interviewer', 'TBD')}\n\nApplication: http://localhost:3001/job-tracker/{application.id}"
        location = application.location or "Virtual"
        
        # URL encode
        import urllib.parse
        params = {
            'action': 'TEMPLATE',
            'text': title,
            'dates': f"{start}/{end}",
            'details': details,
            'location': location
        }
        
        base_url = "https://calendar.google.com/calendar/render"
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        return url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Google Calendar URL: {str(e)}")


def generate_outlook_url(application: JobApplication, interview: dict) -> str:
    """Generate Outlook.com add event URL"""
    try:
        interview_date = datetime.fromisoformat(interview['date'].replace('Z', '+00:00'))
        end_date = interview_date + timedelta(hours=1)
        
        # Format dates for Outlook (ISO 8601)
        start = interview_date.strftime('%Y-%m-%dT%H:%M:%S')
        end = end_date.strftime('%Y-%m-%dT%H:%M:%S')
        
        title = f"Interview: {application.position_title} at {application.company_name}"
        body = f"Interview for {application.position_title}\nType: {interview['type'].upper()}\nInterviewer: {interview.get('interviewer', 'TBD')}\n\nApplication: http://localhost:3001/job-tracker/{application.id}"
        location = application.location or "Virtual"
        
        # URL encode
        import urllib.parse
        params = {
            'path': '/calendar/action/compose',
            'rru': 'addevent',
            'subject': title,
            'body': body,
            'startdt': start,
            'enddt': end,
            'location': location
        }
        
        base_url = "https://outlook.live.com/calendar/0/deeplink/compose"
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        return url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Outlook URL: {str(e)}")


@router.get("/{app_id}/interview/{interview_index}/ical")
async def download_interview_ical(
    app_id: int,
    interview_index: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download interview as iCal file"""
    application = db.query(JobApplication).filter(
        JobApplication.id == app_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if not application.interviews or interview_index >= len(application.interviews):
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview = application.interviews[interview_index]
    ical_content = generate_ical_event(application, interview)
    
    # Return as downloadable file
    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=interview-{application.company_name}.ics"
        }
    )


@router.get("/{app_id}/interview/{interview_index}/google-calendar")
async def get_google_calendar_url(
    app_id: int,
    interview_index: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Google Calendar add event URL"""
    application = db.query(JobApplication).filter(
        JobApplication.id == app_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if not application.interviews or interview_index >= len(application.interviews):
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview = application.interviews[interview_index]
    url = generate_google_calendar_url(application, interview)
    
    return {"url": url}


@router.get("/{app_id}/interview/{interview_index}/outlook")
async def get_outlook_url(
    app_id: int,
    interview_index: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Outlook.com add event URL"""
    application = db.query(JobApplication).filter(
        JobApplication.id == app_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if not application.interviews or interview_index >= len(application.interviews):
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview = application.interviews[interview_index]
    url = generate_outlook_url(application, interview)
    
    return {"url": url}


@router.get("/{app_id}/all-interviews/ical")
async def download_all_interviews_ical(
    app_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download all interviews for an application as iCal file"""
    application = db.query(JobApplication).filter(
        JobApplication.id == app_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if not application.interviews:
        raise HTTPException(status_code=404, detail="No interviews found")
    
    # Generate calendar header
    ical_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//SkillForge Global//Job Tracker//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
"""
    
    # Add each interview as an event
    for interview in application.interviews:
        try:
            interview_date = datetime.fromisoformat(interview['date'].replace('Z', '+00:00'))
            end_date = interview_date + timedelta(hours=1)
            
            dtstart = interview_date.strftime('%Y%m%dT%H%M%SZ')
            dtend = end_date.strftime('%Y%m%dT%H%M%SZ')
            dtstamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
            
            summary = f"Interview: {application.position_title} at {application.company_name}"
            description = f"Interview Type: {interview['type']}\\nInterviewer: {interview.get('interviewer', 'TBD')}"
            uid = f"interview-{application.id}-{interview_date.timestamp()}@skillforge.com"
            
            ical_content += f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{summary}
DESCRIPTION:{description}
LOCATION:{application.location or 'Virtual'}
STATUS:CONFIRMED
END:VEVENT
"""
        except Exception as e:
            print(f"Error processing interview: {e}")
            continue
    
    ical_content += "END:VCALENDAR"
    
    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=interviews-{application.company_name}.ics"
        }
    )


@router.get("/upcoming-interviews")
async def get_upcoming_interviews_ical(
    days: int = 30,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download all upcoming interviews as iCal file"""
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.interviews.isnot(None)
    ).all()
    
    now = datetime.utcnow()
    future_date = now + timedelta(days=days)
    
    # Generate calendar header
    ical_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//SkillForge Global//Job Tracker//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
"""
    
    interview_count = 0
    for app in applications:
        if not app.interviews:
            continue
        
        for interview in app.interviews:
            try:
                interview_date = datetime.fromisoformat(interview['date'].replace('Z', '+00:00'))
                
                # Only include upcoming interviews
                if not (now <= interview_date <= future_date):
                    continue
                
                end_date = interview_date + timedelta(hours=1)
                dtstart = interview_date.strftime('%Y%m%dT%H%M%SZ')
                dtend = end_date.strftime('%Y%m%dT%H%M%SZ')
                dtstamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
                
                summary = f"Interview: {app.position_title} at {app.company_name}"
                description = f"Type: {interview['type']}\\nInterviewer: {interview.get('interviewer', 'TBD')}\\nNotes: {interview.get('notes', 'None')}"
                uid = f"interview-{app.id}-{interview_date.timestamp()}@skillforge.com"
                
                ical_content += f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{summary}
DESCRIPTION:{description}
LOCATION:{app.location or 'Virtual'}
STATUS:CONFIRMED
BEGIN:VALARM
TRIGGER:-PT1H
DESCRIPTION:Interview in 1 hour
ACTION:DISPLAY
END:VALARM
END:VEVENT
"""
                interview_count += 1
            except Exception as e:
                print(f"Error processing interview: {e}")
                continue
    
    ical_content += "END:VCALENDAR"
    
    if interview_count == 0:
        raise HTTPException(status_code=404, detail="No upcoming interviews found")
    
    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=upcoming-interviews.ics"
        }
    )
