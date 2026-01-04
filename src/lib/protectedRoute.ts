import { useRouter } from 'next/router'
import { useMe } from './useMe'

/**
 * Hook to check if user is authenticated and has required role
 */
export function useAuthCheck(requiredRole?: string) {
  const router = useRouter()
  const { me, loading } = useMe()

  // Still loading user data
  if (loading) {
    return { isAuthorized: undefined, user: me, loading: true }
  }

  // User is not authenticated
  if (!me) {
    if (typeof window !== 'undefined' && !router.pathname.includes('login')) {
      const redirectUrl = router.asPath.includes('?') 
        ? router.asPath 
        : `${router.pathname}${router.asPath.split(router.pathname)[1] || ''}`
      router.push(`/login?redirect=${encodeURIComponent(redirectUrl)}`)
    }
    return { isAuthorized: false, user: null, loading: false }
  }

  // Check role if required
  if (requiredRole) {
    const userRole = me.role?.toLowerCase() || 'user'
    let hasAccess = false

    const roleHierarchy: Record<string, string[]> = {
      user: ['user', 'mentor', 'admin', 'superadmin'],
      seller: ['seller', 'mentor', 'admin', 'superadmin'],
      mentor: ['mentor', 'admin', 'superadmin'],
      admin: ['admin', 'superadmin'],
      superadmin: ['superadmin'],
    }

    hasAccess = (roleHierarchy[requiredRole] || []).includes(userRole)

    if (!hasAccess && typeof window !== 'undefined') {
      router.push('/unauthorized')
    }

    return { isAuthorized: hasAccess, user: me, loading: false }
  }

  // User is authenticated and authorized
  return { isAuthorized: true, user: me, loading: false }
}
