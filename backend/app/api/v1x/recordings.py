"""
Session Recording API
Handles starting, stopping, and downloading mentor session recordings
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import text
from typing import Optional
from datetime import datetime
from pathlib import Path
import shutil

from app.core.db import SessionLocal
from app.core.security import get_current_user

router = APIRouter(prefix="/recordings", tags=["recordings"])

# Recording storage directory
RECORDINGS_DIR = Path(__file__).parent.parent.parent / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)

class RecordingStart(BaseModel):
    session_id: int

class RecordingStop(BaseModel):
    session_id: int
    duration: int  # in seconds

@router.post("/start")
def start_recording(data: RecordingStart, user = Depends(get_current_user)):
    """Mark session recording as started"""
    db = SessionLocal()
    try:
        # Check if session exists and user has permission
        session = db.execute(
            text("""
                SELECT id, mentor_id, student_id
                FROM mentor_sessions
                WHERE id=:sid
            """),
            {"sid": data.session_id}
        ).mappings().first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check user is mentor or student
        user_id = user.get("id") if isinstance(user, dict) else user.id
        if user_id not in [session["mentor_id"], session["student_id"]]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Update session with recording started timestamp
        db.execute(
            text("""
                UPDATE mentor_sessions
                SET recording_started_at=:now
                WHERE id=:sid
            """),
            {"sid": data.session_id, "now": datetime.utcnow()}
        )
        db.commit()
        
        return {
            "ok": True,
            "session_id": data.session_id,
            "message": "Recording started"
        }
        
    finally:
        db.close()

@router.post("/stop")
async def stop_recording(
    session_id: int,
    duration: int,
    file: UploadFile = File(...),
    user = Depends(get_current_user)
):
    """Upload and save recording file"""
    db = SessionLocal()
    try:
        # Check session exists and user has permission
        session = db.execute(
            text("""
                SELECT id, mentor_id, student_id
                FROM mentor_sessions
                WHERE id=:sid
            """),
            {"sid": session_id}
        ).mappings().first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        user_id = user.get("id") if isinstance(user, dict) else user.id
        if user_id not in [session["mentor_id"], session["student_id"]]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Generate filename
        filename = f"session_{session_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.webm"
        file_path = RECORDINGS_DIR / filename
        
        # Save file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update session with recording URL and duration
        db.execute(
            text("""
                UPDATE mentor_sessions
                SET recording_url=:url, recording_duration=:duration
                WHERE id=:sid
            """),
            {"sid": session_id, "url": filename, "duration": duration}
        )
        db.commit()
        
        return {
            "ok": True,
            "session_id": session_id,
            "recording_url": f"/api/v1x/recordings/{session_id}/download",
            "duration": duration
        }
        
    finally:
        db.close()

@router.get("/{session_id}")
def get_recording_info(session_id: int, user = Depends(get_current_user)):
    """Get recording information for a session"""
    db = SessionLocal()
    try:
        session = db.execute(
            text("""
                SELECT id, recording_url, recording_duration, recording_started_at
                FROM mentor_sessions
                WHERE id=:sid
            """),
            {"sid": session_id}
        ).mappings().first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not session["recording_url"]:
            return {
                "has_recording": False,
                "session_id": session_id
            }
        
        return {
            "has_recording": True,
            "session_id": session_id,
            "recording_url": f"/api/v1x/recordings/{session_id}/download",
            "duration": session["recording_duration"],
            "started_at": session["recording_started_at"]
        }
        
    finally:
        db.close()

@router.get("/{session_id}/download")
def download_recording(session_id: int, user = Depends(get_current_user)):
    """Download recording file"""
    db = SessionLocal()
    try:
        session = db.execute(
            text("""
                SELECT id, mentor_id, student_id, recording_url
                FROM mentor_sessions
                WHERE id=:sid
            """),
            {"sid": session_id}
        ).mappings().first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check permission
        user_id = user.get("id") if isinstance(user, dict) else user.id
        if user_id not in [session["mentor_id"], session["student_id"]]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        if not session["recording_url"]:
            raise HTTPException(status_code=404, detail="No recording available")
        
        file_path = RECORDINGS_DIR / session["recording_url"]
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Recording file not found")
        
        return FileResponse(
            file_path,
            media_type="video/webm",
            filename=session["recording_url"]
        )
        
    finally:
        db.close()
