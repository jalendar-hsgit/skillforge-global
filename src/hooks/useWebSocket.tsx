import { useEffect, useRef, useState, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'

interface WebSocketUser {
  id: string
  name: string
  color: string
  cursor?: { x: number; y: number }
}

interface WebSocketMessage {
  type: 'update' | 'cursor' | 'user_join' | 'user_leave'
  userId: string
  data?: any
  timestamp: number
}

interface UseWebSocketOptions {
  resumeId: string
  userId: string
  userName: string
  onUpdate?: (data: any) => void
  onUserJoin?: (user: WebSocketUser) => void
  onUserLeave?: (userId: string) => void
  enabled?: boolean
}

export function useWebSocket({
  resumeId,
  userId,
  userName,
  onUpdate,
  onUserJoin,
  onUserLeave,
  enabled = true,
}: UseWebSocketOptions) {
  const [connected, setConnected] = useState(false)
  const [activeUsers, setActiveUsers] = useState<WebSocketUser[]>([])
  const socketRef = useRef<Socket | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  // Generate a consistent color for this user
  const userColor = useRef(
    `hsl(${Math.floor(Math.random() * 360)}, 70%, 60%)`
  ).current

  const connect = useCallback(() => {
    if (!enabled || socketRef.current?.connected) return

    const socket = io(process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:8001', {
      transports: ['websocket', 'polling'],
      auth: {
        userId,
        userName,
        resumeId,
        color: userColor,
      },
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: maxReconnectAttempts,
    })

    socket.on('connect', () => {
      console.log('[WebSocket] Connected to collaboration server')
      setConnected(true)
      reconnectAttempts.current = 0
      
      // Join the resume room
      socket.emit('join_resume', { resumeId, userId, userName, color: userColor })
    })

    socket.on('disconnect', () => {
      console.log('[WebSocket] Disconnected from collaboration server')
      setConnected(false)
    })

    socket.on('connect_error', (error) => {
      console.error('[WebSocket] Connection error:', error)
      reconnectAttempts.current++
      
      if (reconnectAttempts.current >= maxReconnectAttempts) {
        console.error('[WebSocket] Max reconnection attempts reached')
        socket.disconnect()
      }
    })

    // Handle resume updates from other users
    socket.on('resume_update', (message: WebSocketMessage) => {
      if (message.userId !== userId && onUpdate) {
        onUpdate(message.data)
      }
    })

    // Handle cursor movements
    socket.on('cursor_move', (data: { userId: string; position: { x: number; y: number } }) => {
      setActiveUsers((users) =>
        users.map((user) =>
          user.id === data.userId
            ? { ...user, cursor: data.position }
            : user
        )
      )
    })

    // Handle user joining
    socket.on('user_joined', (user: WebSocketUser) => {
      console.log('[WebSocket] User joined:', user.name)
      setActiveUsers((users) => {
        if (users.some((u) => u.id === user.id)) return users
        return [...users, user]
      })
      onUserJoin?.(user)
    })

    // Handle user leaving
    socket.on('user_left', (data: { userId: string }) => {
      console.log('[WebSocket] User left:', data.userId)
      setActiveUsers((users) => users.filter((u) => u.id !== data.userId))
      onUserLeave?.(data.userId)
    })

    // Sync active users list
    socket.on('active_users', (users: WebSocketUser[]) => {
      setActiveUsers(users.filter((u) => u.id !== userId))
    })

    socketRef.current = socket
  }, [enabled, resumeId, userId, userName, userColor, onUpdate, onUserJoin, onUserLeave])

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect()
      socketRef.current = null
      setConnected(false)
      setActiveUsers([])
    }
  }, [])

  const sendUpdate = useCallback((data: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('resume_update', {
        resumeId,
        userId,
        data,
        timestamp: Date.now(),
      })
    }
  }, [resumeId, userId])

  const sendCursor = useCallback((position: { x: number; y: number }) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('cursor_move', {
        resumeId,
        userId,
        position,
      })
    }
  }, [resumeId, userId])

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return {
    connected,
    activeUsers,
    sendUpdate,
    sendCursor,
    reconnect: connect,
    disconnect,
  }
}

// Presence indicator component
interface PresenceIndicatorProps {
  users: WebSocketUser[]
  maxVisible?: number
}

export function PresenceIndicator({ users, maxVisible = 5 }: PresenceIndicatorProps) {
  const visibleUsers = users.slice(0, maxVisible)
  const remainingCount = users.length - maxVisible

  if (users.length === 0) return null

  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center -space-x-2">
        {visibleUsers.map((user) => (
          <div
            key={user.id}
            className="w-8 h-8 rounded-full border-2 border-white flex items-center justify-center text-xs font-bold text-white shadow-lg"
            style={{ backgroundColor: user.color }}
            title={user.name}
          >
            {user.name.charAt(0).toUpperCase()}
          </div>
        ))}
        {remainingCount > 0 && (
          <div className="w-8 h-8 rounded-full border-2 border-white bg-gray-700 flex items-center justify-center text-xs font-bold text-white shadow-lg">
            +{remainingCount}
          </div>
        )}
      </div>
      <span className="text-xs text-white/60">
        {users.length} {users.length === 1 ? 'person' : 'people'} editing
      </span>
    </div>
  )
}

// Cursor component for showing other users' cursors
interface RemoteCursorProps {
  user: WebSocketUser
}

export function RemoteCursor({ user }: RemoteCursorProps) {
  if (!user.cursor) return null

  return (
    <div
      className="fixed pointer-events-none z-[9999] transition-all duration-100"
      style={{
        left: user.cursor.x,
        top: user.cursor.y,
        transform: 'translate(-50%, -50%)',
      }}
    >
      {/* Cursor pointer */}
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M5 3L19 12L12 13L9 19L5 3Z"
          fill={user.color}
          stroke="white"
          strokeWidth="1.5"
        />
      </svg>
      
      {/* User name label */}
      <div
        className="absolute top-6 left-0 px-2 py-1 rounded text-xs font-medium text-white whitespace-nowrap shadow-lg"
        style={{ backgroundColor: user.color }}
      >
        {user.name}
      </div>
    </div>
  )
}
