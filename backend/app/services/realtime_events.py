"""
Real-Time Event Integration Layer - Phase 3.5
Hooks for broadcasting events when entities are created/updated
This layer bridges domain models with WebSocket broadcasting
"""
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from app.services.websocket_manager import (
    manager, Event, EventType, create_event, emit_event
)


# ==================== LEARNING PATH EVENTS ====================

async def on_learning_path_enrolled(
    user_id: int,
    path_id: int,
    path_title: str,
    difficulty: str
):
    """
    Broadcast when user enrolls in learning path
    Called from: POST /api/v1/learning-paths/{path_id}/enroll
    """
    event = create_event(
        EventType.PATH_PROGRESS_UPDATE,
        user_id,
        {
            "path_id": path_id,
            "path_title": path_title,
            "difficulty": difficulty,
            "completion_percentage": 0,
            "action": "enrolled"
        },
        target_user_id=user_id
    )
    await emit_event(event)


async def on_challenge_completed(
    user_id: int,
    path_id: int,
    challenge_id: int,
    challenge_name: str,
    points_earned: int,
    completion_percentage: float,
    is_path_completed: bool = False
):
    """
    Broadcast when user completes a challenge
    Called from: POST /api/v1/learning-paths/{path_id}/challenges/{challenge_id}/complete
    """
    # Emit challenge completion event
    event = create_event(
        EventType.CHALLENGE_COMPLETED,
        user_id,
        {
            "path_id": path_id,
            "challenge_id": challenge_id,
            "challenge_name": challenge_name,
            "points_earned": points_earned,
            "completion_percentage": completion_percentage
        },
        target_user_id=user_id
    )
    await emit_event(event)
    
    # If path is now complete, emit path completed event
    if is_path_completed:
        path_event = create_event(
            EventType.PATH_COMPLETED,
            user_id,
            {
                "path_id": path_id,
                "points_earned": points_earned,
                "completion_percentage": 100.0
            },
            target_user_id=user_id
        )
        await emit_event(path_event)


async def on_certificate_issued(
    user_id: int,
    certificate_id: int,
    certificate_number: str,
    path_id: int,
    path_title: str,
    issue_date: datetime
):
    """
    Broadcast when certificate is issued
    Called from: POST /api/v1/certificates
    """
    event = create_event(
        EventType.CERTIFICATE_EARNED,
        user_id,
        {
            "certificate_id": certificate_id,
            "certificate_number": certificate_number,
            "path_id": path_id,
            "path_title": path_title,
            "issue_date": issue_date.isoformat()
        },
        target_user_id=user_id
    )
    await emit_event(event)


async def on_recommendation_created(
    user_id: int,
    recommendation_id: int,
    path_id: int,
    path_title: str,
    algorithm: str,
    score: float,
    reason: str
):
    """
    Broadcast when recommendation is created for user
    Called from: POST /api/v1/recommendations
    """
    event = create_event(
        EventType.RECOMMENDATION_CREATED,
        user_id,
        {
            "recommendation_id": recommendation_id,
            "path_id": path_id,
            "path_title": path_title,
            "algorithm": algorithm,
            "score": score,
            "reason": reason
        },
        target_user_id=user_id
    )
    await emit_event(event)


async def on_skill_validated(
    user_id: int,
    skill_id: int,
    skill_name: str,
    proficiency_level: str,
    confidence_score: float,
    endorsement_count: int
):
    """
    Broadcast when skill is validated/endorsed
    Called from: POST /api/v1/skills/{skill_id}/validate
    """
    event = create_event(
        EventType.SKILL_VALIDATED,
        user_id,
        {
            "skill_id": skill_id,
            "skill_name": skill_name,
            "proficiency_level": proficiency_level,
            "confidence_score": confidence_score,
            "endorsement_count": endorsement_count
        },
        target_user_id=user_id
    )
    await emit_event(event)


# ==================== MESSAGING & FORUM EVENTS ====================

async def on_message_created(
    message_id: int,
    conversation_id: int,
    sender_id: int,
    sender_name: str,
    recipient_id: int,
    content: str,
    created_at: datetime
):
    """
    Broadcast when new message is sent
    Called from: POST /api/v1/messages/{conversation_id}/send
    """
    # Send to recipient
    event = create_event(
        EventType.MESSAGE_SENT,
        sender_id,
        {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "content": content,
            "created_at": created_at.isoformat()
        },
        target_user_id=recipient_id
    )
    await emit_event(event)
    
    # Also notify sender of delivery
    ack_event = create_event(
        EventType.MESSAGE_SENT,
        sender_id,
        {
            "message_id": message_id,
            "status": "delivered"
        },
        target_user_id=sender_id
    )
    await emit_event(ack_event)


async def on_forum_thread_created(
    thread_id: int,
    topic_id: int,
    author_id: int,
    author_name: str,
    title: str,
    created_at: datetime
):
    """
    Broadcast when new forum thread is created
    Called from: POST /api/v1/forum/topics/{topic_id}/threads
    """
    event = create_event(
        EventType.FORUM_THREAD_CREATED,
        author_id,
        {
            "thread_id": thread_id,
            "topic_id": topic_id,
            "author_id": author_id,
            "author_name": author_name,
            "title": title,
            "created_at": created_at.isoformat()
        }
    )
    await emit_event(event)


async def on_forum_reply_posted(
    reply_id: int,
    thread_id: int,
    topic_id: int,
    author_id: int,
    author_name: str,
    content: str,
    created_at: datetime
):
    """
    Broadcast when reply is posted to forum thread
    Called from: POST /api/v1/forum/threads/{thread_id}/replies
    """
    event = create_event(
        EventType.FORUM_REPLY_POSTED,
        author_id,
        {
            "reply_id": reply_id,
            "thread_id": thread_id,
            "topic_id": topic_id,
            "author_id": author_id,
            "author_name": author_name,
            "content": content,
            "created_at": created_at.isoformat()
        }
    )
    await emit_event(event)


async def on_forum_thread_answer_marked(
    thread_id: int,
    reply_id: int,
    answer_setter_id: int,
    author_id: int
):
    """
    Broadcast when answer is marked as best in forum thread
    Called from: PUT /api/v1/forum/threads/{thread_id}/best-answer
    """
    # Notify author of selected answer
    event = create_event(
        EventType.FORUM_REPLY_POSTED,
        answer_setter_id,
        {
            "thread_id": thread_id,
            "reply_id": reply_id,
            "action": "best_answer_marked"
        },
        target_user_id=author_id
    )
    await emit_event(event)


# ==================== NOTIFICATION EVENTS ====================

async def on_notification_created(
    notification_id: int,
    user_id: int,
    notification_type: str,
    title: str,
    description: str,
    actor_id: Optional[int] = None,
    actor_name: Optional[str] = None,
    created_at: Optional[datetime] = None
):
    """
    Broadcast when notification is created
    Called from: POST /api/v1/notifications
    """
    data: Dict[str, Any] = {
        "notification_id": notification_id,
        "type": notification_type,
        "title": title,
        "description": description,
        "created_at": (created_at or datetime.utcnow()).isoformat()
    }
    
    if actor_id:
        data["actor_id"] = actor_id
    if actor_name:
        data["actor_name"] = actor_name
    
    event = create_event(
        EventType.NOTIFICATION_CREATED,
        actor_id or user_id,
        data,
        target_user_id=user_id
    )
    await emit_event(event)


# ==================== USER ACTIVITY EVENTS ====================

async def on_user_came_online(user_id: int):
    """
    Broadcast when user comes online
    Called from: WebSocket connection endpoint
    """
    event = create_event(
        EventType.USER_ONLINE,
        user_id,
        {"user_id": user_id},
        target_user_id=user_id
    )
    # Broadcast to all connected users
    await emit_event(event)


async def on_user_went_offline(user_id: int):
    """
    Broadcast when user goes offline
    Called from: WebSocket disconnect endpoint
    """
    event = create_event(
        EventType.USER_OFFLINE,
        user_id,
        {"user_id": user_id}
    )
    # Broadcast to all connected users
    await emit_event(event)


# ==================== COURSE EVENTS ====================

async def on_course_enrolled(
    user_id: int,
    course_id: int,
    course_title: str,
    course_path: str | None = None
):
    """
    Broadcast when a learner enrolls in a course
    """
    event = create_event(
        EventType.COURSE_ENROLLED,
        user_id,
        {
            "course_id": course_id,
            "course_title": course_title,
            "course_path": course_path
        },
        target_user_id=user_id
    )
    await emit_event(event)


async def on_course_progress(
    user_id: int,
    course_id: int,
    course_title: str,
    progress_percentage: float,
    video_id: int | None = None,
    video_title: str | None = None,
    video_progress: float | None = None
):
    """
    Broadcast course progress updates
    """
    event = create_event(
        EventType.COURSE_PROGRESS,
        user_id,
        {
            "course_id": course_id,
            "course_title": course_title,
            "progress_percentage": progress_percentage,
            "video_id": video_id,
            "video_title": video_title,
            "video_progress": video_progress
        },
        target_user_id=user_id
    )
    await emit_event(event)


async def on_course_completed(
    user_id: int,
    course_id: int,
    course_title: str,
    completion_percentage: float = 100.0
):
    """
    Broadcast when a learner completes a course
    """
    event = create_event(
        EventType.COURSE_COMPLETED,
        user_id,
        {
            "course_id": course_id,
            "course_title": course_title,
            "completion_percentage": completion_percentage
        },
        target_user_id=user_id
    )
    await emit_event(event)


# ==================== QUIZ EVENTS ====================

async def on_quiz_started(
    user_id: int,
    quiz_id: int,
    started_at: datetime | None = None
):
    """
    Broadcast when a quiz session starts
    """
    event = create_event(
        EventType.QUIZ_STARTED,
        user_id,
        {
            "quiz_id": quiz_id,
            "started_at": (started_at or datetime.utcnow()).isoformat()
        },
        target_user_id=user_id
    )
    await emit_event(event)


async def on_quiz_submitted(
    user_id: int,
    quiz_id: int,
    total_questions: int,
    answered: int,
    submitted_at: datetime | None = None
):
    """
    Broadcast when a quiz is submitted
    """
    event = create_event(
        EventType.QUIZ_SUBMITTED,
        user_id,
        {
            "quiz_id": quiz_id,
            "total_questions": total_questions,
            "answered": answered,
            "submitted_at": (submitted_at or datetime.utcnow()).isoformat()
        },
        target_user_id=user_id
    )
    await emit_event(event)


async def on_quiz_graded(
    user_id: int,
    quiz_id: int,
    score: float,
    total_questions: int,
    graded_at: datetime | None = None
):
    """
    Broadcast when quiz grading is complete
    """
    event = create_event(
        EventType.QUIZ_GRADED,
        user_id,
        {
            "quiz_id": quiz_id,
            "score": score,
            "total_questions": total_questions,
            "graded_at": (graded_at or datetime.utcnow()).isoformat()
        },
        target_user_id=user_id
    )
    await emit_event(event)


# ==================== ACHIEVEMENT EVENTS ====================

async def on_achievement_unlocked(
    user_id: int,
    key: str,
    title: str,
    points: int | None,
    unlocked_at: str
):
    """
    Broadcast when a user unlocks an achievement
    """
    event = create_event(
        EventType.ACHIEVEMENT_UNLOCKED,
        user_id,
        {
            "key": key,
            "title": title,
            "points": points,
            "unlocked_at": unlocked_at
        },
        target_user_id=user_id
    )
    await emit_event(event)


# ==================== GAMIFICATION EVENTS ====================
# ==================== GAMIFICATION EVENTS ====================

async def on_badge_earned(
    user_id: int,
    badge_id: int,
    badge_name: str,
    badge_description: str
):
    """
    Broadcast when user earns a badge
    Called from: Gamification service
    """
    event = create_event(
        EventType.BADGE_EARNED,
        user_id,
        {
            "badge_id": badge_id,
            "badge_name": badge_name,
            "badge_description": badge_description
        },
        target_user_id=user_id
    )
    await emit_event(event)


async def on_coins_earned(
    user_id: int,
    amount: int,
    reason: str,
    total_coins: Optional[int] = None
):
    """
    Broadcast when user earns coins
    Called from: Gamification service (challenge completion, etc)
    """
    data = {
        "amount": amount,
        "reason": reason
    }
    if total_coins is not None:
        data["total_coins"] = total_coins
    
    event = create_event(
        EventType.COIN_EARNED,
        user_id,
        data,
        target_user_id=user_id
    )
    await emit_event(event)


async def on_badge_displayed(
    user_id: int,
    badge_id: int,
    badge_name: str
):
    """
    Broadcast when a user highlights a badge (display/share)
    """
    event = create_event(
        EventType.BADGE_DISPLAYED,
        user_id,
        {
            "badge_id": badge_id,
            "badge_name": badge_name
        },
        target_user_id=user_id
    )
    await emit_event(event)


# ==================== BATCH EVENTS ====================

async def broadcast_to_users(
    user_ids: List[int],
    event_type: EventType,
    data: Dict[str, Any],
    sender_id: Optional[int] = None
):
    """
    Broadcast same event to multiple users
    Useful for group notifications
    """
    for user_id in user_ids:
        event = create_event(
            event_type,
            sender_id or user_id,
            data,
            target_user_id=user_id
        )
        await emit_event(event)


async def broadcast_to_all(
    event_type: EventType,
    data: Dict[str, Any],
    sender_id: Optional[int] = None,
    exclude_user_id: Optional[int] = None
):
    """
    Broadcast event to all connected users
    """
    active_users = manager.get_active_users()
    
    for user_id in active_users:
        if exclude_user_id and user_id == exclude_user_id:
            continue
        
        event = create_event(
            event_type,
            sender_id or user_id,
            data,
            target_user_id=user_id
        )
        await emit_event(event)


# ==================== EVENT HELPERS ====================

def get_connection_count(user_id: int) -> int:
    """Get number of active connections for user"""
    return manager.get_user_connection_count(user_id)


def is_user_online(user_id: int) -> bool:
    """Check if user has active WebSocket connections"""
    return manager.get_user_connection_count(user_id) > 0


def get_active_users() -> List[int]:
    """Get list of currently online users"""
    return manager.get_active_users()


def get_connection_stats() -> Dict[str, int]:
    """Get system-wide WebSocket statistics"""
    return {
        "total_connections": manager.get_total_connections(),
        "active_users": len(manager.get_active_users())
    }
