/**
 * App Root Component with Realtime Integration - Phase 3.6
 * This component should wrap your main app to enable real-time events
 */

'use client'

import React, { useCallback, useEffect } from 'react'
import { RealtimeEventsProvider, useRealtimeEventsContext } from '@/context/RealtimeEventsContext'
import {
  RealtimeNotificationContainer,
  useToastNotifications,
} from '@/components/RealtimeNotification'
import { handleRealtimeEvent, EventHandlerContext } from '@/services/realtimeEventHandlers'

/**
 * Inner component that uses the RealtimeEventsContext
 * This must be inside RealtimeEventsProvider
 */
function RealtimeEventHandler() {
  const { onEvent, connected } = useRealtimeEventsContext()
  const { notifications, showNotification, dismissNotification } = useToastNotifications()

  // Create event handler context with notification support
  const createContext = useCallback((): EventHandlerContext => {
    return {
      showNotification: (message, type = 'info') => {
        showNotification(message, type, 5000)
      },
      // These will be implemented by specific pages/components
      // using their own hooks (useLearningPathRealtime, useMessagingRealtime, etc.)
      updateProgressBar: undefined,
      refreshLearningPath: undefined,
      refreshMessages: undefined,
      refreshNotifications: undefined,
      refreshSkills: undefined,
      refreshLeaderboard: undefined,
      onChallengeCompleted: undefined,
      onPathCompleted: undefined,
      onCertificateEarned: undefined,
      onMessageReceived: undefined,
      onForumReply: undefined,
    }
  }, [showNotification])

  // Register main event handler
  useEffect(() => {
    const context = createContext()
    const unsubscribe = onEvent((event) => {
      handleRealtimeEvent(event, context)
    })

    return unsubscribe
  }, [onEvent, createContext])

  // Show connection status
  useEffect(() => {
    if (connected) {
      console.log('[Realtime] Connected to server')
    } else {
      console.log('[Realtime] Disconnected from server')
    }
  }, [connected])

  return <RealtimeNotificationContainer notifications={notifications} onDismiss={dismissNotification} />
}

/**
 * Wrapper component for your app
 * Usage: Wrap your main App component with this
 *
 * Example in your main layout or _app.tsx:
 * ```
 * export default function RootLayout() {
 *   return (
 *     <RealtimeAppWrapper>
 *       <YourAppContent />
 *     </RealtimeAppWrapper>
 *   )
 * }
 * ```
 */
export function RealtimeAppWrapper({ children }: { children: React.ReactNode }) {
  return (
    <RealtimeEventsProvider enabled={true}>
      <RealtimeEventHandler />
      {children}
    </RealtimeEventsProvider>
  )
}

/**
 * HOC for wrapping your app
 * Usage: export default withRealtimeEvents(YourApp)
 */
export function withRealtimeEvents<P extends object>(
  Component: React.ComponentType<P>
): React.FC<P> {
  return function WithRealtimeEventsComponent(props: P) {
    return (
      <RealtimeAppWrapper>
        <Component {...props} />
      </RealtimeAppWrapper>
    )
  }
}
