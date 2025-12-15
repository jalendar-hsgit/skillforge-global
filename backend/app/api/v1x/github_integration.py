"""
GitHub Integration API router.
OAuth flow, repository syncing, and contribution tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import httpx

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.github_integration import (
    GitHubAccount, GitHubRepository, GitHubContribution, GitHubStats,
    GitHubConnectionStatus, ContributionType
)

router = APIRouter(prefix="/api/v1x/github", tags=["github_integration"])

GITHUB_API_BASE = "https://api.github.com"


# ===================== GitHub OAuth Flow =====================

@router.post("/connect")
def connect_github_account(
    auth_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Connect GitHub account using OAuth code.
    Client should redirect to: https://github.com/login/oauth/authorize
    """
    code = auth_data.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code required")
    
    # TODO: Exchange code for access token with GitHub OAuth
    # This is a skeleton - in production, call GitHub OAuth endpoint
    
    # For now, return a placeholder response
    return {
        "message": "GitHub connection initiated",
        "note": "OAuth integration requires GitHub app configuration"
    }


@router.get("/account")
def get_github_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's GitHub account connection"""
    account = db.query(GitHubAccount).filter(
        GitHubAccount.user_id == current_user.id
    ).first()
    
    if not account:
        return {"connected": False, "account": None}
    
    return {
        "connected": True,
        "account": _format_github_account(account)
    }


@router.post("/disconnect")
def disconnect_github_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disconnect GitHub account"""
    account = db.query(GitHubAccount).filter(
        GitHubAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="No GitHub account connected")
    
    # Delete account and related data
    db.delete(account)
    db.commit()
    
    return {"message": "GitHub account disconnected"}


# ===================== Repository Management =====================

@router.get("/repositories")
def list_user_repositories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """List user's synced GitHub repositories"""
    account = db.query(GitHubAccount).filter(
        GitHubAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="No GitHub account connected")
    
    total = db.query(GitHubRepository).filter(
        GitHubRepository.account_id == account.id
    ).count()
    
    repos = db.query(GitHubRepository).filter(
        GitHubRepository.account_id == account.id
    ).order_by(GitHubRepository.stars_count.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "repositories": [_format_repository(repo) for repo in repos]
    }


@router.get("/repositories/{repo_id}")
def get_repository_details(
    repo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a repository"""
    account = db.query(GitHubAccount).filter(
        GitHubAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="No GitHub account connected")
    
    repo = db.query(GitHubRepository).filter(
        GitHubRepository.id == repo_id,
        GitHubRepository.account_id == account.id
    ).first()
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Get contributions to this repo
    contributions = db.query(GitHubContribution).filter(
        GitHubContribution.repository_id == repo_id
    ).count()
    
    return {
        "repository": _format_repository(repo),
        "contributions": contributions
    }


@router.post("/sync-repositories")
def sync_repositories(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger repository sync from GitHub"""
    account = db.query(GitHubAccount).filter(
        GitHubAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="No GitHub account connected")
    
    # Add background task to sync
    background_tasks.add_task(_sync_repositories_background, account.id, db)
    
    return {
        "message": "Repository sync started",
        "status": "in_progress"
    }


# ===================== Contributions & Activity =====================

@router.get("/contributions")
def get_contributions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    contribution_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get user's GitHub contributions"""
    account = db.query(GitHubAccount).filter(
        GitHubAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="No GitHub account connected")
    
    query = db.query(GitHubContribution).filter(
        GitHubContribution.account_id == account.id
    )
    
    if contribution_type:
        try:
            query = query.filter(GitHubContribution.contribution_type == ContributionType(contribution_type))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid contribution type: {contribution_type}")
    
    total = query.count()
    contributions = query.order_by(GitHubContribution.contributed_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "contributions": [_format_contribution(c) for c in contributions]
    }


@router.get("/stats")
def get_github_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get aggregated GitHub statistics"""
    account = db.query(GitHubAccount).filter(
        GitHubAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="No GitHub account connected")
    
    stats = db.query(GitHubStats).filter(
        GitHubStats.account_id == account.id
    ).first()
    
    if not stats:
        # Create default stats
        stats = GitHubStats(account_id=account.id)
        db.add(stats)
        db.commit()
    
    return {
        "stats": _format_github_stats(stats),
        "account": _format_github_account(account)
    }


@router.post("/sync-contributions")
def sync_contributions(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger contribution sync from GitHub"""
    account = db.query(GitHubAccount).filter(
        GitHubAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="No GitHub account connected")
    
    # Add background task
    background_tasks.add_task(_sync_contributions_background, account.id, db)
    
    return {
        "message": "Contribution sync started",
        "status": "in_progress"
    }


# ===================== Settings =====================

@router.put("/settings")
def update_sync_settings(
    settings_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update GitHub sync settings"""
    account = db.query(GitHubAccount).filter(
        GitHubAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="No GitHub account connected")
    
    account.auto_sync_enabled = settings_data.get("auto_sync_enabled", account.auto_sync_enabled)
    account.sync_interval_hours = settings_data.get("sync_interval_hours", account.sync_interval_hours)
    
    db.commit()
    db.refresh(account)
    
    return {
        "message": "Settings updated",
        "account": _format_github_account(account)
    }


# ===================== Public Profiles =====================

@router.get("/profile/{username}")
def get_public_github_profile(
    username: str,
    db: Session = Depends(get_db)
):
    """Get public GitHub profile (for displaying on user profiles)"""
    account = db.query(GitHubAccount).filter(
        GitHubAccount.github_username == username
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="GitHub account not found")
    
    stats = db.query(GitHubStats).filter(
        GitHubStats.account_id == account.id
    ).first()
    
    return {
        "profile": _format_github_account(account),
        "stats": _format_github_stats(stats) if stats else None,
        "repository_count": db.query(GitHubRepository).filter(
            GitHubRepository.account_id == account.id
        ).count()
    }


# ===================== Helper Functions =====================

def _format_github_account(account):
    """Format GitHub account for API response"""
    return {
        "id": account.id,
        "github_username": account.github_username,
        "github_user_id": account.github_user_id,
        "github_name": account.github_name,
        "github_bio": account.github_bio,
        "github_avatar_url": account.github_avatar_url,
        "github_profile_url": account.github_profile_url,
        "github_company": account.github_company,
        "github_location": account.github_location,
        "public_repos_count": account.public_repos_count,
        "followers_count": account.followers_count,
        "following_count": account.following_count,
        "status": account.status.value,
        "connected_at": account.connected_at.isoformat(),
        "last_synced_at": account.last_synced_at.isoformat() if account.last_synced_at else None
    }


def _format_repository(repo):
    """Format GitHub repository for API response"""
    return {
        "id": repo.id,
        "repo_name": repo.repo_name,
        "repo_full_name": repo.repo_full_name,
        "repo_description": repo.repo_description,
        "repo_url": repo.repo_url,
        "stars_count": repo.stars_count,
        "forks_count": repo.forks_count,
        "watchers_count": repo.watchers_count,
        "open_issues_count": repo.open_issues_count,
        "primary_language": repo.primary_language,
        "is_fork": repo.is_fork,
        "is_private": repo.is_private,
        "total_commits": repo.total_commits,
        "user_commits": repo.user_commits,
        "pushed_at": repo.pushed_at.isoformat() if repo.pushed_at else None
    }


def _format_contribution(contrib):
    """Format GitHub contribution for API response"""
    return {
        "id": contrib.id,
        "type": contrib.contribution_type.value,
        "title": contrib.title,
        "description": contrib.description,
        "additions": contrib.additions,
        "deletions": contrib.deletions,
        "contribution_url": contrib.contribution_url,
        "contributed_at": contrib.contributed_at.isoformat()
    }


def _format_github_stats(stats):
    """Format GitHub stats for API response"""
    return {
        "id": stats.id,
        "total_contributions": stats.total_contributions,
        "contributions_this_year": stats.contributions_this_year,
        "contributions_this_month": stats.contributions_this_month,
        "commits_count": stats.commits_count,
        "pull_requests_count": stats.pull_requests_count,
        "issues_count": stats.issues_count,
        "code_reviews_count": stats.code_reviews_count,
        "top_languages": stats.top_languages,
        "current_streak_days": stats.current_streak_days,
        "longest_streak_days": stats.longest_streak_days,
        "activity_level": stats.activity_level,
        "calculated_at": stats.calculated_at.isoformat()
    }


async def _sync_repositories_background(account_id: int, db: Session):
    """Background task to sync repositories from GitHub API"""
    # TODO: Implement GitHub API call to fetch user's repositories
    # This would call GitHub API and update GitHubRepository records
    pass


async def _sync_contributions_background(account_id: int, db: Session):
    """Background task to sync contributions from GitHub API"""
    # TODO: Implement GitHub API call to fetch user's contributions
    # This would call GitHub API and update GitHubContribution records
    pass
