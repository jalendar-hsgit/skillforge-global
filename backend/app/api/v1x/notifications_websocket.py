"""
WebSocket endpoint for real-time notifications
"""
from fastapi import APIRouter, WebSocket, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.notifications import Notification
import json
import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications WebSocket"])

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        """Register a new WebSocket connection for a user"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected. Total connections for user: {len(self.active_connections[user_id])}")

    def disconnect(self, user_id: int, websocket: WebSocket):
        """Unregister a WebSocket connection"""
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            except ValueError:
                pass
            logger.info(f"User {user_id} disconnected. Remaining connections: {len(self.active_connections.get(user_id, []))}")

    async def broadcast_to_user(self, user_id: int, message: dict):
        """Send message to all connections of a user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(user_id, connection)

    async def broadcast_to_users(self, user_ids: List[int], message: dict):
        """Send message to specific users"""
        for user_id in user_ids:
            await self.broadcast_to_user(user_id, message)


# Global connection manager
manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """Dependency to get connection manager"""
    return manager


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time notifications
    
    Expects: token as query parameter
    Sends: {"event": "notification", "data": {notification_data}}
    """
    user = None
    try:
        # Verify token
        user = verify_token(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return

        # Connect user
        await manager.connect(user.id, websocket)
        
        # Send connection confirmation
        await websocket.send_json({
            "event": "connected",
            "data": {"user_id": user.id, "message": "Connected to notifications"}
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back any messages (for keep-alive)
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if user:
            manager.disconnect(user.id, websocket)


# Public function to send notifications to users
async def send_notification_to_user(
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "info",
    data: dict = None,
    db: Session = None
):
    """
    Send a notification to a user via WebSocket
    
    Args:
        user_id: ID of user to notify
        title: Notification title
        message: Notification message
        notification_type: Type of notification (info, success, warning, error)
        data: Additional data to send
        db: Database session for storing notification
    """
    try:
        # Store in database if db session provided
        if db:
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                data=data or {}
            )
            db.add(notification)
            db.commit()
            notification_data = {
                "id": notification.id,
                "type": notification_type,
                "title": title,
                "message": message,
                "data": data or {},
                "is_read": False,
                "created_at": notification.created_at.isoformat() if notification.created_at else None
            }
        else:
            notification_data = {
                "type": notification_type,
                "title": title,
                "message": message,
                "data": data or {}
            }

        # Send via WebSocket
        await manager.broadcast_to_user(user_id, {
            "event": "notification",
            "data": notification_data
        })
        
        logger.info(f"Notification sent to user {user_id}: {title}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")


async def send_notifications_to_users(
    user_ids: List[int],
    title: str,
    message: str,
    notification_type: str = "info",
    data: dict = None,
    db: Session = None
):
    """Send notification to multiple users"""
    for user_id in user_ids:
        await send_notification_to_user(user_id, title, message, notification_type, data, db)
