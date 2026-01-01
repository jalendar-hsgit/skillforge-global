/**
 * useRealtimeEvents Hook - Phase 3.6
 * WebSocket hook for consuming real-time events from backend
 * Handles learning paths, messaging, forum, notifications, gamification
 */

import { useEffect, useRef, useState, useCallback } from 'react'
import { useAuth } from './useAuth'

export enum EventType {
  // Learning paths
  PATH_PROGRESS_UPDATE = 'path_progress',
  CHALLENGE_COMPLETED = 'challenge_completed',
  PATH_COMPLETED = 'path_completed',
  CERTIFICATE_EARNED = 'certificate_earned',
  RECOMMENDATION_CREATED = 'recommendation_created',

  // Messaging & Forum
  MESSAGE_SENT = 'message_sent',
  FORUM_THREAD_CREATED = 'forum_thread_created',
  FORUM_REPLY_POSTED = 'forum_reply_posted',

  // Core
  NOTIFICATION_CREATED = 'notification_created',
  USER_ONLINE = 'user_online',
  USER_OFFLINE = 'user_offline',
  SKILL_VALIDATED = 'skill_validated',

  // Gamification
  BADGE_EARNED = 'badge_earned',
  COIN_EARNED = 'coin_earned',
}

export interface RealtimeEvent {
  event_type: EventType
  user_id: number
  target_user_id?: number
  data: Record<string, any>
  timestamp: string
}

export interface EventHandler {
  (event: RealtimeEvent): void
}

export interface UseRealtimeEventsOptions {
  enabled?: boolean
  onEvent?: EventHandler
  onError?: (error: Error) => void
  onConnected?: () => void
  onDisconnected?: () => void
  autoReconnect?: boolean
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'
const WS_URL = API_BASE.replace('http', 'ws')

export function useRealtimeEvents({
  enabled = true,
  onEvent,
  onError,
  onConnected,
  onDisconnected,
  autoReconnect = true,
}: UseRealtimeEventsOptions = {}) {
  const { user } = useAuth()
  const wsRef = useRef<WebSocket | null>(null)
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 5

  const [connected, setConnected] = useState(false)
  const [eventLog, setEventLog] = useState<RealtimeEvent[]>([])
  const [userStatuses, setUserStatuses] = useState<Record<number, boolean>>({})

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (!enabled || !user?.id) return
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    try {
      // Create WebSocket URL with user token
      const wsEndpoint = `${WS_URL}/api/v1/ws/connect/user_${user.id}_token`
      console.log('[RealtimeEvents] Connecting to:', wsEndpoint)

      const ws = new WebSocket(wsEndpoint)

      ws.onopen = () => {
        console.log('[RealtimeEvents] Connected')
        setConnected(true)
        reconnectAttemptsRef.current = 0
        onConnected?.()

        // Start heartbeat
        startHeartbeat(ws)
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)

          // Handle heartbeat ACK
          if (message.type === 'heartbeat_ack') {
            console.debug('[RealtimeEvents] Heartbeat ACK received')
            return
          }

          // Handle error messages
          if (message.type === 'error') {
            console.error('[RealtimeEvents] Server error:', message.message)
            onError?.(new Error(message.message))
            return
          }

          // Handle event
          if (message.event_type) {
            const realtimeEvent: RealtimeEvent = message
            console.log('[RealtimeEvents] Event received:', realtimeEvent.event_type)

            // Track user online status
            if (realtimeEvent.event_type === EventType.USER_ONLINE) {
              setUserStatuses((prev) => ({
                ...prev,
                [realtimeEvent.user_id]: true,
              }))
            } else if (realtimeEvent.event_type === EventType.USER_OFFLINE) {
              setUserStatuses((prev) => ({
                ...prev,
                [realtimeEvent.user_id]: false,
              }))
            }

            // Add to event log (keep last 50)
            setEventLog((prev) => [realtimeEvent, ...prev].slice(0, 50))

            // Call handler
            onEvent?.(realtimeEvent)
          }
        } catch (error) {
          console.error('[RealtimeEvents] Failed to parse message:', error)
          onError?.(error instanceof Error ? error : new Error(String(error)))
        }
      }

      ws.onerror = (error) => {
        console.error('[RealtimeEvents] WebSocket error:', error)
        onError?.(new Error('WebSocket connection error'))
      }

      ws.onclose = () => {
        console.log('[RealtimeEvents] Connection closed')
        setConnected(false)
        stopHeartbeat()
        onDisconnected?.()

        // Attempt reconnection
        if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
          console.log(`[RealtimeEvents] Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current})`)

          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, delay)
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('[RealtimeEvents] Failed to create WebSocket:', error)
      onError?.(error instanceof Error ? error : new Error(String(error)))
    }
  }, [enabled, user?.id, onEvent, onError, onConnected, onDisconnected, autoReconnect])

  // Disconnect WebSocket
  const disconnect = useCallback(() => {
    stopHeartbeat()

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setConnected(false)
    setEventLog([])
    setUserStatuses({})
  }, [])

  // Start heartbeat
  const startHeartbeat = (ws: WebSocket) => {
    stopHeartbeat()

    heartbeatIntervalRef.current = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        try {
          ws.send(JSON.stringify({ type: 'heartbeat' }))
        } catch (error) {
          console.error('[RealtimeEvents] Failed to send heartbeat:', error)
        }
      }
    }, 30000) // Send heartbeat every 30 seconds
  }

  // Stop heartbeat
  const stopHeartbeat = () => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current)
      heartbeatIntervalRef.current = null
    }
  }

  // Get user online status
  const isUserOnline = useCallback(
    (userId: number): boolean | undefined => {
      return userStatuses[userId]
    },
    [userStatuses]
  )

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect()

    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    connected,
    eventLog,
    userStatuses,
    isUserOnline,
    connect,
    disconnect,
  }
}
