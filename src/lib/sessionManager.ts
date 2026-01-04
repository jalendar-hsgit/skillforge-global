/**
 * Session Management - Auto-logout after inactivity
 * Provides session timeout tracking and management
 */

import { useRouter } from 'next/router'
import { useEffect, useRef } from 'react'

const SESSION_TIMEOUT = 30 * 60 * 1000 // 30 minutes
const WARNING_TIME = 5 * 60 * 1000 // Show warning at 25 minutes

let timeoutId: NodeJS.Timeout | null = null
let warningTimeoutId: NodeJS.Timeout | null = null

/**
 * Reset session timer on user activity
 */
export const resetSessionTimer = () => {
  if (timeoutId) clearTimeout(timeoutId)
  if (warningTimeoutId) clearTimeout(warningTimeoutId)

  // Warning at 25 minutes
  warningTimeoutId = setTimeout(() => {
    const event = new CustomEvent('sessionWarning', {
      detail: { minutesRemaining: 5 }
    })
    window.dispatchEvent(event)
  }, SESSION_TIMEOUT - WARNING_TIME)

  // Logout at 30 minutes
  timeoutId = setTimeout(() => {
    const event = new CustomEvent('sessionTimeout')
    window.dispatchEvent(event)
  }, SESSION_TIMEOUT)
}

/**
 * Hook: Enable session timeout
 * Usage: call in Layout or main component
 */
export const useSessionTimeout = () => {
  const router = useRouter()
  const activityTimeout = useRef<NodeJS.Timeout | null>(null)

  // Handle timeout event
  useEffect(() => {
    const handleTimeout = async () => {
      console.warn('Session expired, logging out...')
      
      try {
        await fetch('/api/v1/auth/logout', {
          method: 'POST',
          credentials: 'include'
        })
      } catch (err) {
        console.error('Logout error:', err)
      }

      // Clear data
      localStorage.removeItem('token')
      sessionStorage.clear()

      // Redirect
      router.push('/login?session=expired')
    }

    window.addEventListener('sessionTimeout', handleTimeout as EventListener)
    return () => window.removeEventListener('sessionTimeout', handleTimeout as EventListener)
  }, [router])

  // Track activity
  useEffect(() => {
    const handleActivity = () => {
      resetSessionTimer()
    }

    const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click']
    
    events.forEach(event => {
      document.addEventListener(event, handleActivity, true)
    })

    // Start timer
    resetSessionTimer()

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, handleActivity, true)
      })
      if (timeoutId) clearTimeout(timeoutId)
      if (warningTimeoutId) clearTimeout(warningTimeoutId)
    }
  }, [])
}

export default useSessionTimeout
