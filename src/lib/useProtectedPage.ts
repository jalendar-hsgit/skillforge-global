// src/lib/useProtectedPage.ts
/**
 * Hook for protecting pages that require authentication
 * Usage:
 * const { user, loading, isAuthorized } = useProtectedPage('admin')
 */

import { useRouter } from 'next/router'
import { useMe } from './useMe'
import { useEffect, useState } from 'react'

export function useProtectedPage(requiredRole?: string) {
  const router = useRouter()
  const { me, loading, error } = useMe()
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false)

  useEffect(() => {
    // Wait for loading to complete
    if (loading) return

    setHasCheckedAuth(true)

    // Not authenticated
    if (!me) {
      router.push(`/login?redirect=${encodeURIComponent(router.asPath)}`)
      return
    }

    // Check role if required
    if (requiredRole) {
      const userRole = me.role?.toLowerCase() || 'user'
      const roleHierarchy: Record<string, string[]> = {
        user: ['user', 'mentor', 'admin', 'superadmin'],
        seller: ['seller', 'mentor', 'admin', 'superadmin'],
        mentor: ['mentor', 'admin', 'superadmin'],
        admin: ['admin', 'superadmin'],
        superadmin: ['superadmin'],
      }

      const hasAccess = (roleHierarchy[requiredRole] || []).includes(userRole)

      if (!hasAccess) {
        router.push('/unauthorized')
        return
      }
    }
  }, [loading, me, requiredRole, router])

  return {
    user: me,
    loading: loading || !hasCheckedAuth,
    isAuthorized: me ? true : false,
    error,
  }
}
