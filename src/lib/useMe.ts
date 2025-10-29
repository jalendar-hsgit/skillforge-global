import { useEffect, useState } from "react"

export function useMe() {
  const [me, setMe] = useState<{ id: number; email: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        const r = await fetch("/api/session/me", { credentials: "include" } as RequestInit)
        if (!r.ok) {
          setMe(null)
        } else {
          const data = await r.json()
          if (mounted) setMe(data)
        }
      } catch (e: any) {
        if (mounted) setError(e?.message || "failed")
      } finally {
        if (mounted) setLoading(false)
      }
    })()
    return () => { mounted = false }
  }, [])

  return { me, loading, error }
}
