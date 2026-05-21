import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.main import app
from app.core.db import SessionLocal
from app.core.security import create_access_token
from app.models.user import User, UserRole
from app.modelsx.mentor import Mentor, MentorStatus, MentorSession, SessionStatus


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture()
def db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


def make_user(db: Session, email: str, role: UserRole = UserRole.USER) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, password_hash="dummy", role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.role = role
        db.commit()
    return user


def auth_headers(user_id: int):
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}


def seed_mentor_and_session(db: Session, user_id: int) -> tuple[int, int]:
    mentor = db.query(Mentor).filter(Mentor.user_id == user_id).first()
    if not mentor:
        mentor = Mentor(
            user_id=user_id,
            bio="Test mentor",
            expertise="python-ai,web-dev",
            hourly_rate=50.0,
            status=MentorStatus.PENDING,
        )
        db.add(mentor)
        db.commit()
        db.refresh(mentor)
    # Create a session
    session = MentorSession(
        mentor_id=mentor.id,
        student_id=user_id,
        topic="Testing session",
        scheduled_at=datetime.utcnow() + timedelta(days=1),
        duration_minutes=30,
        status=SessionStatus.PENDING,
        price=0.0,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return mentor.id, session.id


def test_admin_dashboard_stats_requires_admin(client, db):
    admin = make_user(db, "admin@example.com", UserRole.ADMIN)
    res = client.get("/api/v1x/admin/dashboard/stats", headers=auth_headers(admin.id))
    assert res.status_code == 200
    body = res.json()
    assert "total_users" in body
    assert "total_sessions" in body

    # Non-admin should be forbidden
    user = make_user(db, "user@example.com", UserRole.USER)
    res2 = client.get("/api/v1x/admin/dashboard/stats", headers=auth_headers(user.id))
    assert res2.status_code == 403


def test_admin_users_list_and_role_update(client, db):
    superadmin = make_user(db, "super@example.com", UserRole.SUPERADMIN)
    u = make_user(db, "change-role@example.com", UserRole.USER)

    # List users (admin permitted)
    res_list = client.get("/api/v1x/admin/users?search=example.com", headers=auth_headers(superadmin.id))
    assert res_list.status_code == 200
    assert isinstance(res_list.json(), list)

    # Update role (superadmin only)
    res_patch = client.patch(
        f"/api/v1x/admin/users/{u.id}/role",
        headers=auth_headers(superadmin.id),
        json={"role": "mentor"},
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["new_role"] == "mentor"

    # Non-superadmin cannot change roles
    admin = make_user(db, "admin2@example.com", UserRole.ADMIN)
    res_forbidden = client.patch(
        f"/api/v1x/admin/users/{u.id}/role",
        headers=auth_headers(admin.id),
        json={"role": "admin"},
    )
    assert res_forbidden.status_code == 403


def test_admin_mentor_applications_and_status_update(client, db):
    admin = make_user(db, "admin3@example.com", UserRole.ADMIN)
    mentor_user = make_user(db, "mentor@apps.example.com", UserRole.USER)
    mentor_id, _ = seed_mentor_and_session(db, mentor_user.id)

    # List applications
    res_apps = client.get("/api/v1x/admin/mentors/applications", headers=auth_headers(admin.id))
    assert res_apps.status_code == 200
    apps = res_apps.json().get("applications", [])
    assert isinstance(apps, list)

    # Approve mentor
    res_approve = client.patch(
        f"/api/v1x/admin/mentors/{mentor_id}/status",
        headers=auth_headers(admin.id),
        json={"status": "approved"},
    )
    assert res_approve.status_code == 200
    assert "updated" in res_approve.json().get("message", "").lower()


def test_admin_sessions_list_and_status_update(client, db):
    admin = make_user(db, "admin4@example.com", UserRole.ADMIN)
    student = make_user(db, "student@apps.example.com", UserRole.USER)
    mentor_id, session_id = seed_mentor_and_session(db, student.id)

    # List sessions
    res_list = client.get("/api/v1x/mentors/admin/sessions", headers=auth_headers(admin.id))
    assert res_list.status_code == 200
    sessions = res_list.json().get("sessions", [])
    assert isinstance(sessions, list)

    # Cancel session
    res_cancel = client.patch(
        f"/api/v1x/mentors/sessions/{session_id}",
        headers=auth_headers(admin.id),
        json={"status": "cancelled", "reason": "testing"},
    )
    assert res_cancel.status_code == 200
    assert "updated" in res_cancel.json().get("message", "").lower()


def test_admin_audit_logs_access(client, db):
    admin = make_user(db, "admin5@example.com", UserRole.ADMIN)
    res_logs = client.get("/api/v1x/admin/logs?limit=5", headers=auth_headers(admin.id))
    assert res_logs.status_code == 200
    data = res_logs.json()
    assert "logs" in data
    assert "total" in data
