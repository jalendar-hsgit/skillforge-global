"""
WebSocket Router - Phase 3.5
WebSocket endpoints for real-time connections
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from typing import Optional
import asyncio
import json

from app.services.websocket_manager import (
    manager, Event, EventType, create_event, emit_event
)
from app.models import User
from app.api.deps import get_current_user
from sqlalchemy.orm import Session
from app.core.db import get_db

router = APIRouter(prefix="/ws", tags=["websocket"])


# ==================== CONNECTION MANAGEMENT ====================

@router.websocket("/connect/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    Main WebSocket endpoint for real-time updates
    Client should connect with: ws://localhost:8001/api/v1/ws/connect/{token}
    Where token is the JWT auth token
    """
    # Note: In production, validate the token here
    # For now, we'll accept the connection
    
    # Extract user_id from token (simplified - in production use proper JWT validation)
    user_id = int(token.split("_")[-1]) if "_" in token else 1
    
    try:
        await manager.connect(websocket, user_id)
        
        # Send welcome message
        welcome_event = create_event(
            EventType.USER_ONLINE,
            user_id,
            {"message": "Connected to real-time updates", "user_id": user_id},
            target_user_id=user_id
        )
        await manager.send_to_user(user_id, welcome_event)
        
        # Keep connection open and listen for messages
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type", "heartbeat")
                
                if message_type == "heartbeat":
                    # Update heartbeat
                    await manager.update_heartbeat(websocket)
                    
                    # Send heartbeat ACK
                    await websocket.send_json({
                        "type": "heartbeat_ack",
                        "timestamp": asyncio.get_event_loop().time()
                    })
                
                elif message_type == "ping":
                    # Respond to ping
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time()
                    })
                
                else:
                    # Unknown message type
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        
        # Broadcast user offline event
        offline_event = create_event(
            EventType.USER_OFFLINE,
            user_id,
            {"message": f"User {user_id} went offline"}
        )
        await emit_event(offline_event)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            manager.disconnect(websocket, user_id)
        except:
            pass


# ==================== EVENT EMISSION ENDPOINTS ====================

@router.post("/emit/path-progress")
async def emit_path_progress(
    user_id: int,
    path_id: int,
    completed_challenges: int,
    total_challenges: int,
    completion_percentage: float,
    current_user: User = Depends(get_current_user)
):
    """Emit path progress update event"""
    event = create_event(
        EventType.PATH_PROGRESS_UPDATE,
        current_user.id,
        {
            "path_id": path_id,
            "completed_challenges": completed_challenges,
            "total_challenges": total_challenges,
            "completion_percentage": completion_percentage
        },
        target_user_id=user_id
    )
    await emit_event(event)
    return {"status": "emitted"}


@router.post("/emit/challenge-completed")
async def emit_challenge_completed(
    user_id: int,
    path_id: int,
    challenge_id: int,
    points_earned: int,
    current_user: User = Depends(get_current_user)
):
    """Emit challenge completion event"""
    event = create_event(
        EventType.CHALLENGE_COMPLETED,
        current_user.id,
        {
            "path_id": path_id,
            "challenge_id": challenge_id,
            "points_earned": points_earned
        },
        target_user_id=user_id
    )
    await emit_event(event)
    return {"status": "emitted"}


@router.post("/emit/path-completed")
async def emit_path_completed(
    user_id: int,
    path_id: int,
    path_title: str,
    total_points: int,
    current_user: User = Depends(get_current_user)
):
    """Emit path completion event"""
    event = create_event(
        EventType.PATH_COMPLETED,
        current_user.id,
        {
            "path_id": path_id,
            "path_title": path_title,
            "total_points": total_points
        },
        target_user_id=user_id
    )
    await emit_event(event)
    return {"status": "emitted"}


@router.post("/emit/certificate-earned")
async def emit_certificate_earned(
    user_id: int,
    certificate_id: int,
    certificate_number: str,
    path_title: str,
    current_user: User = Depends(get_current_user)
):
    """Emit certificate earned event"""
    event = create_event(
        EventType.CERTIFICATE_EARNED,
        current_user.id,
        {
            "certificate_id": certificate_id,
            "certificate_number": certificate_number,
            "path_title": path_title
        },
        target_user_id=user_id
    )
    await emit_event(event)
    return {"status": "emitted"}


@router.post("/emit/recommendation-created")
async def emit_recommendation_created(
    user_id: int,
    recommendation_id: int,
    path_id: int,
    path_title: str,
    reason: str,
    current_user: User = Depends(get_current_user)
):
    """Emit recommendation created event"""
    event = create_event(
        EventType.RECOMMENDATION_CREATED,
        current_user.id,
        {
            "recommendation_id": recommendation_id,
            "path_id": path_id,
            "path_title": path_title,
            "reason": reason
        },
        target_user_id=user_id
    )
    await emit_event(event)
    return {"status": "emitted"}


@router.post("/emit/message-sent")
async def emit_message_sent(
    conversation_id: int,
    message_id: int,
    sender_id: int,
    content: str,
    recipient_id: int,
    current_user: User = Depends(get_current_user)
):
    """Emit message sent event"""
    event = create_event(
        EventType.MESSAGE_SENT,
        sender_id,
        {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "content": content,
            "sender_id": sender_id
        },
        target_user_id=recipient_id
    )
    await emit_event(event)
    return {"status": "emitted"}


@router.post("/emit/forum-reply-posted")
async def emit_forum_reply_posted(
    thread_id: int,
    reply_id: int,
    author_id: int,
    content: str,
    current_user: User = Depends(get_current_user)
):
    """Emit forum reply posted event"""
    event = create_event(
        EventType.FORUM_REPLY_POSTED,
        author_id,
        {
            "thread_id": thread_id,
            "reply_id": reply_id,
            "content": content,
            "author_id": author_id
        }
    )
    await emit_event(event)
    return {"status": "emitted"}


@router.post("/emit/forum-thread-created")
async def emit_forum_thread_created(
    topic_id: int,
    thread_id: int,
    author_id: int,
    title: str,
    current_user: User = Depends(get_current_user)
):
    """Emit forum thread created event"""
    event = create_event(
        EventType.FORUM_THREAD_CREATED,
        author_id,
        {
            "topic_id": topic_id,
            "thread_id": thread_id,
            "title": title,
            "author_id": author_id
        }
    )
    await emit_event(event)
    return {"status": "emitted"}


@router.post("/emit/notification")
async def emit_notification(
    user_id: int,
    notification_id: int,
    notification_type: str,
    title: str,
    description: str,
    current_user: User = Depends(get_current_user)
):
    """Emit notification event"""
    event = create_event(
        EventType.NOTIFICATION_CREATED,
        current_user.id,
        {
            "notification_id": notification_id,
            "notification_type": notification_type,
            "title": title,
            "description": description
        },
        target_user_id=user_id
    )
    await emit_event(event)
    return {"status": "emitted"}


@router.post("/emit/skill-validated")
async def emit_skill_validated(
    user_id: int,
    skill_name: str,
    proficiency_level: str,
    current_user: User = Depends(get_current_user)
):
    """Emit skill validated event"""
    event = create_event(
        EventType.SKILL_VALIDATED,
        current_user.id,
        {
            "skill_name": skill_name,
            "proficiency_level": proficiency_level
        },
        target_user_id=user_id
    )
    await emit_event(event)
    return {"status": "emitted"}


@router.post("/emit/badge-earned")
async def emit_badge_earned(
    user_id: int,
    badge_id: int,
    badge_name: str,
    current_user: User = Depends(get_current_user)
):
    """Emit badge earned event"""
    event = create_event(
        EventType.BADGE_EARNED,
        current_user.id,
        {
            "badge_id": badge_id,
            "badge_name": badge_name
        },
        target_user_id=user_id
    )
    await emit_event(event)
    return {"status": "emitted"}


@router.post("/emit/coin-earned")
async def emit_coin_earned(
    user_id: int,
    amount: int,
    reason: str,
    current_user: User = Depends(get_current_user)
):
    """Emit coin earned event"""
    event = create_event(
        EventType.COIN_EARNED,
        current_user.id,
        {
            "amount": amount,
            "reason": reason
        },
        target_user_id=user_id
    )
    await emit_event(event)
    return {"status": "emitted"}


# ==================== CONNECTION STATS ====================

@router.get("/stats")
async def get_websocket_stats(
    current_user: User = Depends(get_current_user)
):
    """Get WebSocket connection statistics"""
    return {
        "total_connections": manager.get_total_connections(),
        "active_users": len(manager.get_active_users()),
        "user_connection_count": manager.get_user_connection_count(current_user.id),
        "active_users_list": manager.get_active_users()
    }


@router.get("/user-status/{user_id}")
async def get_user_online_status(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Check if user is online"""
    connection_count = manager.get_user_connection_count(user_id)
    return {
        "user_id": user_id,
        "is_online": connection_count > 0,
        "connection_count": connection_count
    }
