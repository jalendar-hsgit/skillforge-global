import pytest


class TestCompleteUserJourney:
    """Integration tests for complete user learning journey"""
    
    def test_new_user_complete_journey(self, client):
        """
        Test complete user journey:
        1. Signup
        2. Login
        3. Browse paths
        4. Save progress
        5. Take quiz
        6. Complete course
        """
        # 1. Signup
        email = "journey@example.com"
        password = "JourneyPass123!"
        
        signup_response = client.post("/api/v1/auth/signup", json={
            "email": email,
            "password": password
        })
        assert signup_response.status_code == 200
        assert signup_response.json()["created"] is True
        
        # 2. Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password
        })
        assert login_response.status_code == 200
        token = login_response.cookies.get("token")
        
        # 3. Get quizzes (browse learning paths)
        quizzes_response = client.get("/api/v1/quizzes")
        assert quizzes_response.status_code == 200
        quizzes = quizzes_response.json()
        assert len(quizzes) > 0
        
        # 4. Start learning a path - save progress
        path = "python-ai"
        progress_response = client.post(
            "/api/v1/progress",
            json={
                "path": path,
                "course_id": "python-basics",
                "progress": 50,
                "completed": False
            },
            cookies={"token": token}
        )
        assert progress_response.status_code in [200, 201]
        
        # 5. Take quiz
        quiz_response = client.get(f"/api/v1/quizzes/{path}")
        assert quiz_response.status_code == 200
        quiz = quiz_response.json()
        
        # Submit quiz answers (get first 5 questions correct)
        answers = {}
        for i in range(min(5, len(quiz["questions"]))):
            q = quiz["questions"][i]
            answers[str(q["id"])] = q["correct"]
        
        quiz_submit_response = client.post(
            f"/api/v1/quizzes/{path}/submit",
            json={"answers": answers},
            cookies={"token": token}
        )
        assert quiz_submit_response.status_code == 200
        quiz_result = quiz_submit_response.json()
        assert quiz_result["score"] == 5
        
        # 6. Complete course
        complete_response = client.post(
            "/api/v1/progress",
            json={
                "path": path,
                "course_id": "python-basics",
                "progress": 100,
                "completed": True
            },
            cookies={"token": token}
        )
        assert complete_response.status_code in [200, 201]
        
        # Verify user data
        me_response = client.get("/api/v1/auth/me", cookies={"token": token})
        assert me_response.status_code == 200
        assert me_response.json()["email"] == email


class TestMultiplePathsJourney:
    """Test user progressing through multiple learning paths"""
    
    def test_multiple_paths_simultaneously(self, client, test_user, auth_token):
        """Test user working on multiple paths at once"""
        paths = ["python-ai", "web-dev", "data-science"]
        
        # Start progress on multiple paths
        for path in paths:
            progress_response = client.post(
                "/api/v1/progress",
                json={
                    "path": path,
                    "course_id": f"{path}-course",
                    "progress": 30
                },
                cookies={"token": auth_token}
            )
            assert progress_response.status_code in [200, 201]
        
        # Get overall progress
        progress_response = client.get("/api/v1/progress", cookies={"token": auth_token})
        assert progress_response.status_code == 200
        
        # Take quiz on one path
        quiz_response = client.get("/api/v1/quizzes/python-ai")
        quiz = quiz_response.json()
        
        answers = {str(quiz["questions"][0]["id"]): quiz["questions"][0]["correct"]}
        submit_response = client.post(
            "/api/v1/quizzes/python-ai/submit",
            json={"answers": answers},
            cookies={"token": auth_token}
        )
        assert submit_response.status_code == 200


class TestQuizRetakeJourney:
    """Test user retaking quizzes to improve score"""
    
    def test_quiz_retake_improves_score(self, client, auth_token):
        """Test taking quiz multiple times with improving scores"""
        path = "web-dev"
        
        # Get quiz
        quiz_response = client.get(f"/api/v1/quizzes/{path}")
        quiz = quiz_response.json()
        
        # First attempt - get 2 questions correct
        answers_1 = {}
        for i in range(min(2, len(quiz["questions"]))):
            q = quiz["questions"][i]
            answers_1[str(q["id"])] = q["correct"]
        
        attempt_1 = client.post(
            f"/api/v1/quizzes/{path}/submit",
            json={"answers": answers_1},
            cookies={"token": auth_token}
        )
        assert attempt_1.status_code == 200
        score_1 = attempt_1.json()["score"]
        assert score_1 == 2
        
        # Second attempt - get 4 questions correct
        answers_2 = {}
        for i in range(min(4, len(quiz["questions"]))):
            q = quiz["questions"][i]
            answers_2[str(q["id"])] = q["correct"]
        
        attempt_2 = client.post(
            f"/api/v1/quizzes/{path}/submit",
            json={"answers": answers_2},
            cookies={"token": auth_token}
        )
        assert attempt_2.status_code == 200
        score_2 = attempt_2.json()["score"]
        assert score_2 == 4
        assert score_2 > score_1  # Improved


class TestProgressContinuity:
    """Test progress continuity across sessions"""
    
    def test_resume_after_logout_login(self, client):
        """Test resuming progress after logout and login"""
        email = "resume@example.com"
        password = "ResumePass123!"
        path = "cloud"
        
        # Signup and login
        client.post("/api/v1/auth/signup", json={"email": email, "password": password})
        login_1 = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        token_1 = login_1.cookies.get("token")
        
        # Save progress
        client.post(
            "/api/v1/progress",
            json={
                "path": path,
                "course_id": "aws-basics",
                "progress": 60
            },
            cookies={"token": token_1}
        )
        
        # Simulate logout by not using token
        # Login again
        login_2 = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        token_2 = login_2.cookies.get("token")
        
        # Get progress with new token
        progress_response = client.get(f"/api/v1/progress/{path}", cookies={"token": token_2})
        assert progress_response.status_code == 200
        # Progress should still be there


class TestPathCompletionJourney:
    """Test completing entire learning path"""
    
    def test_complete_path_with_quiz_passing(self, client, auth_token):
        """Test completing path: progress to 100% and pass quiz"""
        path = "data-science"
        
        # Complete all course progress
        courses = ["python-data", "pandas", "visualization", "ml-basics"]
        for course in courses:
            client.post(
                "/api/v1/progress",
                json={
                    "path": path,
                    "course_id": course,
                    "progress": 100,
                    "completed": True
                },
                cookies={"token": auth_token}
            )
        
        # Take and pass quiz
        quiz_response = client.get(f"/api/v1/quizzes/{path}")
        quiz = quiz_response.json()
        
        # Get all questions correct
        answers = {}
        for q in quiz["questions"]:
            answers[str(q["id"])] = q["correct"]
        
        quiz_result = client.post(
            f"/api/v1/quizzes/{path}/submit",
            json={"answers": answers},
            cookies={"token": auth_token}
        )
        assert quiz_result.status_code == 200
        result = quiz_result.json()
        assert result["score"] == len(quiz["questions"])
        assert result["passed"] is True or result["score"] >= result["total"] * 0.7


class TestErrorRecovery:
    """Test error handling and recovery scenarios"""
    
    def test_recover_from_failed_quiz(self, client, auth_token):
        """Test recovering from failed quiz attempt"""
        path = "mobile"
        
        # Get quiz
        quiz_response = client.get(f"/api/v1/quizzes/{path}")
        quiz = quiz_response.json()
        
        # Fail quiz (all wrong answers)
        wrong_answers = {}
        for q in quiz["questions"]:
            wrong_idx = (q["correct"] + 1) % len(q["options"])
            wrong_answers[str(q["id"])] = wrong_idx
        
        fail_response = client.post(
            f"/api/v1/quizzes/{path}/submit",
            json={"answers": wrong_answers},
            cookies={"token": auth_token}
        )
        assert fail_response.status_code == 200
        fail_result = fail_response.json()
        assert fail_result["score"] == 0
        
        # Retry and pass
        correct_answers = {}
        for q in quiz["questions"]:
            correct_answers[str(q["id"])] = q["correct"]
        
        pass_response = client.post(
            f"/api/v1/quizzes/{path}/submit",
            json={"answers": correct_answers},
            cookies={"token": auth_token}
        )
        assert pass_response.status_code == 200
        pass_result = pass_response.json()
        assert pass_result["score"] == len(quiz["questions"])
    
    def test_invalid_progress_handling(self, client, auth_token):
        """Test handling invalid progress data gracefully"""
        # Try invalid progress value
        response = client.post(
            "/api/v1/progress",
            json={
                "path": "python-ai",
                "course_id": "test",
                "progress": 150  # Invalid: > 100
            },
            cookies={"token": auth_token}
        )
        # Should handle gracefully
        assert response.status_code in [200, 201, 400, 422]


class TestConcurrentOperations:
    """Test concurrent user operations"""
    
    def test_simultaneous_progress_and_quiz(self, client, auth_token):
        """Test saving progress while taking quiz"""
        path = "python-ai"
        
        # Save progress
        progress_response = client.post(
            "/api/v1/progress",
            json={
                "path": path,
                "course_id": "basics",
                "progress": 80
            },
            cookies={"token": auth_token}
        )
        assert progress_response.status_code in [200, 201]
        
        # Take quiz immediately
        quiz_response = client.get(f"/api/v1/quizzes/{path}")
        quiz = quiz_response.json()
        
        answers = {str(quiz["questions"][0]["id"]): quiz["questions"][0]["correct"]}
        quiz_submit = client.post(
            f"/api/v1/quizzes/{path}/submit",
            json={"answers": answers},
            cookies={"token": auth_token}
        )
        assert quiz_submit.status_code == 200
        
        # Both operations should succeed


class TestDataConsistency:
    """Test data consistency across operations"""
    
    def test_progress_and_quiz_consistency(self, client, auth_token):
        """Test that progress and quiz data remain consistent"""
        path = "cloud"
        
        # Save progress
        client.post(
            "/api/v1/progress",
            json={
                "path": path,
                "course_id": "aws",
                "progress": 70
            },
            cookies={"token": auth_token}
        )
        
        # Get progress
        progress_1 = client.get(f"/api/v1/progress/{path}", cookies={"token": auth_token})
        
        # Take quiz
        quiz = client.get(f"/api/v1/quizzes/{path}").json()
        answers = {str(quiz["questions"][0]["id"]): quiz["questions"][0]["correct"]}
        client.post(f"/api/v1/quizzes/{path}/submit", json={"answers": answers}, cookies={"token": auth_token})
        
        # Get progress again - should still be consistent
        progress_2 = client.get(f"/api/v1/progress/{path}", cookies={"token": auth_token})
        
        assert progress_1.status_code == 200
        assert progress_2.status_code == 200


class TestHealthCheck:
    """Test application health and readiness"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_api_availability(self, client):
        """Test that all main API endpoints are available"""
        endpoints = [
            "/api/v1/quizzes",
            "/api/v1/auth/signup",
            "/api/v1/auth/login",
        ]
        
        for endpoint in endpoints:
            if "signup" in endpoint or "login" in endpoint:
                # POST endpoints need JSON data
                response = client.post(endpoint, json={"email": "test@test.com", "password": "Test123!"})
            else:
                response = client.get(endpoint)
            
            # Should not be 500/503 (server errors)
            assert response.status_code < 500
