"""
Mentor eligibility and utility services.
"""
from sqlalchemy.orm import Session
from app.models.progress import Progress
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User
from typing import Tuple, List


class MentorEligibilityService:
    """Service to check if a user is eligible to become a mentor."""
    
    # Eligibility requirements
    MIN_COMPLETED_PATHS = 1  # Must complete at least 1 learning path
    MIN_QUIZ_SCORE_PERCENT = 80  # Must average 80%+ on quizzes
    VALID_PATHS = ['python-ai', 'web-dev', 'data-science', 'cloud', 'mobile']
    
    @classmethod
    def check_eligibility(cls, user_id: int, db: Session) -> Tuple[bool, List[str], List[str], float]:
        """
        Check if user is eligible to become a mentor.
        
        Returns:
            tuple: (eligible, reasons, completed_paths, average_quiz_score)
        """
        reasons = []
        completed_paths = []
        average_quiz_score = 0.0
        
        # Check completed paths
        completed_paths = cls._get_completed_paths(user_id, db)
        
        if len(completed_paths) < cls.MIN_COMPLETED_PATHS:
            reasons.append(f"Must complete at least {cls.MIN_COMPLETED_PATHS} learning path(s). You have completed {len(completed_paths)}.")
        
        # Check quiz scores
        average_quiz_score = cls._get_average_quiz_score(user_id, db)
        
        if average_quiz_score < cls.MIN_QUIZ_SCORE_PERCENT:
            reasons.append(f"Must achieve {cls.MIN_QUIZ_SCORE_PERCENT}%+ average on quizzes. Your average is {average_quiz_score:.1f}%.")
        
        # User is eligible if no reasons for rejection
        eligible = len(reasons) == 0
        
        if eligible:
            reasons.append("You meet all requirements to become a mentor!")
        
        return eligible, reasons, completed_paths, average_quiz_score
    
    @classmethod
    def _get_completed_paths(cls, user_id: int, db: Session) -> List[str]:
        """
        Get list of paths the user has completed.
        
        A path is considered completed if the user has progress records
        for modules in that path. This is a simplified check.
        For more accuracy, you might want to define specific completion criteria.
        """
        # Get all progress records for user
        progress_records = db.query(Progress).filter(Progress.user_id == user_id).all()
        
        # Extract unique paths
        paths_with_progress = set(record.path for record in progress_records)
        
        # For now, consider any path with progress as "completed"
        # TODO: Add more sophisticated completion logic (e.g., minimum modules completed)
        completed = []
        for path in paths_with_progress:
            if path in cls.VALID_PATHS:
                # Check if user has completed multiple modules in this path
                path_progress = [r for r in progress_records if r.path == path]
                if len(path_progress) >= 3:  # Arbitrary: need at least 3 modules completed
                    completed.append(path)
        
        return completed
    
    @classmethod
    def _get_average_quiz_score(cls, user_id: int, db: Session) -> float:
        """
        Calculate user's average quiz score across all attempts.
        
        Returns:
            float: Average score as percentage (0-100)
        """
        quiz_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all()
        
        if not quiz_attempts:
            return 0.0
        
        # Calculate average percentage
        total_percentage = 0.0
        for attempt in quiz_attempts:
            if attempt.total > 0:
                percentage = (attempt.score / attempt.total) * 100
                total_percentage += percentage
        
        average = total_percentage / len(quiz_attempts)
        return round(average, 2)
    
    @classmethod
    def get_best_quiz_score_by_path(cls, user_id: int, path: str, db: Session) -> float:
        """
        Get user's best quiz score for a specific path.
        
        Returns:
            float: Best score as percentage (0-100)
        """
        attempts = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.path == path
        ).all()
        
        if not attempts:
            return 0.0
        
        best_percentage = 0.0
        for attempt in attempts:
            if attempt.total > 0:
                percentage = (attempt.score / attempt.total) * 100
                best_percentage = max(best_percentage, percentage)
        
        return round(best_percentage, 2)


class MentorSearchService:
    """Service for searching and filtering mentors."""
    
    @classmethod
    def search_mentors(cls, db: Session, expertise: str = None, min_rating: float = None, 
                       max_rate: float = None, status: str = "approved", limit: int = 50):
        """
        Search for mentors with filters.
        
        Args:
            expertise: Filter by expertise area (e.g., 'python-ai')
            min_rating: Minimum average rating
            max_rate: Maximum hourly rate
            status: Mentor status (default: approved)
            limit: Max results to return
        """
        from app.modelsx.mentor import Mentor, MentorStatus
        
        query = db.query(Mentor).filter(Mentor.status == MentorStatus.APPROVED)
        
        if expertise:
            # Use LIKE to search within comma-separated expertise field
            query = query.filter(Mentor.expertise.like(f"%{expertise}%"))
        
        if min_rating is not None:
            query = query.filter(Mentor.average_rating >= min_rating)
        
        if max_rate is not None:
            query = query.filter(Mentor.hourly_rate <= max_rate)
        
        return query.order_by(Mentor.average_rating.desc()).limit(limit).all()


class SessionManagementService:
    """Service for managing mentor sessions."""
    
    @classmethod
    def can_book_session(cls, student_id: int, mentor_id: int, scheduled_at, db: Session) -> Tuple[bool, str]:
        """
        Check if a session can be booked.
        
        Returns:
            tuple: (can_book, reason_if_not)
        """
        from app.modelsx.mentor import Mentor, MentorSession, SessionStatus
        from datetime import datetime
        
        # Check if mentor exists and is approved
        mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
        if not mentor:
            return False, "Mentor not found"
        
        if mentor.status != "approved":
            return False, "Mentor is not currently available"
        
        # Check if scheduled time is in the future
        if scheduled_at <= datetime.utcnow():
            return False, "Cannot book sessions in the past"
        
        # Check if mentor has conflicting session
        conflicting = db.query(MentorSession).filter(
            MentorSession.mentor_id == mentor_id,
            MentorSession.scheduled_at == scheduled_at,
            MentorSession.status.in_([SessionStatus.PENDING, SessionStatus.CONFIRMED])
        ).first()
        
        if conflicting:
            return False, "Mentor already has a session at this time"
        
        return True, "OK"
    
    @classmethod
    def generate_meeting_url(cls, session_id: int) -> str:
        """
        Generate a meeting URL for the session.
        For now, returns a placeholder. Integrate with Zoom/Meet later.
        """
        # TODO: Integrate with Zoom API or Google Meet API
        return f"https://meet.skillforge.com/session/{session_id}"
