"""
Tests for session recording functionality
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from pathlib import Path
import io

from app.main import app
from app.core.db import SessionLocal, Base, engine
from app.models.user import User
from app.modelsx.mentor import MentorSession


@pytest.fixture(scope="module")
def client():
    """Create test client"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Create database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_users(db_session):
    """Create test users (mentor and student)"""
    # Create mentor
    mentor = User(
        email="mentor@test.com",
        password_hash="hashed_password_123"
    )
    db_session.add(mentor)
    
    # Create student
    student = User(
        email="student@test.com",
        password_hash="hashed_password_456"
    )
    db_session.add(student)
    
    db_session.commit()
    db_session.refresh(mentor)
    db_session.refresh(student)
    
    return {"mentor": mentor, "student": student}


@pytest.fixture
def test_session(db_session, test_users):
    """Create test mentor session"""
    # First create a Mentor record for the mentor user
    from app.modelsx.mentor import Mentor
    mentor = Mentor(
        user_id=test_users["mentor"].id,
        bio="Test mentor bio",
        expertise="python-ai,fullstack",
        hourly_rate=50.0
    )
    db_session.add(mentor)
    db_session.commit()
    db_session.refresh(mentor)
    
    # Now create the session
    session = MentorSession(
        mentor_id=mentor.id,
        student_id=test_users["student"].id,
        scheduled_at=datetime.now(),
        duration_minutes=60,
        status="confirmed",
        topic="Python Testing"
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def auth_headers_mentor(client, test_users):
    """Get authentication headers for mentor"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "mentor@test.com",
            "password": "password123"
        }
    )
    # For testing, we'll simulate authenticated user
    return {"X-User-ID": str(test_users["mentor"].id)}


@pytest.fixture
def auth_headers_student(client, test_users):
    """Get authentication headers for student"""
    return {"X-User-ID": str(test_users["student"].id)}


def test_start_recording(client, test_session, auth_headers_mentor):
    """Test starting a recording"""
    response = client.post(
        "/api/v1x/recordings/start",
        json={"session_id": test_session.id},
        headers=auth_headers_mentor
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == test_session.id
    assert data["message"] == "Recording started"
    assert "recording_started_at" in data


def test_start_recording_unauthorized(client, test_session):
    """Test starting recording without authentication"""
    response = client.post(
        "/api/v1x/recordings/start",
        json={"session_id": test_session.id}
    )
    
    assert response.status_code == 401


def test_start_recording_not_participant(client, test_session, db_session):
    """Test starting recording as non-participant"""
    # Create another user who is not part of the session
    other_user = User(
        email="other@test.com",
        password_hash="hashed_password_789"
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)
    
    headers = {"X-User-ID": str(other_user.id)}
    
    response = client.post(
        "/api/v1x/recordings/start",
        json={"session_id": test_session.id},
        headers=headers
    )
    
    assert response.status_code == 403


def test_stop_recording_with_file(client, test_session, auth_headers_mentor, db_session):
    """Test stopping recording and uploading file"""
    # First start recording
    client.post(
        "/api/v1x/recordings/start",
        json={"session_id": test_session.id},
        headers=auth_headers_mentor
    )
    
    # Create fake video file
    fake_video = io.BytesIO(b"fake video content")
    fake_video.name = "test_recording.webm"
    
    # Stop recording with file upload
    response = client.post(
        "/api/v1x/recordings/stop",
        data={"session_id": str(test_session.id)},
        files={"file": ("recording.webm", fake_video, "video/webm")},
        headers=auth_headers_mentor
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == test_session.id
    assert data["message"] == "Recording saved"
    assert "recording_url" in data
    assert data["recording_url"].endswith(".webm")
    
    # Verify file was saved
    recordings_dir = Path("backend/recordings")
    assert recordings_dir.exists()
    
    # Check database was updated
    db_session.refresh(test_session)
    assert test_session.recording_url is not None
    assert test_session.recording_duration is not None


def test_stop_recording_no_file(client, test_session, auth_headers_mentor):
    """Test stopping recording without uploading file"""
    # First start recording
    client.post(
        "/api/v1x/recordings/start",
        json={"session_id": test_session.id},
        headers=auth_headers_mentor
    )
    
    # Try to stop without file
    response = client.post(
        "/api/v1x/recordings/stop",
        data={"session_id": str(test_session.id)},
        headers=auth_headers_mentor
    )
    
    assert response.status_code == 400


def test_get_recording_metadata(client, test_session, auth_headers_student, db_session):
    """Test getting recording metadata"""
    # Setup: Add recording data to session
    test_session.recording_url = "session_1_recording.webm"
    test_session.recording_duration = 3600
    test_session.recording_started_at = datetime.now()
    db_session.commit()
    
    response = client.get(
        f"/api/v1x/recordings/{test_session.id}",
        headers=auth_headers_student
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == test_session.id
    assert data["recording_url"] == "session_1_recording.webm"
    assert data["recording_duration"] == 3600
    assert "recording_started_at" in data


def test_get_recording_metadata_no_recording(client, test_session, auth_headers_mentor):
    """Test getting metadata when no recording exists"""
    response = client.get(
        f"/api/v1x/recordings/{test_session.id}",
        headers=auth_headers_mentor
    )
    
    assert response.status_code == 404


def test_download_recording(client, test_session, auth_headers_mentor, db_session):
    """Test downloading recording file"""
    # Setup: Create actual recording file
    recordings_dir = Path("backend/recordings")
    recordings_dir.mkdir(exist_ok=True)
    
    recording_file = recordings_dir / "test_download.webm"
    recording_file.write_bytes(b"test video content")
    
    # Update session with recording
    test_session.recording_url = "test_download.webm"
    db_session.commit()
    
    # Download
    response = client.get(
        f"/api/v1x/recordings/{test_session.id}/download",
        headers=auth_headers_mentor
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "video/webm"
    assert b"test video content" in response.content
    
    # Cleanup
    recording_file.unlink()


def test_download_recording_file_not_found(client, test_session, auth_headers_student, db_session):
    """Test downloading when file doesn't exist on disk"""
    # Setup: Set recording URL but don't create file
    test_session.recording_url = "nonexistent_file.webm"
    db_session.commit()
    
    response = client.get(
        f"/api/v1x/recordings/{test_session.id}/download",
        headers=auth_headers_student
    )
    
    assert response.status_code == 404


def test_recording_permissions(client, test_session, db_session):
    """Test that only session participants can access recordings"""
    # Create non-participant user
    other_user = User(
        email="outsider@test.com",
        password_hash="hashed_password_xyz"
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)
    
    headers = {"X-User-ID": str(other_user.id)}
    
    # Try to start recording
    response = client.post(
        "/api/v1x/recordings/start",
        json={"session_id": test_session.id},
        headers=headers
    )
    assert response.status_code == 403
    
    # Try to get metadata
    response = client.get(
        f"/api/v1x/recordings/{test_session.id}",
        headers=headers
    )
    assert response.status_code == 403
    
    # Try to download
    response = client.get(
        f"/api/v1x/recordings/{test_session.id}/download",
        headers=headers
    )
    assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
