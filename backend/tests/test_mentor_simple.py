"""
Tests for Mentor System API endpoints - Simplified Version
"""
import pytest
from datetime import datetime, timedelta
from app.models.user import User
from app.modelsx.mentor import Mentor, MentorSession
from app.models.progress import Progress
from app.modelsx.quiz import QuizAttempt
from app.core.security import get_password_hash


class TestMentorBasics:
    """Test basic mentor functionality"""
    
    def test_check_eligibility_not_logged_in(self, client):
        """Test eligibility check requires auth"""
        response = client.get("/api/v1x/mentors/eligibility")
        assert response.status_code == 401
    
    def test_search_mentors_public(self, client):
        """Test searching mentors is public"""
        response = client.get("/api/v1x/mentors/search")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_become_mentor_not_logged_in(self, client):
        """Test become mentor requires auth"""
        response = client.post("/api/v1x/mentors/apply", json={
            "bio": "Test bio",
            "expertise": ["Python"],
            "hourly_rate": 50.0
        })
        assert response.status_code == 401


class TestMentorEligibility:
    """Test mentor eligibility checks"""
    
    def test_check_eligibility(self, client, test_user):
        """Test eligibility check for logged-in user"""
        # Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        assert login_response.status_code == 200
        
        # Check eligibility
        response = client.get("/api/v1x/mentors/eligibility")
        # Should return eligibility status
        assert response.status_code in [200, 400]


class TestMentorProfile:
    """Test mentor profile management"""
    
    def test_get_mentor_profile_not_mentor(self, client, test_user):
        """Test getting profile when not a mentor"""
        # Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        assert login_response.status_code == 200
        
        # Get profile (should fail - not a mentor)
        response = client.get("/api/v1x/mentors/me")
        assert response.status_code == 404


class TestMentorSearch:
    """Test mentor search functionality"""
    
    def test_search_all_mentors(self, client):
        """Test searching all mentors"""
        response = client.get("/api/v1x/mentors/search")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_search_by_expertise(self, client):
        """Test searching mentors by expertise"""
        response = client.get("/api/v1x/mentors/search?expertise=Python")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_search_by_rating(self, client):
        """Test searching mentors by minimum rating"""
        response = client.get("/api/v1x/mentors/search?min_rating=4.0")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_search_by_price(self, client):
        """Test searching mentors by maximum price"""
        response = client.get("/api/v1x/mentors/search?max_price=100")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestMentorSessions:
    """Test session booking"""
    
    def test_get_my_sessions_not_logged_in(self, client):
        """Test getting sessions requires auth"""
        response = client.get("/api/v1x/mentors/sessions/my")
        assert response.status_code == 401
    
    def test_get_my_sessions(self, client, test_user):
        """Test getting user's sessions"""
        # Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        assert login_response.status_code == 200
        
        # Get sessions
        response = client.get("/api/v1x/mentors/sessions/my")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestMentorAvailability:
    """Test availability management"""
    
    def test_add_availability_not_logged_in(self, client):
        """Test adding availability requires auth"""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        
        response = client.post("/api/v1x/mentors/availability", json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        assert response.status_code == 401


class TestMentorReviews:
    """Test review system"""
    
    def test_submit_review_not_logged_in(self, client):
        """Test submitting review requires auth"""
        response = client.post("/api/v1x/mentors/reviews", json={
            "session_id": 1,
            "rating": 5,
            "comment": "Great mentor!"
        })
        assert response.status_code == 401
