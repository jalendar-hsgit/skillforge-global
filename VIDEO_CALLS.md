# Video/Voice Call Implementation

This document describes the WebRTC-based video and voice calling feature for the mentor chat system.

## Overview

The video call system enables peer-to-peer audio and video communication between mentors and students during their scheduled sessions. It uses WebRTC for direct browser-to-browser connections with Socket.IO for signaling.

## Architecture

### Components

1. **Backend (Socket.IO Signaling Server)**
   - `backend/app/api/websocket/chat.py` - WebSocket server with signaling events

2. **Frontend Components**
   - `src/components/VideoCall.tsx` - Video call interface with camera/mic controls
   - `src/components/MentorChat.tsx` - Chat interface with call initiation buttons

### WebRTC Flow

```
Caller                    Signaling Server                Callee
  |                              |                           |
  |------ call_initiate -------->|                           |
  |                              |------ call_incoming ----->|
  |                              |                           |
  |                              |<----- call_accept --------|
  |<----- call_accepted ---------|                           |
  |                              |                           |
  |------ webrtc_offer --------->|                           |
  |                              |------ webrtc_offer ------>|
  |                              |                           |
  |                              |<----- webrtc_answer ------|
  |<----- webrtc_answer ---------|                           |
  |                              |                           |
  |--- ice_candidate (x N) ----->|                           |
  |                              |--- ice_candidate (x N) -->|
  |                              |                           |
  |<========== WebRTC Connection Established ==============>|
  |                              |                           |
```

## Backend Implementation

### Socket.IO Events

#### Call Management Events

- **`call_initiate`** - Start a call
  ```python
  data = {
    'session_id': int,
    'call_type': 'video' | 'audio'
  }
  ```

- **`call_incoming`** - Notify callee of incoming call (broadcast)
  ```python
  data = {
    'session_id': int,
    'caller_id': int,
    'call_type': 'video' | 'audio'
  }
  ```

- **`call_accept`** - Accept an incoming call
  ```python
  data = {
    'session_id': int,
    'caller_id': int
  }
  ```

- **`call_accepted`** - Notify caller that call was accepted (broadcast)
  ```python
  data = {
    'session_id': int,
    'accepter_id': int
  }
  ```

- **`call_reject`** - Reject an incoming call
  ```python
  data = {
    'session_id': int
  }
  ```

- **`call_rejected`** - Notify caller that call was rejected (broadcast)
  ```python
  data = {
    'session_id': int,
    'rejector_id': int
  }
  ```

- **`call_end`** - End an active call
  ```python
  data = {
    'session_id': int
  }
  ```

- **`call_ended`** - Notify all participants that call ended (broadcast)
  ```python
  data = {
    'session_id': int,
    'ended_by': int
  }
  ```

#### WebRTC Signaling Events

- **`webrtc_offer`** - Send WebRTC offer to peer
  ```python
  data = {
    'session_id': int,
    'target_user_id': int,
    'offer': RTCSessionDescription
  }
  ```

- **`webrtc_answer`** - Send WebRTC answer to peer
  ```python
  data = {
    'session_id': int,
    'target_user_id': int,
    'answer': RTCSessionDescription
  }
  ```

- **`webrtc_ice_candidate`** - Send ICE candidate to peer
  ```python
  data = {
    'session_id': int,
    'target_user_id': int,
    'candidate': RTCIceCandidate
  }
  ```

### Authorization

All signaling events check:
1. User is authenticated (has valid session)
2. User is a participant in the mentor session (student or mentor)

## Frontend Implementation

### VideoCall Component

**Props:**
```typescript
interface VideoCallProps {
  socket: Socket | null;
  sessionId: number;
  currentUserId: number;
  otherUserId: number;
  onCallEnd: () => void;
}
```

**Features:**
- Full-screen video interface
- Picture-in-picture local video
- Camera toggle (on/off)
- Microphone toggle (mute/unmute)
- End call button
- Connection status indicator
- Automatic cleanup on unmount

**WebRTC Configuration:**
- Uses Google's public STUN servers for NAT traversal
- Supports both video and audio tracks
- Handles ICE candidate exchange
- Monitors connection state

### MentorChat Component

**Updated Props:**
```typescript
interface MentorChatProps {
  sessionId: number;
  currentUserId: number;
  otherUserId: number;  // NEW: Required for WebRTC peer connection
  token: string;
}
```

**New Features:**
- Video call button (📹) in header
- Audio call button (🎤) in header
- Incoming call modal with accept/reject
- Seamless transition to VideoCall component

## Usage Example

```tsx
import MentorChat from '@/components/MentorChat';

function SessionPage() {
  const sessionId = 123;
  const currentUserId = 456;
  const mentorUserId = 789;
  const token = 'your-jwt-token';

  return (
    <MentorChat
      sessionId={sessionId}
      currentUserId={currentUserId}
      otherUserId={mentorUserId}
      token={token}
    />
  );
}
```

## Testing

### Local Testing (Same Computer)

1. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

2. Start the frontend:
   ```bash
   npm run dev
   ```

3. Open two browser windows:
   - Window 1: Login as student
   - Window 2: Login as mentor (use private/incognito mode)

4. Join the same session in both windows

5. Click the video call button in one window

6. Accept the call in the other window

### Testing Checklist

- [ ] Call initiation from both sides
- [ ] Call acceptance
- [ ] Call rejection
- [ ] Video toggle (on/off)
- [ ] Audio toggle (mute/unmute)
- [ ] End call
- [ ] Connection status updates
- [ ] Multiple ICE candidates exchange
- [ ] Reconnection after network interruption

## Configuration

### STUN/TURN Servers

For production, you may need to configure TURN servers for users behind restrictive firewalls:

```typescript
// In VideoCall.tsx
const rtcConfig: RTCConfig = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    {
      urls: 'turn:your-turn-server.com:3478',
      username: 'username',
      credential: 'password'
    }
  ],
};
```

**Recommended TURN Services:**
- [Twilio STUN/TURN](https://www.twilio.com/stun-turn)
- [Xirsys](https://xirsys.com/)
- [Metered.ca](https://www.metered.ca/tools/openrelay/)

### Browser Permissions

The app requires the following browser permissions:
- **Camera** - For video calls
- **Microphone** - For audio in both video and audio calls

Users will be prompted to grant these permissions when initiating or accepting a call.

## Known Limitations

1. **Peer-to-Peer Only**: Direct browser-to-browser connection. No media server for:
   - Recording (can be added with MediaRecorder API)
   - Group calls (requires SFU/MCU)
   - Broadcasting

2. **NAT Traversal**: Some corporate firewalls may block WebRTC. Use TURN servers in production.

3. **Browser Support**: Requires modern browsers with WebRTC support:
   - Chrome 56+
   - Firefox 52+
   - Safari 11+
   - Edge 79+

4. **No Call Queuing**: Only one active call per session at a time.

## Future Enhancements

- [ ] Screen sharing
- [ ] Call recording (MediaRecorder API)
- [ ] Call quality indicators
- [ ] Bandwidth adaptation
- [ ] Virtual backgrounds
- [ ] Group video calls (requires SFU)
- [ ] Call history/logs
- [ ] Push notifications for missed calls
- [ ] Mobile app support (React Native)

## Troubleshooting

### No Video/Audio

1. Check browser permissions (camera/microphone)
2. Verify HTTPS is enabled (WebRTC requires secure context)
3. Check if devices are in use by another app
4. Try different browser

### Connection Fails

1. Check STUN/TURN server configuration
2. Verify Socket.IO connection is active
3. Check firewall settings
4. Try using TURN server instead of STUN only

### One-Way Audio/Video

1. Check ICE candidate exchange in browser console
2. Verify both peers have proper permissions
3. Check for asymmetric NAT issues (use TURN)

## Security Considerations

1. **Authentication**: All signaling events verify JWT token
2. **Authorization**: Session participation checked before allowing calls
3. **Media**: WebRTC uses DTLS-SRTP for encrypted media streams
4. **Signaling**: Use WSS (WebSocket Secure) in production
5. **CORS**: Configure properly for production domain

## Performance

- **Bandwidth**: ~1-2 Mbps for video, ~100 Kbps for audio
- **Latency**: Typically 50-200ms peer-to-peer
- **CPU**: Hardware acceleration recommended for video encoding/decoding

## Dependencies

**Backend:**
- `python-socketio[asyncio]` - Already installed

**Frontend:**
- `socket.io-client` - Already installed
- No additional packages required (uses native WebRTC APIs)

## References

- [WebRTC Specification](https://www.w3.org/TR/webrtc/)
- [MDN WebRTC API](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)
- [Socket.IO Documentation](https://socket.io/docs/v4/)
