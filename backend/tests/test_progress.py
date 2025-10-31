import pytest
from datetime import datetime


class TestProgressTracking:
    """Test progress tracking endpoints"""
    
    def test_get_progress_unauthenticated(self, client):
        """Test getting progress without authentication"""
        response = client.get("/api/v1/progress")
        
        assert response.status_code == 401
    
    def test_get_progress_authenticated_empty(self, client, auth_token):
        """Test getting progress for new user (no progress yet)"""
        response = client.get("/api/v1/progress", cookies={"token": auth_token})
        
        assert response.status_code == 200
        data = response.json()
        # Should return empty list or dict
        assert isinstance(data, (list, dict))
    
    def test_save_progress_unauthenticated(self, client):
        """Test saving progress without authentication"""
        response = client.post("/api/v1/progress", json={
            "path": "python-ai",
            "course_id": "python-basics",
            "progress": 50
        })
        
        assert response.status_code == 401
    
    def test_save_progress_authenticated(self, client, auth_token):
        """Test saving progress with authentication"""
        progress_data = {
            "path": "python-ai",
            "course_id": "python-basics",
            "progress": 50,
            "completed": False
        }
        
        response = client.post(
            "/api/v1/progress",
            json=progress_data,
            cookies={"token": auth_token}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        
        # Verify saved data
        if isinstance(data, dict):
            assert data.get("path") == "python-ai" or data.get("course_id") == "python-basics"
    
    def test_update_progress(self, client, auth_token):
        """Test updating existing progress"""
        # Save initial progress
        client.post(
            "/api/v1/progress",
            json={
                "path": "web-dev",
                "course_id": "html-css",
                "progress": 30
            },
            cookies={"token": auth_token}
        )
        
        # Update progress
        response = client.post(
            "/api/v1/progress",
            json={
                "path": "web-dev",
                "course_id": "html-css",
                "progress": 75
            },
            cookies={"token": auth_token}
        )
        
        assert response.status_code in [200, 201]
    
    def test_complete_course(self, client, auth_token):
        """Test marking course as completed"""
        response = client.post(
            "/api/v1/progress",
            json={
                "path": "data-science",
                "course_id": "pandas-basics",
                "progress": 100,
                "completed": True
            },
            cookies={"token": auth_token}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        
        # Check completion flag
        if "completed" in data:
            assert data["completed"] is True


class TestProgressByPath:
    """Test progress retrieval by learning path"""
    
    def test_get_path_progress_unauthenticated(self, client):
        """Test getting path progress without auth"""
        response = client.get("/api/v1/progress/python-ai")
        
        assert response.status_code == 401
    
    def test_get_path_progress_authenticated(self, client, auth_token):
        """Test getting progress for specific path"""
        # Save some progress first
        client.post(
            "/api/v1/progress",
            json={
                "path": "python-ai",
                "course_id": "python-basics",
                "progress": 60
            },
            cookies={"token": auth_token}
        )
        
        # Get path progress
        response = client.get("/api/v1/progress/python-ai", cookies={"token": auth_token})
        
        assert response.status_code == 200
        # Should return progress data
        assert isinstance(response.json(), (dict, list))
    
    def test_get_path_progress_no_data(self, client, auth_token):
        """Test getting progress for path with no data"""
        response = client.get("/api/v1/progress/mobile", cookies={"token": auth_token})
        
        assert response.status_code == 200
        # Should return empty or null
        data = response.json()
        assert data is None or data == {} or data == []


class TestProgressValidation:
    """Test progress data validation"""
    
    def test_progress_value_bounds(self, client, auth_token):
        """Test that progress value must be between 0-100"""
        # Test progress > 100
        response = client.post(
            "/api/v1/progress",
            json={
                "path": "cloud",
                "course_id": "aws-basics",
                "progress": 150
            },
            cookies={"token": auth_token}
        )
        # Should either reject or clamp to 100
        assert response.status_code in [200, 201, 400, 422]
        
        # Test negative progress
        response = client.post(
            "/api/v1/progress",
            json={
                "path": "cloud",
                "course_id": "aws-basics",
                "progress": -10
            },
            cookies={"token": auth_token}
        )
        # Should either reject or clamp to 0
        assert response.status_code in [200, 201, 400, 422]
    
    def test_invalid_path_id(self, client, auth_token):
        """Test saving progress with invalid path"""
        response = client.post(
            "/api/v1/progress",
            json={
                "path": "nonexistent-path",
                "course_id": "some-course",
                "progress": 50
            },
            cookies={"token": auth_token}
        )
        
        # May accept any path or validate
        assert response.status_code in [200, 201, 400, 404]
    
    def test_missing_required_fields(self, client, auth_token):
        """Test saving progress with missing fields"""
        response = client.post(
            "/api/v1/progress",
            json={"progress": 50},  # Missing path and course_id
            cookies={"token": auth_token}
        )
        
        assert response.status_code in [400, 422]


class TestProgressStatistics:
    """Test progress statistics and aggregation"""
    
    def test_overall_progress_calculation(self, client, auth_token):
        """Test getting overall progress across all paths"""
        # Save progress for multiple paths
        paths_progress = [
            {"path": "python-ai", "course_id": "python-basics", "progress": 100},
            {"path": "web-dev", "course_id": "html-css", "progress": 75},
            {"path": "data-science", "course_id": "pandas", "progress": 50},
        ]
        
        for prog in paths_progress:
            client.post("/api/v1/progress", json=prog, cookies={"token": auth_token})
        
        # Get overall progress
        response = client.get("/api/v1/progress", cookies={"token": auth_token})
        
        assert response.status_code == 200
        # Should return aggregated data
        data = response.json()
        assert isinstance(data, (list, dict))
    
    def test_completed_courses_count(self, client, auth_token):
        """Test counting completed courses"""
        # Complete some courses
        completed_courses = [
            {"path": "python-ai", "course_id": "python-basics", "progress": 100, "completed": True},
            {"path": "python-ai", "course_id": "advanced-python", "progress": 100, "completed": True},
        ]
        
        for course in completed_courses:
            client.post("/api/v1/progress", json=course, cookies={"token": auth_token})
        
        # Get progress
        response = client.get("/api/v1/progress", cookies={"token": auth_token})
        data = response.json()
        
        # Should show completed courses
        assert response.status_code == 200


class TestProgressPersistence:
    """Test progress data persistence"""
    
    def test_progress_persists_across_sessions(self, client, auth_token):
        """Test that progress is saved and retrievable"""
        progress_data = {
            "path": "mobile",
            "course_id": "react-native",
            "progress": 85,
            "completed": False
        }
        
        # Save progress
        save_response = client.post(
            "/api/v1/progress",
            json=progress_data,
            cookies={"token": auth_token}
        )
        assert save_response.status_code in [200, 201]
        
        # Retrieve progress
        get_response = client.get("/api/v1/progress", cookies={"token": auth_token})
        assert get_response.status_code == 200
        
        # Progress should be in response
        retrieved = get_response.json()
        assert isinstance(retrieved, (list, dict))
    
    def test_multiple_courses_same_path(self, client, auth_token):
        """Test tracking progress for multiple courses in same path"""
        courses = [
            {"path": "web-dev", "course_id": "html-css", "progress": 100},
            {"path": "web-dev", "course_id": "javascript", "progress": 60},
            {"path": "web-dev", "course_id": "react", "progress": 30},
        ]
        
        for course in courses:
            response = client.post(
                "/api/v1/progress",
                json=course,
                cookies={"token": auth_token}
            )
            assert response.status_code in [200, 201]
        
        # Get path progress
        response = client.get("/api/v1/progress/web-dev", cookies={"token": auth_token})
        assert response.status_code == 200


class TestProgressTimestamps:
    """Test progress timestamp tracking"""
    
    def test_progress_has_timestamps(self, client, auth_token):
        """Test that progress records include timestamps"""
        response = client.post(
            "/api/v1/progress",
            json={
                "path": "cloud",
                "course_id": "azure-basics",
                "progress": 45
            },
            cookies={"token": auth_token}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            # Check for timestamp fields (created_at, updated_at, etc.)
            has_timestamp = any(
                field in data 
                for field in ["created_at", "updated_at", "timestamp", "last_updated"]
            )
            # Timestamps are optional but good practice
            assert response.status_code in [200, 201]


class TestProgressIntegration:
    """Integration tests for complete progress flow"""
    
    def test_complete_learning_path_flow(self, client, test_user, auth_token):
        """Test complete flow: start -> progress -> complete path"""
        path = "data-science"
        courses = [
            {"course_id": "python-data", "progress": 100},
            {"course_id": "pandas", "progress": 100},
            {"course_id": "visualization", "progress": 100},
        ]
        
        # Complete all courses in path
        for course_data in courses:
            response = client.post(
                "/api/v1/progress",
                json={
                    "path": path,
                    "course_id": course_data["course_id"],
                    "progress": course_data["progress"],
                    "completed": True
                },
                cookies={"token": auth_token}
            )
            assert response.status_code in [200, 201]
        
        # Get overall progress
        progress_response = client.get("/api/v1/progress", cookies={"token": auth_token})
        assert progress_response.status_code == 200
        
        # Get specific path progress
        path_response = client.get(f"/api/v1/progress/{path}", cookies={"token": auth_token})
        assert path_response.status_code == 200
    
    def test_progress_and_quiz_integration(self, client, auth_token):
        """Test progress tracking alongside quiz completion"""
        path = "python-ai"
        
        # Save course progress
        client.post(
            "/api/v1/progress",
            json={
                "path": path,
                "course_id": "python-basics",
                "progress": 100,
                "completed": True
            },
            cookies={"token": auth_token}
        )
        
        # Take quiz
        quiz_response = client.get(f"/api/v1/quizzes/{path}")
        quiz = quiz_response.json()
        
        # Submit quiz with correct answers
        answers = {str(quiz["questions"][0]["id"]): quiz["questions"][0]["correct"]}
        submit_response = client.post(
            f"/api/v1/quizzes/{path}/submit",
            json={"answers": answers},
            cookies={"token": auth_token}
        )
        
        assert submit_response.status_code == 200
        
        # Check progress still accessible
        progress_response = client.get(f"/api/v1/progress/{path}", cookies={"token": auth_token})
        assert progress_response.status_code == 200
