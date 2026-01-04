"""
Team Management API endpoints
Supports team creation, member management, team-based challenges, and shared statistics
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.core.security import get_current_user
from app.core.db import get_db
from app.modelsx.teams import (
    Team, TeamMember, TeamInvitation, TeamChallenge,
    TeamStatistics, TeamContest, TeamAnnouncement,
    TeamRole, TeamVisibility
)
from app.models.user import User
from app.schemas.teams import (
    TeamCreate, TeamUpdate, TeamResponse, TeamDetailResponse,
    TeamMemberCreate, TeamMemberUpdate, TeamMemberResponse, TeamMemberDetailResponse,
    TeamInvitationCreate, TeamInvitationResponse, TeamInvitationDetailResponse,
    TeamChallengeCreate, TeamChallengeResponse,
    TeamStatisticsResponse, TeamLeaderboardResponse,
    TeamContestCreate, TeamContestResponse,
    TeamAnnouncementCreate, TeamAnnouncementUpdate,
    TeamAnnouncementResponse, TeamAnnouncementDetailResponse,
    TeamsListResponse, TeamMembersListResponse, TeamInvitationsListResponse,
    TeamDiscoveryResponse, TeamJoinResponse, TeamStatsOverviewResponse
)

router = APIRouter(prefix="/teams", tags=["teams"])


# Team CRUD Endpoints
@router.post("", response_model=TeamResponse)
def create_team(
    team: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new team"""
    # Check if slug already exists
    existing = db.query(Team).filter(Team.slug == team.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Team slug already exists")
    
    new_team = Team(
        name=team.name,
        slug=team.slug,
        description=team.description,
        owner_id=current_user.id,
        visibility=team.visibility,
        icon_emoji=team.icon_emoji,
        banner_url=team.banner_url,
        max_members=team.max_members,
        has_contests=team.has_contests,
        has_analytics=team.has_analytics
    )
    
    db.add(new_team)
    db.flush()
    
    # Add owner as member with owner role
    owner_member = TeamMember(
        team_id=new_team.id,
        user_id=current_user.id,
        role=TeamRole.OWNER
    )
    db.add(owner_member)
    new_team.member_count = 1
    
    # Create team statistics
    team_stats = TeamStatistics(team_id=new_team.id)
    db.add(team_stats)
    
    db.commit()
    db.refresh(new_team)
    return new_team


@router.get("/discover", response_model=List[TeamDiscoveryResponse])
def discover_teams(
    visibility: Optional[str] = None,
    sort_by: str = Query("members", pattern="^(members|points|rating)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Discover public/restricted teams"""
    query = db.query(Team).filter(
        Team.visibility.in_([TeamVisibility.PUBLIC, TeamVisibility.RESTRICTED]),
        Team.deleted_at == None
    )
    
    # Sort
    if sort_by == "members":
        query = query.order_by(desc(Team.member_count))
    elif sort_by == "points":
        query = query.order_by(desc(Team.total_points))
    elif sort_by == "rating":
        query = query.order_by(desc(Team.average_rating))
    
    teams = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return [
        TeamDiscoveryResponse(
            id=t.id,
            name=t.name,
            slug=t.slug,
            icon_emoji=t.icon_emoji,
            description=t.description,
            member_count=t.member_count,
            total_points=t.total_points,
            average_rating=t.average_rating,
            visibility=t.visibility
        )
        for t in teams
    ]


@router.get("/{team_slug}", response_model=TeamDetailResponse)
def get_team(
    team_slug: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team details"""
    team = db.query(Team).filter(
        Team.slug == team_slug,
        Team.deleted_at == None
    ).first()
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check visibility
    if team.visibility == TeamVisibility.PRIVATE:
        if not current_user or not db.query(TeamMember).filter(
            TeamMember.team_id == team.id,
            TeamMember.user_id == current_user.id
        ).first():
            raise HTTPException(status_code=403, detail="Not authorized to view this team")
    
    owner = db.query(User).filter(User.id == team.owner_id).first()
    members = db.query(TeamMember).filter(TeamMember.team_id == team.id).all()
    
    return TeamDetailResponse(
        id=team.id,
        name=team.name,
        slug=team.slug,
        description=team.description,
        owner_id=team.owner_id,
        owner_username=owner.username if owner else "unknown",
        visibility=team.visibility,
        icon_emoji=team.icon_emoji,
        banner_url=team.banner_url,
        max_members=team.max_members,
        member_count=team.member_count,
        total_challenges_solved=team.total_challenges_solved,
        total_points=team.total_points,
        average_rating=team.average_rating,
        has_contests=team.has_contests,
        has_analytics=team.has_analytics,
        created_at=team.created_at,
        updated_at=team.updated_at,
        members=[
            TeamMemberResponse(
                id=m.id,
                team_id=m.team_id,
                user_id=m.user_id,
                role=m.role,
                is_active=m.is_active,
                challenges_solved=m.challenges_solved,
                contests_won=m.contests_won,
                points_contributed=m.points_contributed,
                last_active_at=m.last_active_at,
                joined_at=m.joined_at
            )
            for m in members
        ]
    )


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    update: TeamUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update team (owner only)"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only team owner can update")
    
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(team, field, value)
    
    db.commit()
    db.refresh(team)
    return team


@router.delete("/{team_id}")
def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete team (owner only) - soft delete"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only team owner can delete")
    
    team.deleted_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Team deleted", "team_id": team_id}


# Team Member Endpoints
@router.get("/{team_id}/members", response_model=TeamMembersListResponse)
def get_team_members(
    team_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team members with leaderboard"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check authorization
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not member and team.visibility == TeamVisibility.PRIVATE:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.is_active == True
    ).order_by(desc(TeamMember.points_contributed))
    
    total_count = query.count()
    members = query.offset((page - 1) * page_size).limit(page_size).all()
    
    result_members = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        result_members.append(TeamMemberDetailResponse(
            id=m.id,
            team_id=m.team_id,
            user_id=m.user_id,
            username=user.username if user else "unknown",
            avatar_url=getattr(user, 'avatar_url', None) if user else None,
            role=m.role,
            is_active=m.is_active,
            challenges_solved=m.challenges_solved,
            contests_won=m.contests_won,
            points_contributed=m.points_contributed,
            last_active_at=m.last_active_at,
            joined_at=m.joined_at
        ))
    
    return TeamMembersListResponse(
        members=result_members,
        total_count=total_count,
        page=page,
        page_size=page_size
    )


@router.post("/{team_id}/members/{user_id}", response_model=TeamMemberResponse)
def add_team_member(
    team_id: int,
    user_id: int,
    member_create: TeamMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add member to team (admin/owner)"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check authorization
    auth_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.role.in_([TeamRole.OWNER, TeamRole.ADMIN])
    ).first()
    
    if not auth_member:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if member already exists
    existing = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User already member of team")
    
    # Check team capacity
    if team.max_members > 0 and team.member_count >= team.max_members:
        raise HTTPException(status_code=400, detail="Team is full")
    
    new_member = TeamMember(
        team_id=team_id,
        user_id=user_id,
        role=member_create.role
    )
    
    db.add(new_member)
    team.member_count += 1
    db.commit()
    db.refresh(new_member)
    
    return new_member


@router.put("/{team_id}/members/{member_id}", response_model=TeamMemberResponse)
def update_team_member(
    team_id: int,
    member_id: int,
    update: TeamMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update member role (owner/admin)"""
    member = db.query(TeamMember).filter(
        TeamMember.id == member_id,
        TeamMember.team_id == team_id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Check authorization
    auth_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.role.in_([TeamRole.OWNER, TeamRole.ADMIN])
    ).first()
    
    if not auth_member:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)
    
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{team_id}/members/{member_id}")
def remove_team_member(
    team_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove member from team (owner/admin or self)"""
    member = db.query(TeamMember).filter(
        TeamMember.id == member_id,
        TeamMember.team_id == team_id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Check authorization
    is_self = member.user_id == current_user.id
    auth_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.role.in_([TeamRole.OWNER, TeamRole.ADMIN])
    ).first()
    
    if not is_self and not auth_member:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(member)
    team = db.query(Team).filter(Team.id == team_id).first()
    if team:
        team.member_count = max(0, team.member_count - 1)
    
    db.commit()
    return {"message": "Member removed", "member_id": member_id}


# Team Invitation Endpoints
@router.post("/{team_id}/invitations", response_model=TeamInvitationResponse)
def invite_to_team(
    team_id: int,
    invitation: TeamInvitationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite user to team (admin/owner)"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check authorization
    auth_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.role.in_([TeamRole.OWNER, TeamRole.ADMIN])
    ).first()
    
    if not auth_member:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if already member
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == invitation.invited_user_id
    ).first()
    
    if existing_member:
        raise HTTPException(status_code=400, detail="User already member")
    
    # Check for pending invitation
    pending = db.query(TeamInvitation).filter(
        TeamInvitation.team_id == team_id,
        TeamInvitation.invited_user_id == invitation.invited_user_id,
        TeamInvitation.status == "pending"
    ).first()
    
    if pending:
        raise HTTPException(status_code=400, detail="Pending invitation already exists")
    
    expires_at = invitation.expires_at or (datetime.utcnow() + timedelta(days=7))
    
    new_invitation = TeamInvitation(
        team_id=team_id,
        invited_user_id=invitation.invited_user_id,
        invited_by_id=current_user.id,
        expires_at=expires_at
    )
    
    db.add(new_invitation)
    db.commit()
    db.refresh(new_invitation)
    
    return new_invitation


@router.get("/invitations", response_model=TeamInvitationsListResponse)
def get_pending_invitations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending team invitations for current user"""
    invitations = db.query(TeamInvitation).filter(
        TeamInvitation.invited_user_id == current_user.id,
        TeamInvitation.status == "pending",
        TeamInvitation.expires_at > datetime.utcnow()
    ).all()
    
    result = []
    for inv in invitations:
        team = db.query(Team).filter(Team.id == inv.team_id).first()
        invited_by = db.query(User).filter(User.id == inv.invited_by_id).first()
        
        result.append(TeamInvitationDetailResponse(
            id=inv.id,
            team_id=inv.team_id,
            team_name=team.name if team else "unknown",
            team_icon=team.icon_emoji if team else None,
            invited_user_id=inv.invited_user_id,
            invited_by_id=inv.invited_by_id,
            invited_by_username=invited_by.username if invited_by else "unknown",
            status=inv.status,
            created_at=inv.created_at,
            responded_at=inv.responded_at,
            expires_at=inv.expires_at
        ))
    
    return TeamInvitationsListResponse(
        invitations=result,
        total_count=len(result),
        pending_count=len(result)
    )


@router.post("/invitations/{invitation_id}/accept", response_model=TeamJoinResponse)
def accept_invitation(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept team invitation"""
    invitation = db.query(TeamInvitation).filter(
        TeamInvitation.id == invitation_id
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    if invitation.invited_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if invitation.status != "pending":
        raise HTTPException(status_code=400, detail="Invitation already responded")
    
    if invitation.expires_at and invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation expired")
    
    # Add user to team
    team = db.query(Team).filter(Team.id == invitation.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check team capacity
    if team.max_members > 0 and team.member_count >= team.max_members:
        raise HTTPException(status_code=400, detail="Team is full")
    
    member = TeamMember(
        team_id=invitation.team_id,
        user_id=current_user.id,
        role=TeamRole.MEMBER
    )
    
    db.add(member)
    team.member_count += 1
    
    invitation.status = "accepted"
    invitation.responded_at = datetime.utcnow()
    
    db.commit()
    
    return TeamJoinResponse(
        success=True,
        message="Successfully joined team",
        team_id=team.id,
        membership_id=member.id
    )


@router.post("/invitations/{invitation_id}/reject")
def reject_invitation(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject team invitation"""
    invitation = db.query(TeamInvitation).filter(
        TeamInvitation.id == invitation_id
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    if invitation.invited_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    invitation.status = "rejected"
    invitation.responded_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Invitation rejected", "invitation_id": invitation_id}


# Team Statistics Endpoints
@router.get("/{team_id}/statistics", response_model=TeamStatisticsResponse)
def get_team_statistics(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team statistics"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    stats = db.query(TeamStatistics).filter(
        TeamStatistics.team_id == team_id
    ).first()
    
    if not stats:
        stats = TeamStatistics(team_id=team_id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    
    return stats


@router.get("/{team_id}/leaderboard", response_model=List[TeamLeaderboardResponse])
def get_team_leaderboard(
    team_id: int,
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team leaderboard"""
    members = db.query(TeamMember).filter(
        TeamMember.team_id == team_id
    ).order_by(desc(TeamMember.points_contributed)).limit(limit).all()
    
    leaderboard = []
    for rank, member in enumerate(members, 1):
        user = db.query(User).filter(User.id == member.user_id).first()
        leaderboard.append(TeamLeaderboardResponse(
            rank=rank,
            member_id=member.id,
            username=user.username if user else "unknown",
            points=member.points_contributed,
            challenges_solved=member.challenges_solved,
            contests_won=member.contests_won,
            last_active_at=member.last_active_at
        ))
    
    return leaderboard


# Team Challenges Endpoints
@router.post("/{team_id}/challenges", response_model=TeamChallengeResponse)
def assign_challenge_to_team(
    team_id: int,
    challenge: TeamChallengeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign challenge to team (admin/mentor)"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check authorization
    auth_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.role.in_([TeamRole.OWNER, TeamRole.ADMIN, TeamRole.MENTOR])
    ).first()
    
    if not auth_member:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    team_challenge = TeamChallenge(
        team_id=team_id,
        challenge_id=challenge.challenge_id,
        assigned_by_id=current_user.id,
        deadline=challenge.deadline,
        is_mandatory=challenge.is_mandatory,
        members_assigned=team.member_count
    )
    
    db.add(team_challenge)
    db.commit()
    db.refresh(team_challenge)
    
    return team_challenge


@router.get("/{team_id}/challenges", response_model=List[TeamChallengeResponse])
def get_team_challenges(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get challenges assigned to team"""
    challenges = db.query(TeamChallenge).filter(
        TeamChallenge.team_id == team_id
    ).all()
    
    return challenges


# Team Announcements Endpoints
@router.post("/{team_id}/announcements", response_model=TeamAnnouncementResponse)
def create_announcement(
    team_id: int,
    announcement: TeamAnnouncementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create team announcement (admin/owner)"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check authorization
    auth_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.role.in_([TeamRole.OWNER, TeamRole.ADMIN])
    ).first()
    
    if not auth_member:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_announcement = TeamAnnouncement(
        team_id=team_id,
        author_id=current_user.id,
        title=announcement.title,
        content=announcement.content,
        announcement_type=announcement.announcement_type,
        is_pinned=announcement.is_pinned,
        importance=announcement.importance
    )
    
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    
    return new_announcement


@router.get("/{team_id}/announcements", response_model=List[TeamAnnouncementDetailResponse])
def get_announcements(
    team_id: int,
    sort_by: str = Query("recent", pattern="^(recent|pinned|important)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team announcements"""
    query = db.query(TeamAnnouncement).filter(
        TeamAnnouncement.team_id == team_id
    )
    
    if sort_by == "pinned":
        query = query.order_by(desc(TeamAnnouncement.is_pinned))
    elif sort_by == "important":
        query = query.order_by(desc(TeamAnnouncement.importance))
    
    query = query.order_by(desc(TeamAnnouncement.created_at))
    announcements = query.all()
    
    results = []
    for ann in announcements:
        author = db.query(User).filter(User.id == ann.author_id).first()
        results.append(TeamAnnouncementDetailResponse(
            id=ann.id,
            team_id=ann.team_id,
            author_id=ann.author_id,
            author_username=author.username if author else "unknown",
            author_avatar=getattr(author, 'avatar_url', None) if author else None,
            title=ann.title,
            content=ann.content,
            announcement_type=ann.announcement_type,
            is_pinned=ann.is_pinned,
            importance=ann.importance,
            view_count=ann.view_count,
            created_at=ann.created_at,
            updated_at=ann.updated_at
        ))
    
    return results


# User Team Stats
@router.get("/user/stats", response_model=TeamStatsOverviewResponse)
def get_user_team_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's team statistics overview"""
    total_teams = db.query(TeamMember).filter(
        TeamMember.user_id == current_user.id
    ).count()
    
    teams_owned = db.query(Team).filter(
        Team.owner_id == current_user.id
    ).count()
    
    teams_member = total_teams - teams_owned
    
    active_teams = db.query(TeamMember).filter(
        TeamMember.user_id == current_user.id,
        TeamMember.is_active == True
    ).count()
    
    total_points = db.query(TeamMember).filter(
        TeamMember.user_id == current_user.id
    ).with_entities(
        db.func.sum(TeamMember.points_contributed)
    ).scalar() or 0
    
    highest_rated = db.query(Team).join(TeamMember).filter(
        TeamMember.user_id == current_user.id
    ).order_by(desc(Team.average_rating)).first()
    
    return TeamStatsOverviewResponse(
        total_teams=total_teams,
        teams_owned=teams_owned,
        teams_member=teams_member,
        active_teams=active_teams,
        total_team_points=total_points,
        highest_rated_team={
            "id": highest_rated.id,
            "name": highest_rated.name,
            "rating": highest_rated.average_rating
        } if highest_rated else None
    )
