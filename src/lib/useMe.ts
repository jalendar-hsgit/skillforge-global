import { useEffect, useState } from "react"

export function useMe() {
  const [me, setMe] = useState<{ id: number; email: string; name?: string; role?: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        // Try with credentials (cookies)
        let response = await fetch("/api/session/me", { 
          credentials: "include",
          method: "GET",
          headers: {
            'Accept': 'application/json',
          }
        })

        // If cookie-based auth fails, try with token from localStorage
        if (!response.ok) {
          const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
          if (token) {
            response = await fetch("/api/session/me", {
              method: "GET",
              headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json',
              }
            })
          }
        }

        if (!response.ok) {
          if (mounted) {
            setMe(null)
            setError(null) // Don't show error on 401, just means not logged in
          }
        } else {
          const data = await response.json()
          if (mounted) {
            setMe(data)
            setError(null)
          }
        }
      } catch (e: any) {
        console.error('useMe error:', e)
        if (mounted) {
          setMe(null)
          setError(e?.message || "failed to fetch user")
        }
      } finally {
        if (mounted) setLoading(false)
      }
    })()
    return () => { mounted = false }
  }, [])

  return { me, loading, error }
}
