/**
 * RealtimeNotification Component - Phase 3.6
 * Toast notifications for real-time events
 */

import React, { useState, useEffect } from 'react'

export type NotificationType = 'success' | 'info' | 'warning' | 'error'

export interface ToastNotification {
  id: string
  message: string
  type: NotificationType
  duration?: number
}

interface RealtimeNotificationProps {
  notifications: ToastNotification[]
  onDismiss: (id: string) => void
}

const typeStyles: Record<NotificationType, { bg: string; border: string; icon: string }> = {
  success: {
    bg: 'bg-green-50 dark:bg-green-900/20',
    border: 'border-green-200 dark:border-green-800',
    icon: '✓',
  },
  info: {
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    border: 'border-blue-200 dark:border-blue-800',
    icon: 'ℹ',
  },
  warning: {
    bg: 'bg-yellow-50 dark:bg-yellow-900/20',
    border: 'border-yellow-200 dark:border-yellow-800',
    icon: '⚠',
  },
  error: {
    bg: 'bg-red-50 dark:bg-red-900/20',
    border: 'border-red-200 dark:border-red-800',
    icon: '✕',
  },
}

function Toast({ notification, onDismiss }: { notification: ToastNotification; onDismiss: () => void }) {
  const styles = typeStyles[notification.type]

  useEffect(() => {
    if (notification.duration) {
      const timer = setTimeout(onDismiss, notification.duration)
      return () => clearTimeout(timer)
    }
  }, [notification.id, notification.duration, onDismiss])

  return (
    <div
      className={`
        flex items-start gap-3 px-4 py-3 rounded-lg border
        ${styles.bg} ${styles.border}
        animate-in fade-in slide-in-from-top-2 duration-300
      `}
    >
      <span className="flex-shrink-0 text-lg font-bold text-current">
        {styles.icon}
      </span>
      <p className="flex-1 text-sm font-medium">{notification.message}</p>
      <button
        onClick={onDismiss}
        className="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
      >
        ×
      </button>
    </div>
  )
}

export function RealtimeNotificationContainer({
  notifications,
  onDismiss,
}: RealtimeNotificationProps) {
  if (notifications.length === 0) {
    return null
  }

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md pointer-events-auto">
      {notifications.map((notification) => (
        <Toast
          key={notification.id}
          notification={notification}
          onDismiss={() => onDismiss(notification.id)}
        />
      ))}
    </div>
  )
}

/**
 * Hook for managing toast notifications
 */
export function useToastNotifications() {
  const [notifications, setNotifications] = useState<ToastNotification[]>([])

  const showNotification = (
    message: string,
    type: NotificationType = 'info',
    duration: number = 5000
  ) => {
    const id = `${Date.now()}-${Math.random()}`
    const notification: ToastNotification = { id, message, type, duration }

    setNotifications((prev) => [...prev, notification])

    return id
  }

  const dismissNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }

  const dismissAll = () => {
    setNotifications([])
  }

  return {
    notifications,
    showNotification,
    dismissNotification,
    dismissAll,
  }
}
