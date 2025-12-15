"""Contest and competition management models."""
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.db import Base


class ContestStatus(str, Enum):
    """Contest status enum."""
    DRAFT = "draft"
    UPCOMING = "upcoming"
    ACTIVE = "active"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class ContestType(str, Enum):
    """Contest type enum."""
    INDIVIDUAL = "individual"
    TEAM = "team"
    RELAY = "relay"


class Contest(Base):
    """Programming contests and competitions."""
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True)
    
    # Basic info
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    rules = Column(Text, nullable=True)
    
    # Contest type and settings
    contest_type = Column(SQLEnum(ContestType), default=ContestType.INDIVIDUAL, nullable=False)
    difficulty = Column(String(50), default="medium")  # easy, medium, hard, expert
    category = Column(String(100), nullable=False)  # dsa, web, ml, etc
    
    # Timing
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    registration_deadline = Column(DateTime, nullable=False)
    
    # Status and visibility
    status = Column(SQLEnum(ContestStatus), default=ContestStatus.DRAFT, nullable=False, index=True)
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Pricing and prizes
    entry_fee = Column(Integer, default=0)  # 0 = free
    total_prize_pool = Column(Integer, default=0)  # In coins
    
    # Constraints
    max_participants = Column(Integer, nullable=True)  # None = unlimited
    min_skill_level = Column(Integer, default=0)  # 0-100 rating
    
    # Metadata
    banner_image = Column(String(255), nullable=True)
    tags = Column(JSON, default={})
    rules_content = Column(JSON, default={})  # Store rules as structured data
    
    # Stats
    total_participants = Column(Integer, default=0)
    total_submissions = Column(Integer, default=0)
    
    # Creator
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", backref="contests_created")
    participants = relationship("ContestParticipant", backref="contest", cascade="all, delete-orphan")
    challenges = relationship("ContestChallenge", backref="contest", cascade="all, delete-orphan")
    leaderboard = relationship("ContestLeaderboard", backref="contest", cascade="all, delete-orphan")
    submissions = relationship("ContestSubmission", backref="contest", cascade="all, delete-orphan")
    prizes = relationship("ContestPrize", backref="contest", cascade="all, delete-orphan")
    teams = relationship("ContestTeam", backref="contest", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Contest(id={self.id}, title={self.title}, status={self.status})>"


class ContestChallenge(Base):
    """Challenges included in a contest."""
    __tablename__ = "contest_challenges"

    id = Column(Integer, primary_key=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id"), nullable=False, index=True)
    
    # Ordering
    order = Column(Integer, default=0)
    
    # Points
    points = Column(Integer, default=100)
    time_limit_seconds = Column(Integer, default=5)
    memory_limit_mb = Column(Integer, default=256)
    
    # Settings
    is_required = Column(Boolean, default=True)
    show_test_cases = Column(Boolean, default=True)
    allow_hints = Column(Boolean, default=True)
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    challenge = relationship("CodingChallenge", backref="contest_challenges")
    
    def __repr__(self):
        return f"<ContestChallenge(contest_id={self.contest_id}, challenge_id={self.challenge_id}, points={self.points})>"


class ContestParticipant(Base):
    """Tracks user participation in contests."""
    __tablename__ = "contest_participants"

    id = Column(Integer, primary_key=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("contest_teams.id"), nullable=True)
    
    # Participation status
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    withdrew_at = Column(DateTime, nullable=True)
    
    # Score tracking
    total_points = Column(Integer, default=0)
    challenges_solved = Column(Integer, default=0)
    last_submission_time = Column(DateTime, nullable=True)
    
    # Ranking
    rank = Column(Integer, nullable=True)
    percentile = Column(Float, nullable=True)
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="contest_participations")
    
    def __repr__(self):
        return f"<ContestParticipant(user_id={self.user_id}, contest_id={self.contest_id}, points={self.total_points})>"


class ContestSubmission(Base):
    """User code submissions during contests."""
    __tablename__ = "contest_submissions"

    id = Column(Integer, primary_key=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id"), nullable=False, index=True)
    
    # Code
    code = Column(Text, nullable=False)
    language = Column(String(50), default="python", nullable=False)
    
    # Execution
    status = Column(String(50), default="pending")  # pending, running, passed, failed, error
    test_cases_passed = Column(Integer, default=0)
    test_cases_total = Column(Integer, default=0)
    execution_time_ms = Column(Integer, nullable=True)
    memory_used_mb = Column(Integer, nullable=True)
    
    # Results
    points_earned = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    compilation_log = Column(Text, nullable=True)
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow)
    evaluated_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="contest_submissions")
    challenge = relationship("CodingChallenge", backref="contest_submissions")
    
    def __repr__(self):
        return f"<ContestSubmission(user_id={self.user_id}, challenge_id={self.challenge_id}, status={self.status})>"


class ContestLeaderboard(Base):
    """Real-time leaderboard for contests."""
    __tablename__ = "contest_leaderboard"

    id = Column(Integer, primary_key=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Ranking
    rank = Column(Integer, nullable=False, index=True)
    score = Column(Integer, default=0)
    penalties = Column(Integer, default=0)  # Time penalties, wrong submissions
    
    # Challenge completion
    challenges_solved = Column(Integer, default=0)
    last_accepted_time = Column(DateTime, nullable=True)
    
    # Streak
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    
    # Performance
    accuracy = Column(Float, default=0.0)  # Percentage of correct submissions
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="contest_leaderboards")
    
    def __repr__(self):
        return f"<ContestLeaderboard(contest_id={self.contest_id}, rank={self.rank}, score={self.score})>"


class ContestPrize(Base):
    """Prize distribution for contests."""
    __tablename__ = "contest_prizes"

    id = Column(Integer, primary_key=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    
    # Ranking
    rank_min = Column(Integer, nullable=False)  # e.g., 1
    rank_max = Column(Integer, nullable=False)  # e.g., 1 for 1st place, 5 for top 5
    
    # Prize details
    title = Column(String(255), nullable=False)  # "First Place", "Top 5", etc
    coins_reward = Column(Integer, default=0)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=True)
    certificate = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    badge = relationship("Badge", backref="contest_prizes")
    
    def __repr__(self):
        return f"<ContestPrize(contest_id={self.contest_id}, rank={self.rank_min}-{self.rank_max})>"


class ContestTeam(Base):
    """Teams for team-based contests."""
    __tablename__ = "contest_teams"

    id = Column(Integer, primary_key=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    
    # Team info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Members
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    max_members = Column(Integer, default=5)
    member_count = Column(Integer, default=1)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Stats
    total_points = Column(Integer, default=0)
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leader = relationship("User", foreign_keys=[leader_id], backref="contest_teams_led")
    participants = relationship("ContestParticipant", backref="team")
    
    def __repr__(self):
        return f"<ContestTeam(contest_id={self.contest_id}, name={self.name}, members={self.member_count})>"


class ContestRound(Base):
    """Multi-round contests."""
    __tablename__ = "contest_rounds"

    id = Column(Integer, primary_key=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    
    # Round info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    round_number = Column(Integer, nullable=False)
    
    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=False)
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ContestRound(contest_id={self.contest_id}, round={self.round_number})>"
