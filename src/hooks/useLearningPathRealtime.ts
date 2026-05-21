/**
 * useLearningPathRealtime Hook - Phase 3.6
 * Real-time updates for learning paths pages
 */

import { useEffect, useCallback, useState } from 'react'
import { useRealtimeEventsContext } from '../context/RealtimeEventsContext'
import { EventType, RealtimeEvent } from '../hooks/useRealtimeEvents'
import { handleRealtimeEvent, EventHandlerContext } from '../services/realtimeEventHandlers'

interface UseLearningPathRealtimeOptions {
  pathId?: number
  onProgressUpdate?: (percentage: number) => void
  onChallengeCompleted?: (challengeId: number, points: number) => void
  onPathCompleted?: () => void
  onCertificateEarned?: (certificateNumber: string) => void
}

export function useLearningPathRealtime({
  pathId,
  onProgressUpdate,
  onChallengeCompleted,
  onPathCompleted,
  onCertificateEarned,
}: UseLearningPathRealtimeOptions = {}) {
  const { onEvent } = useRealtimeEventsContext()

  // Handlers for events
  const context: EventHandlerContext = {
    showNotification: (message, type) => {
      // Notifications are shown separately
      console.log(`[Notification] ${type?.toUpperCase()}: ${message}`)
    },
    updateProgressBar: (id, percentage) => {
      if (!pathId || id === pathId) {
        onProgressUpdate?.(percentage)
      }
    },
    onChallengeCompleted: (data) => {
      onChallengeCompleted?.(data.challenge_id, data.points_earned)
    },
    onPathCompleted: () => {
      onPathCompleted?.()
    },
    onCertificateEarned: (data) => {
      onCertificateEarned?.(data.certificate_number)
    },
  }

  // Register event listener
  useEffect(() => {
    const unsubscribe = onEvent((event: RealtimeEvent) => {
      // Filter events by path ID if specified
      if (pathId && event.data.path_id && event.data.path_id !== pathId) {
        return
      }

      // Handle learning path related events
      if (
        [
          EventType.PATH_PROGRESS_UPDATE,
          EventType.CHALLENGE_COMPLETED,
          EventType.PATH_COMPLETED,
          EventType.CERTIFICATE_EARNED,
        ].includes(event.event_type)
      ) {
        handleRealtimeEvent(event, context)
      }
    })

    return unsubscribe
  }, [pathId, onEvent, onProgressUpdate, onChallengeCompleted, onPathCompleted, onCertificateEarned])
}

/**
 * Hook for real-time updates on specific challenge
 */
export function useChallengeRealtime(
  pathId: number,
  challengeId: number,
  onCompleted?: () => void
) {
  const { onEvent } = useRealtimeEventsContext()

  useEffect(() => {
    const unsubscribe = onEvent((event: RealtimeEvent) => {
      if (
        event.event_type === EventType.CHALLENGE_COMPLETED &&
        event.data.path_id === pathId &&
        event.data.challenge_id === challengeId
      ) {
        console.log('[ChallengeRealtime] Challenge completed:', challengeId)
        onCompleted?.()
      }
    })

    return unsubscribe
  }, [pathId, challengeId, onEvent, onCompleted])
}

/**
 * Hook for real-time progress bar updates
 */
export function useProgressBarRealtime(pathId: number) {
  const { onEvent } = useRealtimeEventsContext()
  const [progress, setProgress] = useState<number>(0)

  useEffect(() => {
    const unsubscribe = onEvent((event: RealtimeEvent) => {
      if (
        event.event_type === EventType.PATH_PROGRESS_UPDATE &&
        event.data.path_id === pathId
      ) {
        setProgress(event.data.completion_percentage)
      } else if (
        event.event_type === EventType.CHALLENGE_COMPLETED &&
        event.data.path_id === pathId
      ) {
        setProgress(event.data.completion_percentage)
      }
    })

    return unsubscribe
  }, [pathId, onEvent])

  return progress
}
