import { useEffect, useState } from 'react'

export type PlanFeatures = {
  plan: 'FREE' | 'PRO' | 'ENTERPRISE'
  name: string
  description?: string
  monthly_price_cents: number
  annual_price_cents: number
  max_session_duration_minutes: number
  monthly_session_limit?: number | null
  can_share_files: boolean
  can_record_sessions: boolean
  can_access_ai_assistant: boolean
  can_book_mentors: boolean
  support_level: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

export function usePlanFeatures() {
  const [features, setFeatures] = useState<PlanFeatures | null>(null)
  const [plan, setPlan] = useState<'FREE'|'PRO'|'ENTERPRISE'|null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    const token = document.cookie.split('; ').find(r => r.startsWith('token='))?.split('=')[1]
    if (!token) {
      setLoading(false)
      return
    }
    const load = async () => {
      try {
        setLoading(true)
        const [subRes, featRes] = await Promise.all([
          fetch(`${API_BASE}/api/v1x/subscriptions/current`, { headers: { Authorization: `Bearer ${token}` } }),
          fetch(`${API_BASE}/api/v1x/subscriptions/features`, { headers: { Authorization: `Bearer ${token}` } }),
        ])
        if (subRes.ok) {
          const sub = await subRes.json()
          if (mounted) setPlan(sub.plan)
        }
        if (featRes.ok) {
          const f = await featRes.json()
          if (mounted) setFeatures(f)
        }
      } catch (e:any) {
        if (mounted) setError(e?.message || 'Failed to load features')
      } finally {
        if (mounted) setLoading(false)
      }
    }
    load()
    return () => { mounted = false }
  }, [])

  return { features, plan, loading, error }
}
