"""
Team and Group Management Models
Supports team creation, membership, team-based contests, and shared statistics
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    JSON, Float, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
from app.core.db import Base


class TeamRole(str, Enum):
    """Roles within a team"""
    OWNER = "owner"  # Can manage team, invite members, delete team
    ADMIN = "admin"  # Can manage members, view analytics
    MENTOR = "mentor"  # Can view member progress, provide guidance
    MEMBER = "member"  # Regular team member


class TeamVisibility(str, Enum):
    """Team visibility settings"""
    PUBLIC = "public"  # Anyone can view and join
    PRIVATE = "private"  # Invitation only
    RESTRICTED = "restricted"  # Anyone can view but invite to join


class Team(Base):
    """
    Represents a team for group learning and competitions
    """
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Team settings
    visibility = Column(SQLEnum(TeamVisibility), default=TeamVisibility.PRIVATE)
    icon_emoji = Column(String(10), nullable=True)  # 🏆, 🎯, 👥, etc
    banner_url = Column(String(500), nullable=True)
    
    # Membership
    max_members = Column(Integer, default=50)  # -1 for unlimited
    member_count = Column(Integer, default=1)
    
    # Team statistics
    total_challenges_solved = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    # Features
    has_contests = Column(Boolean, default=False)  # Team can host contests
    has_analytics = Column(Boolean, default=True)  # Shared analytics
    
    # Metadata
    extra_data = Column(JSON, default={})  # Category, organization, goals, etc
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    invitations = relationship("TeamInvitation", back_populates="team", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_team_owner_created", "owner_id", "created_at"),
        Index("ix_team_visibility", "visibility"),
    )


class TeamMember(Base):
    """
    Represents a member of a team with their role and contribution
    """
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Role and permissions
    role = Column(SQLEnum(TeamRole), default=TeamRole.MEMBER)
    is_active = Column(Boolean, default=True)
    
    # Individual contribution tracking
    challenges_solved = Column(Integer, default=0)
    contests_won = Column(Integer, default=0)
    points_contributed = Column(Integer, default=0)
    
    # Activity
    last_active_at = Column(DateTime, nullable=True)
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", foreign_keys=[team_id], back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index("ix_team_member_unique", "team_id", "user_id", unique=True),
        Index("ix_team_member_role", "team_id", "role"),
    )


class TeamInvitation(Base):
    """
    Team membership invitations
    """
    __tablename__ = "team_invitations"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    invited_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    invited_by_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Invitation state
    status = Column(String(20), default="pending")  # "pending", "accepted", "rejected", "cancelled"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # Invitation expires after time
    
    # Relationships
    team = relationship("Team", foreign_keys=[team_id], back_populates="invitations")
    invited_user = relationship("User", foreign_keys=[invited_user_id])
    invited_by = relationship("User", foreign_keys=[invited_by_id])


class TeamChallenge(Base):
    """
    Challenges assigned to a team (team learning goals)
    """
    __tablename__ = "team_challenges"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(Integer, nullable=False)  # Reference to coding challenge
    
    # Assignment info
    assigned_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Deadline and status
    deadline = Column(DateTime, nullable=True)
    is_mandatory = Column(Boolean, default=False)
    
    # Completion tracking
    members_assigned = Column(Integer, default=0)
    members_completed = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", foreign_keys=[team_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])


class TeamStatistics(Base):
    """
    Aggregated statistics for a team (updated periodically)
    """
    __tablename__ = "team_statistics"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Overall stats
    total_members = Column(Integer, default=0)
    active_members = Column(Integer, default=0)
    total_challenges_solved = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    average_points_per_member = Column(Float, default=0.0)
    
    # Streak and milestones
    longest_streak = Column(Integer, default=0)
    total_contests = Column(Integer, default=0)
    contests_won = Column(Integer, default=0)
    
    # Member contribution breakdown
    top_contributor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    contribution_distribution = Column(JSON, default={})  # {"user_1": 0.3, "user_2": 0.25, ...}
    
    # Growth metrics
    growth_30_days = Column(Float, default=0.0)  # % change in points
    new_members_30_days = Column(Integer, default=0)
    
    # Last update
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", foreign_keys=[team_id])
    top_contributor = relationship("User", foreign_keys=[top_contributor_id])


class TeamContest(Base):
    """
    Team-based contests where multiple teams compete
    """
    __tablename__ = "team_contests"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    contest_id = Column(Integer, nullable=False)  # Reference to global contest
    
    # Participation
    registered_at = Column(DateTime, default=datetime.utcnow)
    final_score = Column(Integer, default=0)
    rank = Column(Integer, nullable=True)
    
    # Leaderboard position
    challenges_completed = Column(Integer, default=0)
    problems_solved = Column(Integer, default=0)
    time_penalty = Column(Integer, default=0)  # In minutes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    team = relationship("Team", foreign_keys=[team_id])


class TeamAnnouncement(Base):
    """
    Announcements within a team
    """
    __tablename__ = "team_announcements"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Content
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    announcement_type = Column(String(30), default="general")  # "general", "milestone", "contest", "deadline"
    
    # Pins and importance
    is_pinned = Column(Boolean, default=False)
    importance = Column(String(20), default="normal")  # "low", "normal", "high", "urgent"
    
    # Engagement
    view_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", foreign_keys=[team_id])
    author = relationship("User", foreign_keys=[author_id])
