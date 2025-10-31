import pytest
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.progress import Progress
from app.models.quiz_attempt import QuizAttempt
from app.core.security import get_password_hash


class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, db_session: Session):
        """Test creating a user"""
        user = User(
            email="modeltest@example.com",
            hashed_password=hash_password("TestPass123!")
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "modeltest@example.com"
        assert user.hashed_password != "TestPass123!"  # Should be hashed
    
    def test_user_email_unique(self, db_session: Session):
        """Test that user email must be unique"""
        email = "unique@example.com"
        
        # Create first user
        user1 = User(email=email, hashed_password=hash_password("Pass1"))
        db_session.add(user1)
        db_session.commit()
        
        # Try to create duplicate
        user2 = User(email=email, hashed_password=hash_password("Pass2"))
        db_session.add(user2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_user_query(self, db_session: Session):
        """Test querying users"""
        user = User(
            email="query@example.com",
            hashed_password=hash_password("QueryPass123!")
        )
        db_session.add(user)
        db_session.commit()
        
        # Query by email
        found = db_session.query(User).filter(User.email == "query@example.com").first()
        assert found is not None
        assert found.id == user.id
    
    def test_user_update(self, db_session: Session):
        """Test updating user"""
        user = User(
            email="update@example.com",
            hashed_password=hash_password("OldPass123!")
        )
        db_session.add(user)
        db_session.commit()
        
        # Update password
        user.hashed_password = hash_password("NewPass123!")
        db_session.commit()
        
        # Verify update
        found = db_session.query(User).filter(User.id == user.id).first()
        assert found.hashed_password == user.hashed_password


class TestProgressModel:
    """Test Progress model"""
    
    def test_create_progress(self, db_session: Session, test_user):
        """Test creating progress record"""
        user = db_session.query(User).filter(User.email == test_user["email"]).first()
        
        progress = Progress(
            user_id=user.id,
            path="python-ai",
            course_id="python-basics",
            progress=50,
            completed=False
        )
        db_session.add(progress)
        db_session.commit()
        
        assert progress.id is not None
        assert progress.user_id == user.id
        assert progress.progress == 50
    
    def test_progress_constraints(self, db_session: Session, test_user):
        """Test progress value constraints"""
        user = db_session.query(User).filter(User.email == test_user["email"]).first()
        
        # Valid progress (0-100)
        valid_progress = Progress(
            user_id=user.id,
            path="web-dev",
            course_id="html",
            progress=75
        )
        db_session.add(valid_progress)
        db_session.commit()
        
        assert valid_progress.id is not None
    
    def test_update_progress(self, db_session: Session, test_user):
        """Test updating progress"""
        user = db_session.query(User).filter(User.email == test_user["email"]).first()
        
        progress = Progress(
            user_id=user.id,
            path="data-science",
            course_id="pandas",
            progress=30
        )
        db_session.add(progress)
        db_session.commit()
        
        # Update progress
        progress.progress = 80
        progress.completed = True
        db_session.commit()
        
        # Verify
        found = db_session.query(Progress).filter(Progress.id == progress.id).first()
        assert found.progress == 80
        assert found.completed is True
    
    def test_query_user_progress(self, db_session: Session, test_user):
        """Test querying progress by user"""
        user = db_session.query(User).filter(User.email == test_user["email"]).first()
        
        # Create multiple progress records
        paths = ["python-ai", "web-dev", "cloud"]
        for path in paths:
            progress = Progress(
                user_id=user.id,
                path=path,
                course_id=f"{path}-course",
                progress=50
            )
            db_session.add(progress)
        db_session.commit()
        
        # Query all progress for user
        user_progress = db_session.query(Progress).filter(Progress.user_id == user.id).all()
        assert len(user_progress) >= 3


class TestQuizAttemptModel:
    """Test QuizAttempt model"""
    
    def test_create_quiz_attempt(self, db_session: Session, test_user):
        """Test creating quiz attempt"""
        user = db_session.query(User).filter(User.email == test_user["email"]).first()
        
        attempt = QuizAttempt(
            user_id=user.id,
            path="python-ai",
            score=18,
            total=25,
            passed=True
        )
        db_session.add(attempt)
        db_session.commit()
        
        assert attempt.id is not None
        assert attempt.score == 18
        assert attempt.passed is True
    
    def test_quiz_attempt_query(self, db_session: Session, test_user):
        """Test querying quiz attempts"""
        user = db_session.query(User).filter(User.email == test_user["email"]).first()
        
        # Create multiple attempts
        attempts_data = [
            {"path": "python-ai", "score": 15, "total": 25, "passed": False},
            {"path": "python-ai", "score": 20, "total": 25, "passed": True},
            {"path": "web-dev", "score": 4, "total": 5, "passed": True},
        ]
        
        for data in attempts_data:
            attempt = QuizAttempt(user_id=user.id, **data)
            db_session.add(attempt)
        db_session.commit()
        
        # Query attempts for python-ai path
        python_attempts = db_session.query(QuizAttempt).filter(
            QuizAttempt.user_id == user.id,
            QuizAttempt.path == "python-ai"
        ).all()
        
        assert len(python_attempts) >= 2
    
    def test_best_quiz_score(self, db_session: Session, test_user):
        """Test finding best quiz score"""
        user = db_session.query(User).filter(User.email == test_user["email"]).first()
        
        # Create multiple attempts with different scores
        scores = [15, 20, 18, 22, 19]
        for score in scores:
            attempt = QuizAttempt(
                user_id=user.id,
                path="data-science",
                score=score,
                total=25,
                passed=score >= 18
            )
            db_session.add(attempt)
        db_session.commit()
        
        # Find best score
        best = db_session.query(QuizAttempt).filter(
            QuizAttempt.user_id == user.id,
            QuizAttempt.path == "data-science"
        ).order_by(QuizAttempt.score.desc()).first()
        
        assert best.score == 22


class TestModelRelationships:
    """Test relationships between models"""
    
    def test_user_progress_relationship(self, db_session: Session):
        """Test relationship between User and Progress"""
        # Create user
        user = User(
            email="relations@example.com",
            hashed_password=hash_password("Pass123!")
        )
        db_session.add(user)
        db_session.commit()
        
        # Create progress
        progress = Progress(
            user_id=user.id,
            path="mobile",
            course_id="react-native",
            progress=60
        )
        db_session.add(progress)
        db_session.commit()
        
        # Test relationship (if defined)
        # This depends on whether you've defined relationships in models
        assert progress.user_id == user.id
    
    def test_user_quiz_attempts_relationship(self, db_session: Session):
        """Test relationship between User and QuizAttempt"""
        user = User(
            email="attempts@example.com",
            hashed_password=hash_password("Pass123!")
        )
        db_session.add(user)
        db_session.commit()
        
        # Create quiz attempts
        for i in range(3):
            attempt = QuizAttempt(
                user_id=user.id,
                path="cloud",
                score=i + 3,
                total=5,
                passed=True
            )
            db_session.add(attempt)
        db_session.commit()
        
        # Query attempts
        attempts = db_session.query(QuizAttempt).filter(
            QuizAttempt.user_id == user.id
        ).all()
        
        assert len(attempts) >= 3


class TestModelValidation:
    """Test model data validation"""
    
    def test_user_email_required(self, db_session: Session):
        """Test that user email is required"""
        user = User(hashed_password=hash_password("Pass123!"))
        db_session.add(user)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_progress_user_id_required(self, db_session: Session):
        """Test that progress requires user_id"""
        progress = Progress(
            path="python-ai",
            course_id="basics",
            progress=50
        )
        db_session.add(progress)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_quiz_attempt_validation(self, db_session: Session, test_user):
        """Test quiz attempt data validation"""
        user = db_session.query(User).filter(User.email == test_user["email"]).first()
        
        # Valid attempt
        valid_attempt = QuizAttempt(
            user_id=user.id,
            path="web-dev",
            score=4,
            total=5,
            passed=True
        )
        db_session.add(valid_attempt)
        db_session.commit()
        
        assert valid_attempt.id is not None


class TestModelCRUD:
    """Test CRUD operations on models"""
    
    def test_create_read_update_delete_user(self, db_session: Session):
        """Test full CRUD cycle for User"""
        # Create
        user = User(
            email="crud@example.com",
            hashed_password=hash_password("CrudPass123!")
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        
        # Read
        found = db_session.query(User).filter(User.id == user_id).first()
        assert found is not None
        assert found.email == "crud@example.com"
        
        # Update
        found.email = "updated@example.com"
        db_session.commit()
        updated = db_session.query(User).filter(User.id == user_id).first()
        assert updated.email == "updated@example.com"
        
        # Delete
        db_session.delete(updated)
        db_session.commit()
        deleted = db_session.query(User).filter(User.id == user_id).first()
        assert deleted is None
    
    def test_create_read_update_delete_progress(self, db_session: Session, test_user):
        """Test full CRUD cycle for Progress"""
        user = db_session.query(User).filter(User.email == test_user["email"]).first()
        
        # Create
        progress = Progress(
            user_id=user.id,
            path="cloud",
            course_id="aws",
            progress=40
        )
        db_session.add(progress)
        db_session.commit()
        progress_id = progress.id
        
        # Read
        found = db_session.query(Progress).filter(Progress.id == progress_id).first()
        assert found is not None
        assert found.progress == 40
        
        # Update
        found.progress = 90
        db_session.commit()
        updated = db_session.query(Progress).filter(Progress.id == progress_id).first()
        assert updated.progress == 90
        
        # Delete
        db_session.delete(updated)
        db_session.commit()
        deleted = db_session.query(Progress).filter(Progress.id == progress_id).first()
        assert deleted is None


class TestModelEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_progress_boundary_values(self, db_session: Session, test_user):
        """Test progress with boundary values"""
        user = db_session.query(User).filter(User.email == test_user["email"]).first()
        
        # Test 0 progress
        progress_zero = Progress(
            user_id=user.id,
            path="mobile",
            course_id="flutter",
            progress=0
        )
        db_session.add(progress_zero)
        
        # Test 100 progress
        progress_full = Progress(
            user_id=user.id,
            path="mobile",
            course_id="swift",
            progress=100
        )
        db_session.add(progress_full)
        
        db_session.commit()
        
        assert progress_zero.id is not None
        assert progress_full.id is not None
    
    def test_quiz_attempt_perfect_score(self, db_session: Session, test_user):
        """Test quiz attempt with perfect score"""
        user = db_session.query(User).filter(User.email == test_user["email"]).first()
        
        attempt = QuizAttempt(
            user_id=user.id,
            path="python-ai",
            score=25,
            total=25,
            passed=True
        )
        db_session.add(attempt)
        db_session.commit()
        
        assert attempt.score == attempt.total
        assert attempt.passed is True
    
    def test_quiz_attempt_zero_score(self, db_session: Session, test_user):
        """Test quiz attempt with zero score"""
        user = db_session.query(User).filter(User.email == test_user["email"]).first()
        
        attempt = QuizAttempt(
            user_id=user.id,
            path="web-dev",
            score=0,
            total=5,
            passed=False
        )
        db_session.add(attempt)
        db_session.commit()
        
        assert attempt.score == 0
        assert attempt.passed is False
