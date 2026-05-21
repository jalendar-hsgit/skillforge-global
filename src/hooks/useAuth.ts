/**
 * useAuth hook - Authentication wrapper around useMe
 * Provides user authentication state and helper methods
 */
import { useMe, Me } from './useMe'
import { useRouter } from 'next/router'
import { useCallback } from 'react'

export interface AuthState {
  user: Me
  isAuthenticated: boolean
  isLoading: boolean
  isAdmin: boolean
  isMentor: boolean
  logout: () => Promise<void>
  requireAuth: () => boolean
}

export function useAuth(): AuthState {
  const { me, loading } = useMe()
  const router = useRouter()

  const logout = useCallback(async () => {
    try {
      await fetch('/api/session/logout', {
        method: 'POST',
        credentials: 'include'
      })
      // Redirect to home after logout
      router.push('/')
      // Force page reload to clear state
      window.location.href = '/'
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }, [router])

  const requireAuth = useCallback(() => {
    if (!loading && !me) {
      router.push('/login')
      return false
    }
    return true
  }, [loading, me, router])

  return {
    user: me,
    isAuthenticated: !!me,
    isLoading: loading,
    isAdmin: me?.role === 'admin',
    isMentor: me?.is_mentor === true || me?.role === 'mentor',
    logout,
    requireAuth
  }
}

export default useAuth
