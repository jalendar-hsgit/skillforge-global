"""
WebSocket Connection Manager - Phase 3.5
Manages WebSocket connections and broadcasts real-time events
"""
from typing import Dict, List, Set
from fastapi import WebSocket
from datetime import datetime
import json
import asyncio
from enum import Enum


class EventType(str, Enum):
    """Real-time event types"""
    # Learning paths
    PATH_PROGRESS_UPDATE = "path_progress_update"
    CHALLENGE_COMPLETED = "challenge_completed"
    PATH_COMPLETED = "path_completed"
    CERTIFICATE_EARNED = "certificate_earned"
    RECOMMENDATION_CREATED = "recommendation_created"
    
    # Messaging & Forums
    MESSAGE_SENT = "message_sent"
    FORUM_REPLY_POSTED = "forum_reply_posted"
    FORUM_THREAD_CREATED = "forum_thread_created"
    
    # Notifications
    NOTIFICATION_CREATED = "notification_created"
    
    # User activity
    USER_ONLINE = "user_online"
    USER_OFFLINE = "user_offline"
    SKILL_VALIDATED = "skill_validated"
    
    # Gamification
    BADGE_EARNED = "badge_earned"
    COIN_EARNED = "coin_earned"

    # Courses
    COURSE_ENROLLED = "course_enrolled"
    COURSE_PROGRESS = "course_progress"
    COURSE_COMPLETED = "course_completed"

    # Quizzes
    QUIZ_STARTED = "quiz_started"
    QUIZ_SUBMITTED = "quiz_submitted"
    QUIZ_GRADED = "quiz_graded"

    # Achievements
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"

    # Badge display
    BADGE_DISPLAYED = "badge_displayed"


class Event:
    """Real-time event data structure"""
    
    def __init__(
        self,
        event_type: EventType,
        user_id: int,
        data: dict,
        timestamp: datetime = None,
        target_user_id: int = None
    ):
        self.event_type = event_type
        self.user_id = user_id
        self.target_user_id = target_user_id  # Who should receive this event
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_json(self) -> str:
        """Convert event to JSON for transmission"""
        return json.dumps({
            "type": self.event_type,
            "user_id": self.user_id,
            "target_user_id": self.target_user_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        })
    
    @classmethod
    def from_json(cls, data: str) -> 'Event':
        """Create event from JSON"""
        parsed = json.loads(data)
        return cls(
            event_type=EventType(parsed["type"]),
            user_id=parsed["user_id"],
            data=parsed["data"],
            timestamp=datetime.fromisoformat(parsed["timestamp"]),
            target_user_id=parsed.get("target_user_id")
        )


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting"""
    
    def __init__(self):
        # Map of user_id -> list of active WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}
        
        # Map of user_id -> set of WebSocket objects for quick lookup
        self.user_sockets: Dict[int, Set[WebSocket]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}
        
        # Event queue for broadcasting
        self.event_queue: asyncio.Queue = None
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Register a new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
            self.user_sockets[user_id] = set()
        
        self.active_connections[user_id].append(websocket)
        self.user_sockets[user_id].add(websocket)
        
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "last_heartbeat": datetime.utcnow()
        }
        
        print(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Unregister a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            
            if websocket in self.user_sockets.get(user_id, set()):
                self.user_sockets[user_id].discard(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                if user_id in self.user_sockets:
                    del self.user_sockets[user_id]
        
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        
        print(f"User {user_id} disconnected")
    
    async def broadcast(self, event: Event):
        """Broadcast event to target user(s)"""
        # If target_user_id specified, send only to that user
        if event.target_user_id:
            await self.send_to_user(event.target_user_id, event)
        else:
            # Broadcast to all connected users
            for user_id, connections in self.active_connections.items():
                for connection in connections:
                    try:
                        await connection.send_text(event.to_json())
                    except Exception as e:
                        print(f"Error broadcasting to user {user_id}: {e}")
    
    async def broadcast_to_users(self, event: Event, user_ids: List[int]):
        """Broadcast event to specific users"""
        for user_id in user_ids:
            await self.send_to_user(user_id, event)
    
    async def send_to_user(self, user_id: int, event: Event):
        """Send event to specific user"""
        if user_id not in self.active_connections:
            return
        
        dead_connections = []
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_text(event.to_json())
            except Exception as e:
                print(f"Error sending to user {user_id}: {e}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for connection in dead_connections:
            try:
                self.disconnect(connection, user_id)
            except:
                pass
    
    async def send_to_group(self, event: Event, user_ids: List[int]):
        """Send event to a group of users"""
        for user_id in user_ids:
            await self.send_to_user(user_id, event)
    
    async def broadcast_exclusive(self, event: Event, exclude_user_id: int = None):
        """Broadcast to all except specified user"""
        for user_id, connections in self.active_connections.items():
            if exclude_user_id and user_id == exclude_user_id:
                continue
            
            for connection in connections:
                try:
                    await connection.send_text(event.to_json())
                except Exception as e:
                    print(f"Error broadcasting to user {user_id}: {e}")
    
    def get_user_connection_count(self, user_id: int) -> int:
        """Get number of active connections for user"""
        return len(self.active_connections.get(user_id, []))
    
    def get_active_users(self) -> List[int]:
        """Get list of users with active connections"""
        return list(self.active_connections.keys())
    
    def get_total_connections(self) -> int:
        """Get total active connections across all users"""
        return sum(len(conns) for conns in self.active_connections.values())
    
    async def update_heartbeat(self, websocket: WebSocket):
        """Update last heartbeat timestamp"""
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["last_heartbeat"] = datetime.utcnow()
    
    async def check_stale_connections(self, timeout_seconds: int = 300):
        """Remove stale connections (no heartbeat for timeout_seconds)"""
        now = datetime.utcnow()
        stale_websockets = []
        
        for websocket, metadata in self.connection_metadata.items():
            elapsed = (now - metadata["last_heartbeat"]).total_seconds()
            if elapsed > timeout_seconds:
                stale_websockets.append((websocket, metadata["user_id"]))
        
        for websocket, user_id in stale_websockets:
            try:
                await websocket.close()
                self.disconnect(websocket, user_id)
            except:
                pass


# Global connection manager instance
manager = ConnectionManager()


async def emit_event(event: Event):
    """Helper function to emit events to connected users"""
    await manager.broadcast(event)


def create_event(
    event_type: EventType,
    user_id: int,
    data: dict,
    target_user_id: int = None
) -> Event:
    """Helper function to create events"""
    return Event(
        event_type=event_type,
        user_id=user_id,
        data=data,
        target_user_id=target_user_id
    )
