"""
Simplified tests for session recording functionality
"""
import pytest
import io
from datetime import datetime
from app.models.user import User
from app.modelsx.mentor import Mentor, MentorSession, MentorStatus
from app.core.security import get_password_hash


def test_start_recording(client, db_session):
    """Test starting a recording"""
    # Create users
    mentor_user = User(email="mentor@test.com", password_hash=get_password_hash("pass123"))
    student_user = User(email="student@test.com", password_hash=get_password_hash("pass123"))
    db_session.add_all([mentor_user, student_user])
    db_session.commit()
    db_session.refresh(mentor_user)
    db_session.refresh(student_user)
    
    # Create mentor
    mentor = Mentor(
        user_id=mentor_user.id,
        bio="Test bio",
        expertise="python",
        hourly_rate=50.0,
        status=MentorStatus.APPROVED
    )
    db_session.add(mentor)
    db_session.commit()
    db_session.refresh(mentor)
    
    # Create session
    session = MentorSession(
        mentor_id=mentor.id,
        student_id=student_user.id,
        scheduled_at=datetime.utcnow(),
        duration_minutes=60
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    # Login as mentor
    login_response = client.post("/api/v1/auth/login", json={
        "email": "mentor@test.com",
        "password": "pass123"
    })
    assert login_response.status_code == 200
    
    # Start recording
    response = client.post(
        "/api/v1x/recordings/start",
        json={"session_id": session.id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session.id
    assert "recording_started_at" in data


def test_stop_recording_with_file(client, db_session):
    """Test stopping a recording and uploading file"""
    # Create users and session
    mentor_user = User(email="mentor2@test.com", password_hash=get_password_hash("pass123"))
    student_user = User(email="student2@test.com", password_hash=get_password_hash("pass123"))
    db_session.add_all([mentor_user, student_user])
    db_session.commit()
    db_session.refresh(mentor_user)
    db_session.refresh(student_user)
    
    mentor = Mentor(
        user_id=mentor_user.id,
        bio="Test bio",
        expertise="python",
        hourly_rate=50.0,
        status=MentorStatus.APPROVED
    )
    db_session.add(mentor)
    db_session.commit()
    db_session.refresh(mentor)
    
    session = MentorSession(
        mentor_id=mentor.id,
        student_id=student_user.id,
        scheduled_at=datetime.utcnow(),
        duration_minutes=60,
        recording_started_at=datetime.utcnow()
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    # Login as mentor
    client.post("/api/v1/auth/login", json={
        "email": "mentor2@test.com",
        "password": "pass123"
    })
    
    # Upload recording
    fake_file = io.BytesIO(b"fake video data")
    response = client.post(
        "/api/v1x/recordings/stop",
        data={"session_id": str(session.id)},
        files={"file": ("recording.webm", fake_file, "video/webm")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "recording_url" in data
    assert data["session_id"] == session.id


def test_get_recording_metadata(client, db_session):
    """Test getting recording metadata"""
    # Create users and session with recording
    mentor_user = User(email="mentor3@test.com", password_hash=get_password_hash("pass123"))
    student_user = User(email="student3@test.com", password_hash=get_password_hash("pass123"))
    db_session.add_all([mentor_user, student_user])
    db_session.commit()
    db_session.refresh(mentor_user)
    db_session.refresh(student_user)
    
    mentor = Mentor(
        user_id=mentor_user.id,
        bio="Test bio",
        expertise="python",
        hourly_rate=50.0,
        status=MentorStatus.APPROVED
    )
    db_session.add(mentor)
    db_session.commit()
    db_session.refresh(mentor)
    
    session = MentorSession(
        mentor_id=mentor.id,
        student_id=student_user.id,
        scheduled_at=datetime.utcnow(),
        duration_minutes=60,
        recording_url="session_1_recording.webm",
        recording_duration=3600
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    # Login as student
    client.post("/api/v1/auth/login", json={
        "email": "student3@test.com",
        "password": "pass123"
    })
    
    # Get metadata
    response = client.get(f"/api/v1x/recordings/{session.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session.id
    assert data["recording_url"] == "session_1_recording.webm"
    assert data["recording_duration"] == 3600


def test_unauthorized_access(client, db_session):
    """Test that unauthorized users cannot access recordings"""
    # Create session with different users
    mentor_user = User(email="mentor4@test.com", password_hash=get_password_hash("pass123"))
    student_user = User(email="student4@test.com", password_hash=get_password_hash("pass123"))
    other_user = User(email="other@test.com", password_hash=get_password_hash("pass123"))
    db_session.add_all([mentor_user, student_user, other_user])
    db_session.commit()
    db_session.refresh(mentor_user)
    db_session.refresh(student_user)
    db_session.refresh(other_user)
    
    mentor = Mentor(
        user_id=mentor_user.id,
        bio="Test bio",
        expertise="python",
        hourly_rate=50.0,
        status=MentorStatus.APPROVED
    )
    db_session.add(mentor)
    db_session.commit()
    db_session.refresh(mentor)
    
    session = MentorSession(
        mentor_id=mentor.id,
        student_id=student_user.id,
        scheduled_at=datetime.utcnow(),
        duration_minutes=60
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    # Login as other user (not part of session)
    client.post("/api/v1/auth/login", json={
        "email": "other@test.com",
        "password": "pass123"
    })
    
    # Try to start recording
    response = client.post(
        "/api/v1x/recordings/start",
        json={"session_id": session.id}
    )
    
    assert response.status_code == 403
