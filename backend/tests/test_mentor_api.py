"""
Tests for Mentor System API endpoints
"""
import pytest
from datetime import datetime, timedelta
from app.models.user import User
from app.modelsx.mentor import Mentor, MentorSession
from app.models.progress import Progress
from app.modelsx.quiz import QuizAttempt
from app.core.security import get_password_hash

# Test data
TEST_USER_EMAIL = "student@test.com"
TEST_MENTOR_EMAIL = "mentor@test.com"
TEST_PASSWORD = "testpass123"


@pytest.fixture
def test_student(db_session):
    """Create test student user"""
    user = User(
        email=TEST_USER_EMAIL,
        hashed_password=get_password_hash(TEST_PASSWORD),
        full_name="Test Student"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def eligible_student(db_session):
    """Create student eligible to become mentor"""
    # Create user
    user = User(
        email="eligible@test.com",
        hashed_password=get_password_hash(TEST_PASSWORD),
        full_name="Eligible Student"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Add completed progress (path completed)
    progress = Progress(
        user_id=user.id,
        module_id=1,
        completed=True,
        completed_at=datetime.utcnow()
    )
    db_session.add(progress)
    
    # Add quiz attempts with high scores (>80% average)
    quiz1 = QuizAttempt(
        user_id=user.id,
        quiz_id=1,
        score=90.0,
        max_score=100.0,
        passed=True,
        completed_at=datetime.utcnow()
    )
    quiz2 = QuizAttempt(
        user_id=user.id,
        quiz_id=2,
        score=85.0,
        max_score=100.0,
        passed=True,
        completed_at=datetime.utcnow()
    )
    db_session.add_all([quiz1, quiz2])
    db_session.commit()
    
    return user


@pytest.fixture
def test_mentor(db_session):
    """Create test mentor"""
    # Create user
    user = User(
        email=TEST_MENTOR_EMAIL,
        hashed_password=get_password_hash(TEST_PASSWORD),
        full_name="Test Mentor"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create mentor profile
    mentor = Mentor(
        user_id=user.id,
        bio="Experienced developer",
        expertise=["Python", "FastAPI"],
        hourly_rate=50.0,
        status="approved",
        average_rating=4.5,
        total_sessions=10
    )
    db_session.add(mentor)
    db_session.commit()
    db_session.refresh(mentor)
    
    return mentor


class TestMentorEligibility:
    """Test mentor eligibility checks"""
    
    def test_check_eligibility_not_eligible(self, client, test_student):
        """Test eligibility check for non-eligible user"""
        # Login first
        login_response = client.post("/api/v1/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        
        # Check eligibility
        response = client.get("/api/v1x/mentors/eligibility")
        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] is False
        assert "reasons" in data
    
    def test_check_eligibility_eligible(self, client, eligible_student):
        """Test eligibility check for eligible user"""
        # Login as eligible student
        login_response = client.post("/api/v1/auth/login", json={
            "email": "eligible@test.com",
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        
        # Check eligibility
        response = client.get("/api/v1x/mentors/eligibility")
        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] is True


class TestMentorApplication:
    """Test mentor application process"""
    
    @pytest.mark.asyncio
    async def test_apply_not_eligible(self, test_student, auth_headers):
        """Test applying when not eligible"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1x/mentors/apply",
                headers=auth_headers,
                json={
                    "bio": "I want to be a mentor",
                    "expertise": ["Python"],
                    "hourly_rate": 50.0
                }
            )
            assert response.status_code == 400
            assert "not eligible" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_apply_eligible(self, eligible_student):
        """Test applying when eligible"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Login
            login_response = await client.post(
                "/api/v1/auth/login",
                json={"email": "eligible@test.com", "password": TEST_PASSWORD}
            )
            token = login_response.cookies.get("token")
            headers = {"Cookie": f"token={token}"}
            
            # Apply
            response = await client.post(
                "/api/v1x/mentors/apply",
                headers=headers,
                json={
                    "bio": "I want to help others learn Python",
                    "expertise": ["Python", "FastAPI"],
                    "hourly_rate": 40.0
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "pending"
            assert data["bio"] == "I want to help others learn Python"


class TestMentorProfile:
    """Test mentor profile endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_own_profile(self, test_mentor):
        """Test getting own mentor profile"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Login
            login_response = await client.post(
                "/api/v1/auth/login",
                json={"email": TEST_MENTOR_EMAIL, "password": TEST_PASSWORD}
            )
            token = login_response.cookies.get("token")
            headers = {"Cookie": f"token={token}"}
            
            # Get profile
            response = await client.get(
                "/api/v1x/mentors/me",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == test_mentor.user_id
            assert data["bio"] == "Experienced developer"
    
    @pytest.mark.asyncio
    async def test_update_profile(self, test_mentor):
        """Test updating mentor profile"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Login
            login_response = await client.post(
                "/api/v1/auth/login",
                json={"email": TEST_MENTOR_EMAIL, "password": TEST_PASSWORD}
            )
            token = login_response.cookies.get("token")
            headers = {"Cookie": f"token={token}"}
            
            # Update
            response = await client.patch(
                "/api/v1x/mentors/me",
                headers=headers,
                json={
                    "bio": "Updated bio",
                    "hourly_rate": 60.0
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["bio"] == "Updated bio"
            assert data["hourly_rate"] == 60.0


class TestMentorSearch:
    """Test mentor search functionality"""
    
    @pytest.mark.asyncio
    async def test_search_mentors(self, test_mentor):
        """Test searching for mentors"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1x/mentors/search")
            assert response.status_code == 200
            data = response.json()
            assert len(data) > 0
            assert data[0]["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_search_by_expertise(self, test_mentor):
        """Test searching mentors by expertise"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1x/mentors/search",
                params={"expertise": "Python"}
            )
            assert response.status_code == 200
            data = response.json()
            assert all("Python" in m["expertise"] for m in data)
    
    @pytest.mark.asyncio
    async def test_get_mentor_by_id(self, test_mentor):
        """Test getting specific mentor"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(f"/api/v1x/mentors/{test_mentor.id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == test_mentor.id


class TestMentorSessions:
    """Test session booking and management"""
    
    @pytest.mark.asyncio
    async def test_book_session(self, test_student, test_mentor, auth_headers):
        """Test booking a mentor session"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            start_time = datetime.utcnow() + timedelta(days=1)
            response = await client.post(
                "/api/v1x/mentors/sessions",
                headers=auth_headers,
                json={
                    "mentor_id": test_mentor.id,
                    "start_time": start_time.isoformat(),
                    "duration_minutes": 60,
                    "topic": "Learn FastAPI",
                    "notes": "Need help with authentication"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "pending"
            assert data["mentor_id"] == test_mentor.id
    
    @pytest.mark.asyncio
    async def test_get_my_sessions(self, test_student, auth_headers):
        """Test getting user's sessions"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1x/mentors/sessions/my",
                headers=auth_headers
            )
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


class TestMentorAvailability:
    """Test availability management"""
    
    @pytest.mark.asyncio
    async def test_add_availability(self, test_mentor):
        """Test adding availability slot"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Login as mentor
            login_response = await client.post(
                "/api/v1/auth/login",
                json={"email": TEST_MENTOR_EMAIL, "password": TEST_PASSWORD}
            )
            token = login_response.cookies.get("token")
            headers = {"Cookie": f"token={token}"}
            
            # Add availability
            start_time = datetime.utcnow() + timedelta(days=2)
            end_time = start_time + timedelta(hours=2)
            response = await client.post(
                "/api/v1x/mentors/availability",
                headers=headers,
                json={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["is_available"] is True
    
    @pytest.mark.asyncio
    async def test_get_mentor_availability(self, test_mentor):
        """Test getting mentor's availability"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/v1x/mentors/availability/{test_mentor.id}"
            )
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


class TestMentorReviews:
    """Test review system"""
    
    @pytest.mark.asyncio
    async def test_submit_review(self, test_student, test_mentor, auth_headers, test_db):
        """Test submitting a review"""
        # First create a completed session
        db = next(get_db())
        session = MentorSession(
            mentor_id=test_mentor.id,
            student_id=test_student.id,
            start_time=datetime.utcnow() - timedelta(hours=2),
            end_time=datetime.utcnow() - timedelta(hours=1),
            duration_minutes=60,
            status="completed",
            topic="Test Session"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1x/mentors/reviews",
                headers=auth_headers,
                json={
                    "session_id": session.id,
                    "rating": 5,
                    "comment": "Excellent mentor!"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["rating"] == 5
    
    @pytest.mark.asyncio
    async def test_get_mentor_reviews(self, test_mentor):
        """Test getting mentor reviews"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/v1x/mentors/reviews/{test_mentor.id}"
            )
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
