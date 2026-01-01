/**
 * RealtimeEventsContext - Phase 3.6
 * Context provider for real-time events throughout the app
 */

import React, { createContext, useContext, ReactNode } from 'react'
import { useRealtimeEvents, EventType, RealtimeEvent, EventHandler } from '../hooks/useRealtimeEvents'

interface RealtimeEventsContextType {
  connected: boolean
  eventLog: RealtimeEvent[]
  userStatuses: Record<number, boolean>
  isUserOnline: (userId: number) => boolean | undefined
  onEvent: (handler: EventHandler) => void
  connect: () => void
  disconnect: () => void
}

const RealtimeEventsContext = createContext<RealtimeEventsContextType | undefined>(undefined)

interface RealtimeEventsProviderProps {
  children: ReactNode
  enabled?: boolean
}

export function RealtimeEventsProvider({
  children,
  enabled = true,
}: RealtimeEventsProviderProps) {
  const eventHandlers = React.useRef<Set<EventHandler>>(new Set())

  const { connected, eventLog, userStatuses, isUserOnline, connect, disconnect } =
    useRealtimeEvents({
      enabled,
      onEvent: (event) => {
        // Call all registered handlers
        eventHandlers.current.forEach((handler) => {
          try {
            handler(event)
          } catch (error) {
            console.error('[RealtimeEventsProvider] Handler error:', error)
          }
        })
      },
    })

  const onEvent = React.useCallback((handler: EventHandler) => {
    eventHandlers.current.add(handler)
    return () => {
      eventHandlers.current.delete(handler)
    }
  }, [])

  const value: RealtimeEventsContextType = {
    connected,
    eventLog,
    userStatuses,
    isUserOnline,
    onEvent,
    connect,
    disconnect,
  }

  return (
    <RealtimeEventsContext.Provider value={value}>
      {children}
    </RealtimeEventsContext.Provider>
  )
}

export function useRealtimeEventsContext() {
  const context = useContext(RealtimeEventsContext)
  if (!context) {
    throw new Error('useRealtimeEventsContext must be used within RealtimeEventsProvider')
  }
  return context
}
