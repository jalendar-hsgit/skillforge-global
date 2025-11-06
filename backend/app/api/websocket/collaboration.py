"""
WebSocket server for real-time resume collaboration
"""
import socketio
from typing import Dict, Set, Optional
from datetime import datetime
import json

# Create Socket.IO server for collaboration
collab_sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # Configure properly in production
    logger=True,
    engineio_logger=False,  # Reduce noise in logs
    ping_timeout=60,
    ping_interval=25
)

# Track active users per resume: {resume_id: {user_id: {sid, name, color}}}
active_resume_users: Dict[str, Dict[str, dict]] = {}

# Track user sessions: {sid: {resume_id, user_id, name, color}}
user_sessions: Dict[str, dict] = {}


@collab_sio.event
async def connect(sid, environ, auth):
    """Handle new connection"""
    print(f"[Collaboration] Client connecting: {sid}")
    
    if not auth:
        print(f"[Collaboration] No auth provided for {sid}")
        return True  # Still allow connection, will authenticate on join_resume
    
    # Store auth data for later use
    await collab_sio.save_session(sid, {
        'auth': auth,
        'connected_at': datetime.utcnow().isoformat()
    })
    
    print(f"[Collaboration] Client {sid} connected successfully")
    return True


@collab_sio.event
async def disconnect(sid):
    """Handle disconnection"""
    print(f"[Collaboration] Client disconnecting: {sid}")
    
    # Get user session data
    if sid in user_sessions:
        session = user_sessions[sid]
        resume_id = session.get('resumeId')
        user_id = session.get('userId')
        
        # Remove from active users
        if resume_id and resume_id in active_resume_users:
            if user_id in active_resume_users[resume_id]:
                del active_resume_users[resume_id][user_id]
                
                # Notify others in the room
                await collab_sio.emit(
                    'user_left',
                    {'userId': user_id},
                    room=f"resume_{resume_id}",
                    skip_sid=sid
                )
                
                # Send updated user list
                await _send_active_users(resume_id, skip_sid=sid)
                
                # Clean up empty resume rooms
                if not active_resume_users[resume_id]:
                    del active_resume_users[resume_id]
        
        # Remove session tracking
        del user_sessions[sid]
        
        print(f"[Collaboration] User {user_id} left resume {resume_id}")


@collab_sio.event
async def join_resume(sid, data):
    """User joins a resume editing session"""
    try:
        resume_id = data.get('resumeId')
        user_id = data.get('userId')
        user_name = data.get('userName', 'Anonymous')
        user_color = data.get('color', '#888888')
        
        if not resume_id or not user_id:
            print(f"[Collaboration] Invalid join_resume data: {data}")
            return
        
        print(f"[Collaboration] User {user_id} ({user_name}) joining resume {resume_id}")
        
        # Join the Socket.IO room
        room_name = f"resume_{resume_id}"
        await collab_sio.enter_room(sid, room_name)
        
        # Track user session
        user_sessions[sid] = {
            'resumeId': resume_id,
            'userId': user_id,
            'userName': user_name,
            'color': user_color,
            'joined_at': datetime.utcnow().isoformat()
        }
        
        # Track active users for this resume
        if resume_id not in active_resume_users:
            active_resume_users[resume_id] = {}
        
        active_resume_users[resume_id][user_id] = {
            'sid': sid,
            'id': user_id,
            'name': user_name,
            'color': user_color,
            'cursor': None
        }
        
        # Notify others that user joined
        await collab_sio.emit(
            'user_joined',
            {
                'id': user_id,
                'name': user_name,
                'color': user_color
            },
            room=room_name,
            skip_sid=sid
        )
        
        # Send current active users to the new joiner
        await _send_active_users(resume_id, to_sid=sid)
        
        print(f"[Collaboration] User {user_id} joined resume {resume_id}. Active users: {len(active_resume_users[resume_id])}")
        
    except Exception as e:
        print(f"[Collaboration] Error in join_resume: {e}")


@collab_sio.event
async def resume_update(sid, data):
    """Broadcast resume update to other collaborators"""
    try:
        if sid not in user_sessions:
            print(f"[Collaboration] Update from unknown session: {sid}")
            return
        
        session = user_sessions[sid]
        resume_id = data.get('resumeId') or session.get('resumeId')
        user_id = data.get('userId') or session.get('userId')
        
        if not resume_id:
            print(f"[Collaboration] No resume_id in update")
            return
        
        # Broadcast to all users in the room except sender
        room_name = f"resume_{resume_id}"
        
        message = {
            'type': 'update',
            'userId': user_id,
            'data': data.get('data'),
            'timestamp': data.get('timestamp', datetime.utcnow().timestamp() * 1000)
        }
        
        await collab_sio.emit(
            'resume_update',
            message,
            room=room_name,
            skip_sid=sid
        )
        
        # print(f"[Collaboration] User {user_id} updated resume {resume_id}")
        
    except Exception as e:
        print(f"[Collaboration] Error in resume_update: {e}")


@collab_sio.event
async def cursor_move(sid, data):
    """Broadcast cursor position to other collaborators"""
    try:
        if sid not in user_sessions:
            return
        
        session = user_sessions[sid]
        resume_id = data.get('resumeId') or session.get('resumeId')
        user_id = data.get('userId') or session.get('userId')
        position = data.get('position')
        
        if not resume_id or not position:
            return
        
        # Update cursor position in active users
        if resume_id in active_resume_users and user_id in active_resume_users[resume_id]:
            active_resume_users[resume_id][user_id]['cursor'] = position
        
        # Broadcast to others
        room_name = f"resume_{resume_id}"
        await collab_sio.emit(
            'cursor_move',
            {
                'userId': user_id,
                'position': position
            },
            room=room_name,
            skip_sid=sid
        )
        
    except Exception as e:
        print(f"[Collaboration] Error in cursor_move: {e}")


async def _send_active_users(resume_id: str, to_sid: Optional[str] = None, skip_sid: Optional[str] = None):
    """Send list of active users to room or specific user"""
    if resume_id not in active_resume_users:
        return
    
    users = [
        {
            'id': user_data['id'],
            'name': user_data['name'],
            'color': user_data['color'],
            'cursor': user_data.get('cursor')
        }
        for user_data in active_resume_users[resume_id].values()
    ]
    
    if to_sid:
        # Send to specific user
        await collab_sio.emit('active_users', users, to=to_sid)
    else:
        # Broadcast to room
        room_name = f"resume_{resume_id}"
        await collab_sio.emit('active_users', users, room=room_name, skip_sid=skip_sid)


# Create ASGI app
collab_socket_app = socketio.ASGIApp(
    collab_sio,
    other_asgi_app=None,
    socketio_path='socket.io'
)

print("[Collaboration] WebSocket server initialized")
