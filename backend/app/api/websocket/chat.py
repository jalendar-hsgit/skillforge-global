"""
WebSocket server for real-time mentor chat
"""
import socketio
from typing import Dict, Set
from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.user import User
from app.modelsx.mentor import MentorMessage, MentorSession
from app.core.security import decode_token

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # Configure properly in production
    logger=True,
    engineio_logger=True
)

# Track active connections: {user_id: {sid, ...}}
active_connections: Dict[int, Set[str]] = {}

# Track session rooms: {session_id: {user_id, ...}}
session_rooms: Dict[int, Set[int]] = {}


def get_user_from_token(token: str, db: Session) -> User:
    """Validate token and get user"""
    try:
        payload = decode_token(token)
        if not payload:
            return None
        
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except Exception as e:
        print(f"Auth error: {e}")
        return None


def is_participant(user_id: int, session_id: int, db: Session) -> bool:
    """Check if user is part of the session"""
    session = db.query(MentorSession).filter(
        MentorSession.id == session_id
    ).first()
    
    if not session:
        return False
    
    return user_id == session.student_id or user_id == session.mentor.user_id


@sio.event
async def connect(sid, environ, auth):
    """Handle new connection"""
    print(f"Client connecting: {sid}")
    
    # Get token from auth
    if not auth or 'token' not in auth:
        await sio.disconnect(sid)
        return False
    
    # Validate token
    token = auth['token']
    db = next(get_db())
    user = get_user_from_token(token, db)
    
    if not user:
        await sio.disconnect(sid)
        return False
    
    # Track connection
    if user.id not in active_connections:
        active_connections[user.id] = set()
    active_connections[user.id].add(sid)
    
    # Store user_id in session
    await sio.save_session(sid, {'user_id': user.id})
    
    print(f"User {user.id} connected with sid {sid}")
    return True


@sio.event
async def disconnect(sid):
    """Handle disconnection"""
    session = await sio.get_session(sid)
    if session and 'user_id' in session:
        user_id = session['user_id']
        if user_id in active_connections:
            active_connections[user_id].discard(sid)
            if not active_connections[user_id]:
                del active_connections[user_id]
        print(f"User {user_id} disconnected")


@sio.event
async def join_session(sid, data):
    """Join a mentor session chat room"""
    session_data = await sio.get_session(sid)
    if not session_data or 'user_id' not in session_data:
        await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
        return
    
    user_id = session_data['user_id']
    session_id = data.get('session_id')
    
    if not session_id:
        await sio.emit('error', {'message': 'Session ID required'}, room=sid)
        return
    
    # Check if user is participant
    db = next(get_db())
    if not is_participant(user_id, session_id, db):
        await sio.emit('error', {'message': 'Not authorized for this session'}, room=sid)
        return
    
    # Join room
    room_name = f"session_{session_id}"
    await sio.enter_room(sid, room_name)
    
    # Track in session rooms
    if session_id not in session_rooms:
        session_rooms[session_id] = set()
    session_rooms[session_id].add(user_id)
    
    # Load recent messages
    messages = db.query(MentorMessage).filter(
        MentorMessage.session_id == session_id
    ).order_by(MentorMessage.created_at.desc()).limit(50).all()
    
    # Send message history
    await sio.emit('message_history', {
        'messages': [
            {
                'id': msg.id,
                'sender_id': msg.sender_id,
                'content': msg.content,
                'created_at': msg.created_at.isoformat()
            }
            for msg in reversed(messages)
        ]
    }, room=sid)
    
    # Notify room
    await sio.emit('user_joined', {
        'user_id': user_id,
        'session_id': session_id
    }, room=room_name, skip_sid=sid)
    
    print(f"User {user_id} joined session {session_id}")


@sio.event
async def leave_session(sid, data):
    """Leave a mentor session chat room"""
    session_data = await sio.get_session(sid)
    if not session_data or 'user_id' not in session_data:
        return
    
    user_id = session_data['user_id']
    session_id = data.get('session_id')
    
    if not session_id:
        return
    
    room_name = f"session_{session_id}"
    await sio.leave_room(sid, room_name)
    
    # Remove from tracking
    if session_id in session_rooms:
        session_rooms[session_id].discard(user_id)
        if not session_rooms[session_id]:
            del session_rooms[session_id]
    
    # Notify room
    await sio.emit('user_left', {
        'user_id': user_id,
        'session_id': session_id
    }, room=room_name)
    
    print(f"User {user_id} left session {session_id}")


@sio.event
async def send_message(sid, data):
    """Send a message in a session"""
    session_data = await sio.get_session(sid)
    if not session_data or 'user_id' not in session_data:
        await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
        return
    
    user_id = session_data['user_id']
    session_id = data.get('session_id')
    content = data.get('content')
    
    if not session_id or not content:
        await sio.emit('error', {'message': 'Session ID and content required'}, room=sid)
        return
    
    # Verify authorization
    db = next(get_db())
    if not is_participant(user_id, session_id, db):
        await sio.emit('error', {'message': 'Not authorized'}, room=sid)
        return
    
    # Save message to database
    message = MentorMessage(
        session_id=session_id,
        sender_id=user_id,
        content=content.strip()
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Broadcast to room
    room_name = f"session_{session_id}"
    await sio.emit('new_message', {
        'id': message.id,
        'session_id': session_id,
        'sender_id': user_id,
        'content': message.content,
        'created_at': message.created_at.isoformat()
    }, room=room_name)
    
    print(f"Message sent in session {session_id} by user {user_id}")


@sio.event
async def typing(sid, data):
    """Broadcast typing indicator"""
    session_data = await sio.get_session(sid)
    if not session_data or 'user_id' not in session_data:
        return
    
    user_id = session_data['user_id']
    session_id = data.get('session_id')
    is_typing = data.get('is_typing', False)
    
    if not session_id:
        return
    
    room_name = f"session_{session_id}"
    await sio.emit('user_typing', {
        'user_id': user_id,
        'session_id': session_id,
        'is_typing': is_typing
    }, room=room_name, skip_sid=sid)


# WebRTC Signaling Events

@sio.event
async def call_initiate(sid, data):
    """Initiate a video/voice call"""
    session_data = await sio.get_session(sid)
    if not session_data or 'user_id' not in session_data:
        await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
        return
    
    user_id = session_data['user_id']
    session_id = data.get('session_id')
    call_type = data.get('call_type', 'video')  # 'video' or 'audio'
    
    if not session_id:
        await sio.emit('error', {'message': 'Session ID required'}, room=sid)
        return
    
    # Verify authorization
    db = next(get_db())
    if not is_participant(user_id, session_id, db):
        await sio.emit('error', {'message': 'Not authorized'}, room=sid)
        return
    
    # Notify other participants in the room
    room_name = f"session_{session_id}"
    await sio.emit('call_incoming', {
        'session_id': session_id,
        'caller_id': user_id,
        'call_type': call_type
    }, room=room_name, skip_sid=sid)
    
    print(f"Call initiated in session {session_id} by user {user_id}")


@sio.event
async def call_accept(sid, data):
    """Accept an incoming call"""
    session_data = await sio.get_session(sid)
    if not session_data or 'user_id' not in session_data:
        return
    
    user_id = session_data['user_id']
    session_id = data.get('session_id')
    caller_id = data.get('caller_id')
    
    if not session_id or not caller_id:
        return
    
    # Notify the caller
    room_name = f"session_{session_id}"
    await sio.emit('call_accepted', {
        'session_id': session_id,
        'accepter_id': user_id
    }, room=room_name, skip_sid=sid)
    
    print(f"Call accepted in session {session_id} by user {user_id}")


@sio.event
async def call_reject(sid, data):
    """Reject an incoming call"""
    session_data = await sio.get_session(sid)
    if not session_data or 'user_id' not in session_data:
        return
    
    user_id = session_data['user_id']
    session_id = data.get('session_id')
    
    if not session_id:
        return
    
    # Notify the room
    room_name = f"session_{session_id}"
    await sio.emit('call_rejected', {
        'session_id': session_id,
        'rejector_id': user_id
    }, room=room_name, skip_sid=sid)
    
    print(f"Call rejected in session {session_id} by user {user_id}")


@sio.event
async def call_end(sid, data):
    """End an active call"""
    session_data = await sio.get_session(sid)
    if not session_data or 'user_id' not in session_data:
        return
    
    user_id = session_data['user_id']
    session_id = data.get('session_id')
    
    if not session_id:
        return
    
    # Notify the room
    room_name = f"session_{session_id}"
    await sio.emit('call_ended', {
        'session_id': session_id,
        'ended_by': user_id
    }, room=room_name)
    
    print(f"Call ended in session {session_id} by user {user_id}")


@sio.event
async def webrtc_offer(sid, data):
    """Forward WebRTC offer to peer"""
    session_data = await sio.get_session(sid)
    if not session_data or 'user_id' not in session_data:
        return
    
    user_id = session_data['user_id']
    session_id = data.get('session_id')
    offer = data.get('offer')
    target_user_id = data.get('target_user_id')
    
    if not session_id or not offer or not target_user_id:
        return
    
    # Forward to target user
    if target_user_id in active_connections:
        for target_sid in active_connections[target_user_id]:
            await sio.emit('webrtc_offer', {
                'session_id': session_id,
                'from_user_id': user_id,
                'offer': offer
            }, room=target_sid)


@sio.event
async def webrtc_answer(sid, data):
    """Forward WebRTC answer to peer"""
    session_data = await sio.get_session(sid)
    if not session_data or 'user_id' not in session_data:
        return
    
    user_id = session_data['user_id']
    session_id = data.get('session_id')
    answer = data.get('answer')
    target_user_id = data.get('target_user_id')
    
    if not session_id or not answer or not target_user_id:
        return
    
    # Forward to target user
    if target_user_id in active_connections:
        for target_sid in active_connections[target_user_id]:
            await sio.emit('webrtc_answer', {
                'session_id': session_id,
                'from_user_id': user_id,
                'answer': answer
            }, room=target_sid)


@sio.event
async def webrtc_ice_candidate(sid, data):
    """Forward ICE candidate to peer"""
    session_data = await sio.get_session(sid)
    if not session_data or 'user_id' not in session_data:
        return
    
    user_id = session_data['user_id']
    session_id = data.get('session_id')
    candidate = data.get('candidate')
    target_user_id = data.get('target_user_id')
    
    if not session_id or not candidate or not target_user_id:
        return
    
    # Forward to target user
    if target_user_id in active_connections:
        for target_sid in active_connections[target_user_id]:
            await sio.emit('webrtc_ice_candidate', {
                'session_id': session_id,
                'from_user_id': user_id,
                'candidate': candidate
            }, room=target_sid)


# Create ASGI app with proper handling for non-socket.io requests
# The other_asgi_app=None and static_files=None ensures proper WebSocket handling
socket_app = socketio.ASGIApp(
    sio,
    socketio_path='socket.io',
    # Handle non-socket.io requests by closing gracefully
    other_asgi_app=None
)
