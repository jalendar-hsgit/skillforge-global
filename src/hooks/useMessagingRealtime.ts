/**
 * useMessagingRealtime Hook - Phase 3.6
 * Real-time updates for messaging
 */

import { useEffect } from 'react'
import { useRealtimeEventsContext } from '../context/RealtimeEventsContext'
import { EventType, RealtimeEvent } from '../hooks/useRealtimeEvents'

interface UseMessagingRealtimeOptions {
  conversationId?: number
  onNewMessage?: (data: any) => void
  onMessageDelivered?: (messageId: number) => void
  onUserTyping?: (userId: number, isTyping: boolean) => void
}

export function useMessagingRealtime({
  conversationId,
  onNewMessage,
  onMessageDelivered,
  onUserTyping,
}: UseMessagingRealtimeOptions = {}) {
  const { onEvent } = useRealtimeEventsContext()

  useEffect(() => {
    const unsubscribe = onEvent((event: RealtimeEvent) => {
      if (event.event_type === EventType.MESSAGE_SENT) {
        // Check if this message is for our conversation
        if (!conversationId || event.data.conversation_id === conversationId) {
          console.log('[MessagingRealtime] New message:', event.data.content)
          onNewMessage?.(event.data)
        }
      }

      // Track message delivery
      if (
        event.event_type === EventType.MESSAGE_SENT &&
        event.data.status === 'delivered'
      ) {
        onMessageDelivered?.(event.data.message_id)
      }
    })

    return unsubscribe
  }, [conversationId, onEvent, onNewMessage, onMessageDelivered])
}

/**
 * Hook for forum real-time updates
 */
interface UseForumRealtimeOptions {
  topicId?: number
  threadId?: number
  onNewThread?: (data: any) => void
  onNewReply?: (data: any) => void
  onBestAnswerMarked?: (data: any) => void
}

export function useForumRealtime({
  topicId,
  threadId,
  onNewThread,
  onNewReply,
  onBestAnswerMarked,
}: UseForumRealtimeOptions = {}) {
  const { onEvent } = useRealtimeEventsContext()

  useEffect(() => {
    const unsubscribe = onEvent((event: RealtimeEvent) => {
      // New thread created
      if (event.event_type === EventType.FORUM_THREAD_CREATED) {
        if (!topicId || event.data.topic_id === topicId) {
          console.log('[ForumRealtime] New thread:', event.data.title)
          onNewThread?.(event.data)
        }
      }

      // New reply posted
      if (event.event_type === EventType.FORUM_REPLY_POSTED) {
        if (!threadId || event.data.thread_id === threadId) {
          console.log('[ForumRealtime] New reply')
          onNewReply?.(event.data)
        }
      }

      // Best answer marked
      if (
        event.event_type === EventType.FORUM_REPLY_POSTED &&
        event.data.action === 'best_answer_marked'
      ) {
        onBestAnswerMarked?.(event.data)
      }
    })

    return unsubscribe
  }, [topicId, threadId, onEvent, onNewThread, onNewReply, onBestAnswerMarked])
}

/**
 * Hook for user online status tracking
 */
export function useUserOnlineStatus() {
  const { isUserOnline, userStatuses } = useRealtimeEventsContext()

  return {
    isUserOnline,
    userStatuses,
  }
}
