import { useEffect, useState } from 'react'
export type Me = { 
  id: number
  email: string
  full_name?: string
  role?: 'user' | 'mentor' | 'admin'
  is_mentor?: boolean
} | null

export function useMe() {
  const [me, setMe] = useState<Me>(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    let mounted = true
    
    const checkSession = async () => {
      try {
        const response = await fetch('/api/session/me', {
          credentials: 'include'
        })
        if (!mounted) return
        if (!response.ok) {
          setMe(null)
          setLoading(false)
          return
        }
        const data = await response.json()
        setMe(data)
      } catch (err) {
        if (mounted) {
          setMe(null)
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    checkSession()
    return () => { mounted = false }
  }, [])
  return { me, loading }
}
