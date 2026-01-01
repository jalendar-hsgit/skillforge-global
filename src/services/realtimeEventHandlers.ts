/**
 * Realtime Event Handlers - Phase 3.6
 * Business logic for handling different event types
 */

import { RealtimeEvent, EventType } from '../hooks/useRealtimeEvents'

export interface EventHandlerContext {
  showNotification?: (message: string, type?: 'success' | 'info' | 'warning' | 'error') => void
  updateProgressBar?: (pathId: number, percentage: number) => void
  refreshLearningPath?: (pathId: number) => void
  refreshMessages?: (conversationId?: number) => void
  refreshNotifications?: () => void
  refreshSkills?: () => void
  refreshLeaderboard?: () => void
  onChallengeCompleted?: (data: any) => void
  onPathCompleted?: (data: any) => void
  onCertificateEarned?: (data: any) => void
  onMessageReceived?: (data: any) => void
  onForumReply?: (data: any) => void
}

/**
 * Handle learning path progress update
 */
export async function handlePathProgressUpdate(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  const {
    path_id,
    completed_challenges,
    total_challenges,
    completion_percentage,
  } = event.data

  console.log(`[EventHandler] Path progress: ${completion_percentage}%`)

  context.updateProgressBar?.(path_id, completion_percentage)
  context.showNotification?.(
    `Learning Path: ${completed_challenges}/${total_challenges} challenges completed`,
    'info'
  )
}

/**
 * Handle challenge completion
 */
export async function handleChallengeCompleted(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  const {
    path_id,
    challenge_id,
    challenge_name,
    points_earned,
    completion_percentage,
  } = event.data

  console.log(`[EventHandler] Challenge completed: ${challenge_name}`)

  context.updateProgressBar?.(path_id, completion_percentage)
  context.showNotification?.(
    `🎉 Challenge "${challenge_name}" completed! +${points_earned} points`,
    'success'
  )
  context.onChallengeCompleted?.({ path_id, challenge_id, points_earned })
  context.refreshLearningPath?.(path_id)
}

/**
 * Handle path completion
 */
export async function handlePathCompleted(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  const { path_id, completion_percentage, points_earned } = event.data

  console.log(`[EventHandler] Path completed: ${path_id}`)

  context.updateProgressBar?.(path_id, 100)
  context.showNotification?.(
    `🏆 Path completed! You earned ${points_earned} points`,
    'success'
  )
  context.onPathCompleted?.({ path_id, points_earned })
  context.refreshLearningPath?.(path_id)
}

/**
 * Handle certificate earned
 */
export async function handleCertificateEarned(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  const { certificate_id, certificate_number, path_title, issue_date } = event.data

  console.log(`[EventHandler] Certificate earned: ${certificate_number}`)

  context.showNotification?.(
    `📜 Certificate earned for "${path_title}"! Certificate #${certificate_number}`,
    'success'
  )
  context.onCertificateEarned?.({ certificate_id, certificate_number, path_title })
}

/**
 * Handle recommendation created
 */
export async function handleRecommendationCreated(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  const {
    recommendation_id,
    path_id,
    path_title,
    reason,
  } = event.data

  console.log(`[EventHandler] Recommendation created: ${path_title}`)

  context.showNotification?.(
    `💡 New recommendation: "${path_title}" - ${reason}`,
    'info'
  )
}

/**
 * Handle message sent
 */
export async function handleMessageSent(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  const {
    message_id,
    conversation_id,
    sender_id,
    sender_name,
    content,
  } = event.data

  console.log(`[EventHandler] Message from ${sender_name}: ${content}`)

  context.onMessageReceived?.({ message_id, conversation_id, sender_id, sender_name, content })
  context.refreshMessages?.(conversation_id)
}

/**
 * Handle forum thread created
 */
export async function handleForumThreadCreated(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  const { thread_id, topic_id, author_name, title, created_at } = event.data

  console.log(`[EventHandler] Forum thread: ${title}`)

  context.showNotification?.(
    `📝 New forum thread by ${author_name}: "${title}"`,
    'info'
  )
}

/**
 * Handle forum reply posted
 */
export async function handleForumReplyPosted(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  const { reply_id, thread_id, author_name, content } = event.data

  console.log(`[EventHandler] Forum reply from ${author_name}`)

  context.onForumReply?.({ reply_id, thread_id, author_name })
}

/**
 * Handle notification created
 */
export async function handleNotificationCreated(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  const { notification_id, type, title, description } = event.data

  console.log(`[EventHandler] Notification: ${title}`)

  context.showNotification?.(title, 'info')
  context.refreshNotifications?.()
}

/**
 * Handle skill validated
 */
export async function handleSkillValidated(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  const { skill_name, proficiency_level, endorsement_count } = event.data

  console.log(`[EventHandler] Skill validated: ${skill_name} (${proficiency_level})`)

  context.showNotification?.(
    `✅ Skill "${skill_name}" validated at ${proficiency_level} level (+${endorsement_count} endorsements)`,
    'success'
  )
  context.refreshSkills?.()
}

/**
 * Handle badge earned
 */
export async function handleBadgeEarned(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  const { badge_id, badge_name, badge_description } = event.data

  console.log(`[EventHandler] Badge earned: ${badge_name}`)

  context.showNotification?.(
    `🏅 Badge earned: ${badge_name}`,
    'success'
  )
}

/**
 * Handle coins earned
 */
export async function handleCoinEarned(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  const { amount, reason, total_coins } = event.data

  console.log(`[EventHandler] Coins earned: ${amount} (${reason})`)

  context.showNotification?.(
    `💰 +${amount} coins earned! ${reason}${total_coins ? ` (Total: ${total_coins})` : ''}`,
    'success'
  )
}

/**
 * Handle user online/offline
 */
export async function handleUserStatusChange(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  const { event_type, user_id } = event

  const status = event_type === EventType.USER_ONLINE ? 'online' : 'offline'
  console.log(`[EventHandler] User ${user_id} is now ${status}`)

  // Could update user presence indicators, etc.
}

/**
 * Main event router - dispatches to appropriate handler
 */
export async function handleRealtimeEvent(
  event: RealtimeEvent,
  context: EventHandlerContext
) {
  try {
    switch (event.event_type) {
      case EventType.PATH_PROGRESS_UPDATE:
        return handlePathProgressUpdate(event, context)
      case EventType.CHALLENGE_COMPLETED:
        return handleChallengeCompleted(event, context)
      case EventType.PATH_COMPLETED:
        return handlePathCompleted(event, context)
      case EventType.CERTIFICATE_EARNED:
        return handleCertificateEarned(event, context)
      case EventType.RECOMMENDATION_CREATED:
        return handleRecommendationCreated(event, context)
      case EventType.MESSAGE_SENT:
        return handleMessageSent(event, context)
      case EventType.FORUM_THREAD_CREATED:
        return handleForumThreadCreated(event, context)
      case EventType.FORUM_REPLY_POSTED:
        return handleForumReplyPosted(event, context)
      case EventType.NOTIFICATION_CREATED:
        return handleNotificationCreated(event, context)
      case EventType.SKILL_VALIDATED:
        return handleSkillValidated(event, context)
      case EventType.BADGE_EARNED:
        return handleBadgeEarned(event, context)
      case EventType.COIN_EARNED:
        return handleCoinEarned(event, context)
      case EventType.USER_ONLINE:
      case EventType.USER_OFFLINE:
        return handleUserStatusChange(event, context)
      default:
        console.warn('[EventHandler] Unknown event type:', event.event_type)
    }
  } catch (error) {
    console.error('[EventHandler] Error handling event:', error)
  }
}
