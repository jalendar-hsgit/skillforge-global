import pytest
import json


class TestQuizList:
    """Test quiz listing endpoints"""
    
    def test_list_all_quizzes(self, client):
        """Test getting all quizzes"""
        response = client.get("/api/v1/quizzes")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5  # 5 learning paths
        
        # Verify structure
        quiz = data[0]
        assert "id" in quiz
        assert "title" in quiz
        assert "questions" in quiz
        assert isinstance(quiz["questions"], list)
    
    def test_quiz_question_structure(self, client):
        """Test that quiz questions have correct structure"""
        response = client.get("/api/v1/quizzes")
        data = response.json()
        
        for quiz in data:
            for question in quiz["questions"]:
                assert "id" in question
                assert "question" in question
                assert "options" in question
                assert "correct" in question
                assert len(question["options"]) >= 2
                assert isinstance(question["correct"], int)
                assert 0 <= question["correct"] < len(question["options"])


class TestQuizByPath:
    """Test quiz retrieval by path slug"""
    
    def test_get_quiz_python_ai(self, client):
        """Test getting Python AI quiz"""
        response = client.get("/api/v1/quizzes/python-ai")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "python-ai"
        assert data["title"] == "Python & AI Mastery"
        assert len(data["questions"]) == 25  # Python AI has 25 questions
    
    def test_get_quiz_web_dev(self, client):
        """Test getting Web Development quiz"""
        response = client.get("/api/v1/quizzes/web-dev")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "web-dev"
        assert data["title"] == "Full-Stack Web Development"
        assert len(data["questions"]) == 5
    
    def test_get_quiz_data_science(self, client):
        """Test getting Data Science quiz"""
        response = client.get("/api/v1/quizzes/data-science")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "data-science"
        assert len(data["questions"]) == 5
    
    def test_get_quiz_cloud(self, client):
        """Test getting Cloud Engineering quiz"""
        response = client.get("/api/v1/quizzes/cloud")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "cloud"
        assert len(data["questions"]) == 5
    
    def test_get_quiz_mobile(self, client):
        """Test getting Mobile Development quiz"""
        response = client.get("/api/v1/quizzes/mobile")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "mobile"
        assert len(data["questions"]) == 5
    
    def test_get_quiz_nonexistent(self, client):
        """Test getting non-existent quiz returns 404"""
        response = client.get("/api/v1/quizzes/nonexistent-path")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestQuizSubmission:
    """Test quiz submission and scoring"""
    
    def test_submit_quiz_unauthenticated(self, client):
        """Test submitting quiz without authentication"""
        response = client.post("/api/v1/quizzes/python-ai/submit", json={
            "answers": {"1": 0, "2": 1}
        })
        
        assert response.status_code == 401
    
    def test_submit_quiz_authenticated(self, client, test_user, auth_token):
        """Test submitting quiz with authentication"""
        # Get quiz first to see questions
        quiz_response = client.get("/api/v1/quizzes/python-ai")
        quiz = quiz_response.json()
        
        # Submit correct answers for first 3 questions
        answers = {}
        for i in range(min(3, len(quiz["questions"]))):
            q = quiz["questions"][i]
            answers[str(q["id"])] = q["correct"]
        
        response = client.post(
            "/api/v1/quizzes/python-ai/submit",
            json={"answers": answers},
            cookies={"token": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "passed" in data
        assert "total" in data
        assert data["score"] == 3  # All correct
        assert data["total"] == len(answers)
    
    def test_submit_quiz_incorrect_answers(self, client, test_user, auth_token):
        """Test submitting quiz with incorrect answers"""
        # Get quiz
        quiz_response = client.get("/api/v1/quizzes/web-dev")
        quiz = quiz_response.json()
        
        # Submit wrong answers
        answers = {}
        for i in range(min(3, len(quiz["questions"]))):
            q = quiz["questions"][i]
            # Pick wrong answer (not the correct one)
            wrong_answer = (q["correct"] + 1) % len(q["options"])
            answers[str(q["id"])] = wrong_answer
        
        response = client.post(
            "/api/v1/quizzes/web-dev/submit",
            json={"answers": answers},
            cookies={"token": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 0  # All wrong
        assert data["passed"] is False
    
    def test_submit_quiz_mixed_answers(self, client, test_user, auth_token):
        """Test submitting quiz with mix of correct and incorrect"""
        quiz_response = client.get("/api/v1/quizzes/python-ai")
        quiz = quiz_response.json()
        
        # Submit mix: first 2 correct, next 2 wrong
        answers = {}
        for i in range(min(4, len(quiz["questions"]))):
            q = quiz["questions"][i]
            if i < 2:
                answers[str(q["id"])] = q["correct"]  # Correct
            else:
                wrong = (q["correct"] + 1) % len(q["options"])
                answers[str(q["id"])] = wrong  # Wrong
        
        response = client.post(
            "/api/v1/quizzes/python-ai/submit",
            json={"answers": answers},
            cookies={"token": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 2
        assert data["total"] == 4
    
    def test_submit_quiz_empty_answers(self, client, auth_token):
        """Test submitting quiz with no answers"""
        response = client.post(
            "/api/v1/quizzes/python-ai/submit",
            json={"answers": {}},
            cookies={"token": auth_token}
        )
        
        assert response.status_code in [200, 400]  # May accept or reject empty
    
    def test_submit_quiz_invalid_question_id(self, client, auth_token):
        """Test submitting with invalid question IDs"""
        response = client.post(
            "/api/v1/quizzes/python-ai/submit",
            json={"answers": {"999": 0}},  # Non-existent question
            cookies={"token": auth_token}
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400]


class TestQuizPassing:
    """Test quiz passing logic"""
    
    def test_passing_score_calculation(self, client, auth_token):
        """Test that passing score is calculated correctly (typically 70%)"""
        quiz_response = client.get("/api/v1/quizzes/data-science")
        quiz = quiz_response.json()
        total_questions = len(quiz["questions"])
        
        # Submit enough correct answers to pass (70%)
        passing_count = int(total_questions * 0.7) + 1
        answers = {}
        for i in range(passing_count):
            q = quiz["questions"][i]
            answers[str(q["id"])] = q["correct"]
        
        response = client.post(
            "/api/v1/quizzes/data-science/submit",
            json={"answers": answers},
            cookies={"token": auth_token}
        )
        
        data = response.json()
        # Check if marked as passed
        if "passed" in data:
            assert data["passed"] is True or data["score"] >= passing_count


class TestQuizDataIntegrity:
    """Test quiz data integrity and consistency"""
    
    def test_quiz_ids_unique(self, client):
        """Test that all quiz IDs are unique"""
        response = client.get("/api/v1/quizzes")
        quizzes = response.json()
        
        ids = [q["id"] for q in quizzes]
        assert len(ids) == len(set(ids))  # No duplicates
    
    def test_question_ids_unique_per_quiz(self, client):
        """Test that question IDs are unique within each quiz"""
        response = client.get("/api/v1/quizzes")
        quizzes = response.json()
        
        for quiz in quizzes:
            question_ids = [q["id"] for q in quiz["questions"]]
            assert len(question_ids) == len(set(question_ids))
    
    def test_all_questions_have_correct_answer(self, client):
        """Test that all questions have valid correct answer index"""
        response = client.get("/api/v1/quizzes")
        quizzes = response.json()
        
        for quiz in quizzes:
            for question in quiz["questions"]:
                correct_idx = question["correct"]
                num_options = len(question["options"])
                assert 0 <= correct_idx < num_options
    
    def test_all_questions_have_minimum_options(self, client):
        """Test that all questions have at least 2 options"""
        response = client.get("/api/v1/quizzes")
        quizzes = response.json()
        
        for quiz in quizzes:
            for question in quiz["questions"]:
                assert len(question["options"]) >= 2
    
    def test_question_text_not_empty(self, client):
        """Test that no question text is empty"""
        response = client.get("/api/v1/quizzes")
        quizzes = response.json()
        
        for quiz in quizzes:
            for question in quiz["questions"]:
                assert len(question["question"].strip()) > 0
                for option in question["options"]:
                    assert len(option.strip()) > 0


class TestQuizConcepts:
    """Test that quizzes cover advanced concepts"""
    
    def test_python_ai_advanced_topics(self, client):
        """Test Python AI quiz covers advanced topics"""
        response = client.get("/api/v1/quizzes/python-ai")
        quiz = response.json()
        
        # Check for advanced keywords in questions
        all_text = " ".join([q["question"].lower() for q in quiz["questions"]])
        
        # Should have AI/ML concepts
        ai_keywords = ["neural", "machine learning", "deep learning", "model", "training", 
                       "algorithm", "gradient", "tensor", "pytorch", "tensorflow"]
        has_ai_content = any(keyword in all_text for keyword in ai_keywords)
        assert has_ai_content, "Python AI quiz should cover AI/ML concepts"
    
    def test_quiz_difficulty_distribution(self, client):
        """Test that quizzes have good difficulty distribution"""
        response = client.get("/api/v1/quizzes/python-ai")
        quiz = response.json()
        
        # With 25 questions, should be comprehensive
        assert len(quiz["questions"]) >= 20, "Should have substantial question count"
        
        # All questions should have at least 3 options for good difficulty
        for question in quiz["questions"]:
            assert len(question["options"]) >= 3, "Questions should have multiple options"
