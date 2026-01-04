/**
 * CSRF Protection Utilities
 * Provides token management and form protection for CSRF attacks
 */

import React from 'react'

/**
 * Get CSRF token from meta tag, sessionStorage, or generate new
 */
export const getCsrfToken = (): string => {
  // Check meta tag first
  if (typeof window !== 'undefined') {
    const metaTag = document.querySelector('meta[name="csrf-token"]')
    if (metaTag) {
      return metaTag.getAttribute('content') || ''
    }

    // Check sessionStorage
    const stored = sessionStorage.getItem('csrf_token')
    if (stored) return stored

    // Generate new token
    const token = generateToken()
    sessionStorage.setItem('csrf_token', token)
    return token
  }

  return ''
}

/**
 * Generate a random CSRF token
 */
const generateToken = (): string => {
  if (typeof window === 'undefined') return ''
  
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')
}

/**
 * Fetch wrapper that automatically adds CSRF token
 */
export const fetchWithCsrf = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = getCsrfToken()
  
  const headers = new Headers(options.headers || {})
  headers.set('X-CSRF-Token', token)
  
  return fetch(url, {
    ...options,
    headers
  })
}

/**
 * Hook: Use CSRF token in React components
 */
export const useCsrfToken = (): string => {
  return getCsrfToken()
}

/**
 * Hook: Wrap form submission with CSRF protection
 */
export const useProtectedForm = (onSubmit: (data: any) => Promise<void>) => {
  const csrfToken = getCsrfToken()
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const formData = new FormData(e.currentTarget)
      formData.append('csrf_token', csrfToken)
      
      const data = Object.fromEntries(formData)
      await onSubmit(data)
    } catch (err: any) {
      setError(err?.message || 'An error occurred')
      handleCsrfError(err)
    } finally {
      setLoading(false)
    }
  }

  return { handleSubmit, csrfToken, loading, error }
}

/**
 * Handle CSRF token errors
 */
export const handleCsrfError = (error: any) => {
  if (error?.status === 403 && error?.message?.includes('CSRF')) {
    console.error('CSRF token validation failed')
    // Clear stored token to force regeneration
    sessionStorage.removeItem('csrf_token')
  }
}
