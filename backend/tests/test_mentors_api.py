"""Modern mentor API test suite aligned with current routers and schemas.

Covers:
 - Eligibility (eligible / not eligible)
 - Application flow
 - Profile get / update
 - Search and get-by-id
 - Session booking, listing (student & mentor), status update
 - Availability add & list
 - Review submission and listing
"""

from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.main import app
from app.core.db import SessionLocal
from app.core.security import create_access_token
from app.models.user import User, UserRole
from app.models.progress import Progress
from app.models.quiz_attempt import QuizAttempt
from app.modelsx.mentor import Mentor, MentorSession, MentorStatus, SessionStatus


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def db() -> Session:
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


def make_user(db: Session, email: str, role: UserRole = UserRole.USER) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, password_hash="test", role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.role = role
        db.commit()
    return user


def auth(email: str, db: Session) -> dict:
    user = db.query(User).filter(User.email == email).first()
    assert user, f"User {email} not found"
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def seed_eligibility(db: Session, user_id: int):
    # Progress: need >=3 modules in a valid path (python-ai)
    for i in range(1, 4):
        db.add(Progress(user_id=user_id, path="python-ai", module_id=f"mod{i}"))
    # Quiz attempts: average >= 80%
    db.add(QuizAttempt(user_id=user_id, path="python-ai", score=90, total=100, passed=True))
    db.add(QuizAttempt(user_id=user_id, path="python-ai", score=85, total=100, passed=True))
    db.commit()


def approve_mentor(db: Session, mentor: Mentor):
    mentor.status = MentorStatus.APPROVED
    mentor.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(mentor)


class TestEligibility:
    def test_not_eligible(self, client, db):
        u = make_user(db, "not-eligible@example.com")
        res = client.get("/api/v1x/mentors/eligibility", headers=auth(u.email, db))
        assert res.status_code == 200
        body = res.json()
        assert body["eligible"] is False
        assert any("Must complete" in r for r in body["reasons"]) or any("average" in r for r in body["reasons"])  # flexible

    def test_eligible(self, client, db):
        u = make_user(db, "eligible@example.com")
        seed_eligibility(db, u.id)
        res = client.get("/api/v1x/mentors/eligibility", headers=auth(u.email, db))
        assert res.status_code == 200
        body = res.json()
        assert body["eligible"] is True


class TestApplicationAndProfile:
    def test_apply(self, client, db):
        u = make_user(db, "apply-user@example.com")
        seed_eligibility(db, u.id)
        payload = {
            "bio": "Experienced engineer with a passion for teaching others FastAPI and scalable Python." ,
            "expertise": "python-ai,web-dev",
            "hourly_rate": 45.0
        }
        res = client.post("/api/v1x/mentors/apply", json=payload, headers=auth(u.email, db))
        assert res.status_code == 201
        body = res.json()
        assert body["status"] == "pending"
        assert body["expertise"] == payload["expertise"]

    def test_get_and_update_profile(self, client, db):
        # Create mentor directly
        u = make_user(db, "mentor-profile@example.com")
        seed_eligibility(db, u.id)
        mentor = Mentor(user_id=u.id, bio="Initial bio that is long enough to pass.", expertise="python-ai,web-dev", hourly_rate=30.0, status=MentorStatus.PENDING)
        db.add(mentor)
        db.commit(); db.refresh(mentor)
        # Get profile (should be pending)
        res_get = client.get("/api/v1x/mentors/me", headers=auth(u.email, db))
        assert res_get.status_code == 200
        # Update
        res_patch = client.patch("/api/v1x/mentors/me", headers=auth(u.email, db), json={"bio": "Updated mentor biography with sufficient length for validation.", "hourly_rate": 55.0})
        assert res_patch.status_code == 200
        body = res_patch.json()
        assert body["bio"].startswith("Updated mentor biography")
        assert body["hourly_rate"] == 55.0


class TestSearch:
    def test_search_and_get_by_id(self, client, db):
        # Seed approved mentor
        u = make_user(db, "search-mentor@example.com")
        seed_eligibility(db, u.id)
        mentor = Mentor(user_id=u.id, bio="Searchable mentor with expertise.", expertise="python-ai,web-dev", hourly_rate=35.0, status=MentorStatus.PENDING)
        db.add(mentor); db.commit(); db.refresh(mentor)
        approve_mentor(db, mentor)
        res_search = client.get("/api/v1x/mentors/search?expertise=python-ai")
        assert res_search.status_code == 200
        data = res_search.json()
        assert any(m["id"] == mentor.id for m in data)
        res_get = client.get(f"/api/v1x/mentors/{mentor.id}")
        assert res_get.status_code == 200
        assert res_get.json()["id"] == mentor.id


class TestSessions:
    def test_book_list_update_sessions(self, client, db):
        student = make_user(db, "session-student@example.com")
        mentor_user = make_user(db, "session-mentor@example.com")
        seed_eligibility(db, mentor_user.id)
        mentor = Mentor(user_id=mentor_user.id, bio="Session mentor bio long enough.", expertise="python-ai,web-dev", hourly_rate=40.0, status=MentorStatus.PENDING)
        db.add(mentor); db.commit(); db.refresh(mentor); approve_mentor(db, mentor)
        # Book session
        scheduled_at = datetime.utcnow() + timedelta(days=1)
        book_payload = {
            "mentor_id": mentor.id,
            "topic": "Scaling FastAPI",
            "description": "Discuss async patterns and optimization.",
            "scheduled_at": scheduled_at.isoformat(),
            "duration_minutes": 60
        }
        res_book = client.post("/api/v1x/mentors/sessions", json=book_payload, headers=auth(student.email, db))
        assert res_book.status_code == 201
        session_id = res_book.json()["id"]
        # List as student
        res_list_student = client.get("/api/v1x/mentors/sessions/my", headers=auth(student.email, db))
        assert res_list_student.status_code == 200
        assert isinstance(res_list_student.json()["sessions"], list)
        # List as mentor
        res_list_mentor = client.get("/api/v1x/mentors/sessions/my?as_mentor=true", headers=auth(mentor_user.email, db))
        assert res_list_mentor.status_code == 200
        # Update status (confirm) as mentor
        res_confirm = client.patch(f"/api/v1x/mentors/sessions/{session_id}", json={"status": "confirmed"}, headers=auth(mentor_user.email, db))
        assert res_confirm.status_code == 200
        assert res_confirm.json()["session"]["status"] == "confirmed"


class TestAvailability:
    def test_add_and_list(self, client, db):
        u = make_user(db, "avail-mentor@example.com")
        seed_eligibility(db, u.id)
        mentor = Mentor(user_id=u.id, bio="Availability mentor bio long enough.", expertise="python-ai,web-dev", hourly_rate=50.0, status=MentorStatus.PENDING)
        db.add(mentor); db.commit(); db.refresh(mentor); approve_mentor(db, mentor)
        payload = {"day_of_week": 1, "start_time": "14:00", "end_time": "15:00", "timezone": "UTC"}
        res_add = client.post("/api/v1x/mentors/availability", json=payload, headers=auth(u.email, db))
        assert res_add.status_code == 201
        res_list = client.get(f"/api/v1x/mentors/availability/{mentor.id}")
        assert res_list.status_code == 200
        assert isinstance(res_list.json()["slots"], list)


class TestReviews:
    def test_submit_and_list_reviews(self, client, db):
        student = make_user(db, "review-student@example.com")
        mentor_user = make_user(db, "review-mentor@example.com")
        seed_eligibility(db, mentor_user.id)
        mentor = Mentor(user_id=mentor_user.id, bio="Review mentor bio long enough.", expertise="python-ai,web-dev", hourly_rate=45.0, status=MentorStatus.PENDING)
        db.add(mentor); db.commit(); db.refresh(mentor); approve_mentor(db, mentor)
        # Create completed session directly
        session = MentorSession(mentor_id=mentor.id, student_id=student.id, topic="Finished Session", scheduled_at=datetime.utcnow() - timedelta(days=1), duration_minutes=30, status=SessionStatus.COMPLETED, price=0.0)
        db.add(session); db.commit(); db.refresh(session)
        review_payload = {"session_id": session.id, "rating": 5, "review_text": "Great session", "tags": "helpful,patient"}
        res_review = client.post("/api/v1x/mentors/reviews", json=review_payload, headers=auth(student.email, db))
        assert res_review.status_code == 201
        assert res_review.json()["rating"] == 5
        res_list = client.get(f"/api/v1x/mentors/reviews/{mentor.id}")
        assert res_list.status_code == 200
        body = res_list.json()
        assert body["total"] >= 1
        assert body["average_rating"] >= 5.0
