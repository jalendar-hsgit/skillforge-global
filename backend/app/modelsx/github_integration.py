"""
GitHub Integration models for linking accounts and tracking activity.
- GitHubAccount: User's GitHub profile connection
- GitHubRepository: Synced GitHub repositories
- GitHubContribution: Tracked contributions and activity
- GitHubStats: Aggregated GitHub statistics
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.db import Base


class GitHubConnectionStatus(str, Enum):
    """Status of GitHub account connection"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"
    ERROR = "error"


class ContributionType(str, Enum):
    """Types of GitHub contributions"""
    COMMIT = "commit"
    PULL_REQUEST = "pull_request"
    ISSUE = "issue"
    CODE_REVIEW = "code_review"
    DISCUSSION = "discussion"
    REPOSITORY = "repository"


class GitHubAccount(Base):
    """User's GitHub account connection"""
    __tablename__ = "github_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # GitHub OAuth info
    github_username = Column(String(255), nullable=False, unique=True)
    github_user_id = Column(Integer, nullable=False, unique=True)
    github_access_token = Column(String(500), nullable=True)  # Encrypted in production
    github_refresh_token = Column(String(500), nullable=True)
    
    # Profile info
    github_name = Column(String(255), nullable=True)
    github_bio = Column(Text, nullable=True)
    github_avatar_url = Column(String(500), nullable=True)
    github_profile_url = Column(String(500), nullable=True)
    github_company = Column(String(255), nullable=True)
    github_location = Column(String(255), nullable=True)
    github_blog = Column(String(500), nullable=True)
    
    # Stats
    public_repos_count = Column(Integer, default=0)
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    public_gists_count = Column(Integer, default=0)
    
    # Connection status
    status = Column(SQLEnum(GitHubConnectionStatus), default=GitHubConnectionStatus.CONNECTED)
    
    # Sync info
    last_synced_at = Column(DateTime, nullable=True)
    sync_error_message = Column(Text, nullable=True)
    
    # Settings
    auto_sync_enabled = Column(Boolean, default=True)
    sync_interval_hours = Column(Integer, default=24)
    
    # Timestamps
    connected_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="github_account")
    repositories = relationship("GitHubRepository", back_populates="account", cascade="all, delete-orphan")
    contributions = relationship("GitHubContribution", back_populates="account", cascade="all, delete-orphan")
    stats = relationship("GitHubStats", back_populates="account", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<GitHubAccount(user_id={self.user_id}, github_user={self.github_username})>"


class GitHubRepository(Base):
    """Synced GitHub repository information"""
    __tablename__ = "github_repositories"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("github_accounts.id"), nullable=False)
    
    # Repository info
    github_repo_id = Column(Integer, nullable=False)
    repo_name = Column(String(255), nullable=False)
    repo_full_name = Column(String(511), nullable=False)  # owner/repo_name
    repo_description = Column(Text, nullable=True)
    repo_url = Column(String(500), nullable=False)
    
    # Repository stats
    stars_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    watchers_count = Column(Integer, default=0)
    open_issues_count = Column(Integer, default=0)
    
    # Language & Type
    primary_language = Column(String(100), nullable=True)
    languages = Column(JSON, default={})  # {"Python": 45, "JavaScript": 55}
    is_fork = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)
    
    # Commits
    total_commits = Column(Integer, default=0)
    user_commits = Column(Integer, default=0)
    
    # Dates
    created_at_github = Column(DateTime, nullable=True)
    updated_at_github = Column(DateTime, nullable=True)
    pushed_at = Column(DateTime, nullable=True)
    
    # Sync
    synced_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("GitHubAccount", back_populates="repositories")
    
    def __repr__(self):
        return f"<GitHubRepository(repo={self.repo_full_name}, owner_id={self.account_id})>"


class GitHubContribution(Base):
    """GitHub contribution tracking"""
    __tablename__ = "github_contributions"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("github_accounts.id"), nullable=False)
    repository_id = Column(Integer, ForeignKey("github_repositories.id"), nullable=True)
    
    # Contribution info
    contribution_type = Column(SQLEnum(ContributionType), nullable=False)
    github_id = Column(String(255), nullable=False)  # Unique identifier in GitHub
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    # Stats
    additions = Column(Integer, default=0)  # Lines added
    deletions = Column(Integer, default=0)  # Lines deleted
    
    # Links
    contribution_url = Column(String(500), nullable=True)
    
    # Date
    contributed_at = Column(DateTime, nullable=False)
    
    # Extra Data
    extra_data = Column(JSON, default={})  # Extra data for each type
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("GitHubAccount", back_populates="contributions")
    
    def __repr__(self):
        return f"<GitHubContribution(type={self.contribution_type}, account_id={self.account_id})>"


class GitHubStats(Base):
    """Aggregated GitHub statistics"""
    __tablename__ = "github_stats"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("github_accounts.id"), nullable=False, unique=True)
    
    # Contribution stats
    total_contributions = Column(Integer, default=0)
    contributions_this_year = Column(Integer, default=0)
    contributions_this_month = Column(Integer, default=0)
    
    # Breakdown
    commits_count = Column(Integer, default=0)
    pull_requests_count = Column(Integer, default=0)
    issues_count = Column(Integer, default=0)
    code_reviews_count = Column(Integer, default=0)
    
    # Top languages
    top_languages = Column(JSON, default=[])  # [{"name": "Python", "percentage": 45}, ...]
    
    # Streaks
    current_streak_days = Column(Integer, default=0)
    longest_streak_days = Column(Integer, default=0)
    
    # Activity level (0-10 scale)
    activity_level = Column(Integer, default=0)
    
    # Last calculated
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("GitHubAccount", back_populates="stats")
    
    def __repr__(self):
        return f"<GitHubStats(account_id={self.account_id}, contributions={self.total_contributions})>"
