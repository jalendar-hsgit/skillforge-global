"""
Badge and Gamification Service
Handles badge earning, milestone tracking, and achievement unlocking
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import logging

from app.modelsx.badges import (
    Badge, UserBadge, BadgeProgress, Leaderboard, Achievement,
    UserAchievement, BadgeConditionType, BadgeCategory
)
from app.models.user import User

logger = logging.getLogger(__name__)


class BadgeService:
    """Service for managing badge earning and achievement tracking"""

    @staticmethod
    def award_badge(
        db: Session,
        user_id: int,
        badge_id: int,
        context_data: dict = None
    ) -> UserBadge | None:
        """
        Award a badge to a user
        
        Args:
            db: Database session
            user_id: User ID
            badge_id: Badge ID
            context_data: Optional contextual data (challenge_id, score, time, etc)
        
        Returns:
            UserBadge record or None if already earned
        """
        try:
            # Check if user already has this badge
            existing = db.query(UserBadge).filter(
                and_(
                    UserBadge.user_id == user_id,
                    UserBadge.badge_id == badge_id
                )
            ).first()

            if existing:
                # For repeatable badges, increment count
                existing.earn_count = (existing.earn_count or 1) + 1
                existing.last_earned_at = datetime.utcnow()
                db.commit()
                return existing

            # Create new badge record
            user_badge = UserBadge(
                user_id=user_id,
                badge_id=badge_id,
                earn_count=1,
                first_earned_at=datetime.utcnow(),
                last_earned_at=datetime.utcnow()
            )
            db.add(user_badge)
            db.commit()

            # Award points to leaderboard
            BadgeService.update_leaderboard(db, user_id, badge_id=badge_id)

            logger.info(f"Badge {badge_id} awarded to user {user_id}")
            return user_badge

        except Exception as e:
            logger.error(f"Error awarding badge: {str(e)}")
            db.rollback()
            return None

    @staticmethod
    def check_milestone_badges(
        db: Session,
        user_id: int,
        milestone_type: str,
        value: int
    ) -> list[UserBadge]:
        """
        Check and award badges based on milestone completion
        
        Milestone types:
        - challenges_solved: Number of challenges solved
        - courses_completed: Number of courses completed
        - streak_days: Consecutive days active
        - points_earned: Total points earned
        
        Args:
            db: Database session
            user_id: User ID
            milestone_type: Type of milestone reached
            value: Current value (e.g., 10 challenges solved)
        
        Returns:
            List of newly awarded badges
        """
        awarded_badges = []

        try:
            # Find relevant badges for this milestone
            condition_type_map = {
                'challenges_solved': BadgeConditionType.CHALLENGES_SOLVED,
                'courses_completed': BadgeConditionType.LANGUAGE_MASTER,
                'streak_days': BadgeConditionType.STREAK_DAYS,
                'points_earned': BadgeConditionType.POINTS_EARNED,
            }

            condition_type = condition_type_map.get(milestone_type)
            if not condition_type:
                return awarded_badges

            # Find badges with matching conditions
            badges_to_check = db.query(Badge).filter(
                and_(
                    Badge.condition_type == condition_type,
                    Badge.is_active == True,
                    Badge.condition_value <= value
                )
            ).all()

            for badge in badges_to_check:
                # Award if conditions met
                user_badge = BadgeService.award_badge(db, user_id, badge.id)
                if user_badge:
                    awarded_badges.append(user_badge)

        except Exception as e:
            logger.error(f"Error checking milestone badges: {str(e)}")

        return awarded_badges

    @staticmethod
    def update_badge_progress(
        db: Session,
        user_id: int,
        badge_id: int,
        current_value: int,
        target_value: int
    ) -> BadgeProgress:
        """
        Update progress toward a badge (e.g., 7/10 challenges)
        
        Args:
            db: Database session
            user_id: User ID
            badge_id: Badge ID
            current_value: Current progress value
            target_value: Target value needed
        
        Returns:
            BadgeProgress record
        """
        try:
            # Check existing progress
            progress = db.query(BadgeProgress).filter(
                and_(
                    BadgeProgress.user_id == user_id,
                    BadgeProgress.badge_id == badge_id
                )
            ).first()

            progress_percentage = (current_value / target_value * 100) if target_value > 0 else 0
            is_completed = current_value >= target_value

            if progress:
                progress.current_value = current_value
                progress.target_value = target_value
                progress.progress_percentage = progress_percentage
                progress.is_completed = is_completed
                if is_completed and not progress.completed_at:
                    progress.completed_at = datetime.utcnow()
                    # Award the badge when progress completes
                    BadgeService.award_badge(db, user_id, badge_id)
            else:
                progress = BadgeProgress(
                    user_id=user_id,
                    badge_id=badge_id,
                    current_value=current_value,
                    target_value=target_value,
                    progress_percentage=progress_percentage,
                    is_completed=is_completed,
                    completed_at=datetime.utcnow() if is_completed else None
                )
                db.add(progress)
                if is_completed:
                    BadgeService.award_badge(db, user_id, badge_id)

            db.commit()
            return progress

        except Exception as e:
            logger.error(f"Error updating badge progress: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def update_leaderboard(
        db: Session,
        user_id: int,
        badges_earned: int = 0,
        badge_id: int = None,
        challenges_solved: int = 0,
        points_earned: int = 0,
        contests_won: int = 0
    ):
        """
        Update leaderboard entry for user
        
        Args:
            db: Database session
            user_id: User ID
            badges_earned: Increment badge count
            badge_id: Badge ID for points calculation
            challenges_solved: Increment challenges count
            points_earned: Increment points count
            contests_won: Increment contests count
        """
        try:
            # Get or create leaderboard entry
            leaderboard = db.query(Leaderboard).filter(
                Leaderboard.user_id == user_id
            ).first()

            if not leaderboard:
                leaderboard = Leaderboard(user_id=user_id)
                db.add(leaderboard)

            # Update counts
            if badges_earned > 0:
                leaderboard.badges_earned = (leaderboard.badges_earned or 0) + badges_earned

            if challenges_solved > 0:
                leaderboard.challenges_solved = (leaderboard.challenges_solved or 0) + challenges_solved

            if contests_won > 0:
                leaderboard.contests_won = (leaderboard.contests_won or 0) + contests_won

            # Get badge points if badge_id provided
            if badge_id:
                badge = db.query(Badge).filter(Badge.id == badge_id).first()
                if badge and badge.points_value:
                    leaderboard.total_points = (leaderboard.total_points or 0) + badge.points_value
                    points_earned = badge.points_value

            if points_earned > 0:
                leaderboard.total_points = (leaderboard.total_points or 0) + points_earned

            leaderboard.updated_at = datetime.utcnow()
            db.commit()

        except Exception as e:
            logger.error(f"Error updating leaderboard: {str(e)}")
            db.rollback()

    @staticmethod
    def award_achievement(
        db: Session,
        user_id: int,
        achievement_id: int,
        context_data: dict = None
    ) -> UserAchievement | None:
        """
        Award an achievement to a user
        
        Args:
            db: Database session
            user_id: User ID
            achievement_id: Achievement ID
            context_data: Optional context (challenge_id, score, time, etc)
        
        Returns:
            UserAchievement record or None
        """
        try:
            # Check if already earned (achievements are one-time)
            existing = db.query(UserAchievement).filter(
                and_(
                    UserAchievement.user_id == user_id,
                    UserAchievement.achievement_id == achievement_id
                )
            ).first()

            if existing:
                logger.info(f"Achievement {achievement_id} already earned by user {user_id}")
                return existing

            # Create achievement record
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement_id,
                context_data=context_data or {},
                unlocked_at=datetime.utcnow()
            )
            db.add(user_achievement)

            # Update leaderboard
            achievement = db.query(Achievement).filter(
                Achievement.id == achievement_id
            ).first()
            if achievement:
                BadgeService.update_leaderboard(
                    db,
                    user_id,
                    points_earned=achievement.points or 0
                )

            db.commit()
            logger.info(f"Achievement {achievement_id} awarded to user {user_id}")
            return user_achievement

        except Exception as e:
            logger.error(f"Error awarding achievement: {str(e)}")
            db.rollback()
            return None

    @staticmethod
    def get_user_badges(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> list[UserBadge]:
        """Get all badges earned by a user"""
        return db.query(UserBadge).filter(
            UserBadge.user_id == user_id
        ).order_by(UserBadge.last_earned_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_leaderboard_position(
        db: Session,
        user_id: int
    ) -> dict:
        """Get user's leaderboard position and stats"""
        try:
            user_lb = db.query(Leaderboard).filter(
                Leaderboard.user_id == user_id
            ).first()

            if not user_lb:
                return {
                    'user_id': user_id,
                    'total_points': 0,
                    'badges_earned': 0,
                    'challenges_solved': 0,
                    'overall_rank': None
                }

            # Calculate rank
            rank = db.query(func.count(Leaderboard.id)).filter(
                Leaderboard.total_points > user_lb.total_points
            ).scalar() + 1

            return {
                'user_id': user_id,
                'total_points': user_lb.total_points or 0,
                'badges_earned': user_lb.badges_earned or 0,
                'challenges_solved': user_lb.challenges_solved or 0,
                'overall_rank': rank,
                'current_streak': user_lb.current_streak or 0,
                'longest_streak': user_lb.longest_streak or 0
            }

        except Exception as e:
            logger.error(f"Error getting leaderboard position: {str(e)}")
            return None
