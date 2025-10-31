"""
File upload endpoints for mentor chat
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pathlib import Path
import os
import uuid
from datetime import datetime
from typing import List

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.mentor import MentorSession
from app.modelsx.chat_file import MentorChatFile

router = APIRouter(prefix="/chat/files", tags=["chat-files"])

# File upload configuration
UPLOAD_DIR = Path("./app/uploads/chat_files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
    'document': ['.pdf', '.doc', '.docx', '.txt', '.md'],
    'archive': ['.zip', '.rar'],
    'code': ['.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.json']
}

ALL_ALLOWED_EXTENSIONS = []
for exts in ALLOWED_EXTENSIONS.values():
    ALL_ALLOWED_EXTENSIONS.extend(exts)


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    ext = Path(filename).suffix.lower()
    return ext in ALL_ALLOWED_EXTENSIONS


def get_file_category(filename: str) -> str:
    """Determine file category"""
    ext = Path(filename).suffix.lower()
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return category
    return 'other'


@router.post("/upload")
async def upload_chat_file(
    session_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a file to a chat session.
    Returns file metadata for the client to display.
    """
    # Verify session exists and user is participant
    session = db.query(MentorSession).filter(
        MentorSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if user is participant (student or mentor)
    from app.modelsx.mentor import Mentor
    mentor = db.query(Mentor).filter(Mentor.id == session.mentor_id).first()
    is_participant = (
        current_user.id == session.student_id or 
        (mentor and current_user.id == mentor.user_id)
    )
    
    if not is_participant:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Validate file
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(ALL_ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Create database record
    chat_file = MentorChatFile(
        session_id=session_id,
        sender_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        mime_type=file.content_type or 'application/octet-stream'
    )
    
    db.add(chat_file)
    db.commit()
    db.refresh(chat_file)
    
    return {
        "id": chat_file.id,
        "filename": chat_file.filename,
        "original_filename": chat_file.original_filename,
        "file_size": chat_file.file_size,
        "mime_type": chat_file.mime_type,
        "category": get_file_category(file.filename),
        "uploaded_at": chat_file.uploaded_at.isoformat(),
        "sender_id": chat_file.sender_id,
        "download_url": f"/api/v1x/chat/files/{chat_file.id}/download"
    }


@router.get("/{file_id}/download")
async def download_chat_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a chat file"""
    from fastapi.responses import FileResponse
    
    # Get file record
    chat_file = db.query(MentorChatFile).filter(
        MentorChatFile.id == file_id
    ).first()
    
    if not chat_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Verify user is participant
    session = db.query(MentorSession).filter(
        MentorSession.id == chat_file.session_id
    ).first()
    
    from app.modelsx.mentor import Mentor
    mentor = db.query(Mentor).filter(Mentor.id == session.mentor_id).first()
    is_participant = (
        current_user.id == session.student_id or 
        (mentor and current_user.id == mentor.user_id)
    )
    
    if not is_participant:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check file exists
    file_path = Path(chat_file.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=str(file_path),
        filename=chat_file.original_filename,
        media_type=chat_file.mime_type
    )


@router.get("/session/{session_id}")
async def get_session_files(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all files uploaded to a session"""
    # Verify session and participation
    session = db.query(MentorSession).filter(
        MentorSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    from app.modelsx.mentor import Mentor
    mentor = db.query(Mentor).filter(Mentor.id == session.mentor_id).first()
    is_participant = (
        current_user.id == session.student_id or 
        (mentor and current_user.id == mentor.user_id)
    )
    
    if not is_participant:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get files
    files = db.query(MentorChatFile).filter(
        MentorChatFile.session_id == session_id
    ).order_by(MentorChatFile.uploaded_at.desc()).all()
    
    return {
        "session_id": session_id,
        "files": [
            {
                "id": f.id,
                "filename": f.filename,
                "original_filename": f.original_filename,
                "file_size": f.file_size,
                "mime_type": f.mime_type,
                "category": get_file_category(f.original_filename),
                "uploaded_at": f.uploaded_at.isoformat(),
                "sender_id": f.sender_id,
                "download_url": f"/api/v1x/chat/files/{f.id}/download"
            }
            for f in files
        ]
    }


@router.delete("/{file_id}")
async def delete_chat_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat file (sender only)"""
    # Get file record
    chat_file = db.query(MentorChatFile).filter(
        MentorChatFile.id == file_id
    ).first()
    
    if not chat_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Only sender can delete
    if chat_file.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the sender can delete this file")
    
    # Delete file from disk
    file_path = Path(chat_file.file_path)
    if file_path.exists():
        os.remove(file_path)
    
    # Delete from database
    db.delete(chat_file)
    db.commit()
    
    return {"success": True, "message": "File deleted"}
