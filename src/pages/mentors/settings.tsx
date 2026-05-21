import { useEffect, useState } from 'react'
import Head from 'next/head'
import Layout from '@/components/Layout'
import { Card } from '@/components/Card'
import { Button } from '@/components/Button'
import { useMe } from '@/hooks/useMe'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

type ConnectStatus = {
  account_id?: string | null
  onboarding_complete: boolean
  payouts_enabled: boolean
  details_submitted: boolean
  requirements_due?: string | null
}

export default function MentorSettingsPage() {
  const { me, loading } = useMe()
  const [status, setStatus] = useState<ConnectStatus | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const authHeader = (): HeadersInit => {
    const token = document.cookie.split('; ').find(r => r.startsWith('token='))?.split('=')[1]
    return token ? ({ Authorization: `Bearer ${token}` } as HeadersInit) : ({} as HeadersInit)
  }

  const loadStatus = async () => {
    try {
      setError(null)
  const res = await fetch(`${API_BASE}/api/v1x/connect/status`, { headers: authHeader() })
      if (!res.ok) throw new Error((await res.json()).detail || 'Failed to load status')
      const data = await res.json()
      setStatus(data)
    } catch (e: any) {
      setError(e?.message || 'Failed to load')
    }
  }

  useEffect(() => {
    if (!loading && me) loadStatus()
  }, [loading, me])

  const ensureAccount = async () => {
    try {
      setBusy(true)
      setError(null)
      const res = await fetch(`${API_BASE}/api/v1x/connect/create-account`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(authHeader() as any) }
      })
      if (!res.ok) throw new Error((await res.json()).detail || 'Failed to create account')
      await loadStatus()
    } catch (e: any) {
      setError(e?.message || 'Error creating account')
    } finally {
      setBusy(false)
    }
  }

  const startOnboarding = async () => {
    try {
      setBusy(true)
      setError(null)
  const res = await fetch(`${API_BASE}/api/v1x/connect/onboarding-link`, { headers: authHeader() })
      if (!res.ok) throw new Error((await res.json()).detail || 'Failed to get onboarding link')
      const data = await res.json()
      window.location.href = data.url
    } catch (e: any) {
      setError(e?.message || 'Error starting onboarding')
    } finally {
      setBusy(false)
    }
  }

  const openDashboard = async () => {
    try {
      setBusy(true)
      setError(null)
  const res = await fetch(`${API_BASE}/api/v1x/connect/login-link`, { headers: authHeader() })
      if (!res.ok) throw new Error((await res.json()).detail || 'Failed to get login link')
      const data = await res.json()
      window.location.href = data.url
    } catch (e: any) {
      setError(e?.message || 'Error opening dashboard')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Layout>
      <Head><title>Mentor Settings – Payouts</title></Head>
      <section className="mx-auto max-w-4xl px-6 pt-36 pb-20">
        <h1 className="text-3xl font-bold mb-6">Mentor Settings</h1>
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-2">Stripe Connect Payouts</h2>
          <p className="text-sm text-gray-600 mb-4">Set up your payouts to receive earnings.</p>

          {error && <div className="text-red-600 text-sm mb-3">{error}</div>}

          {!status ? (
            <div className="text-sm text-gray-600">Loading status…</div>
          ) : (
            <div className="space-y-3 mb-6">
              <div>
                <span className="font-medium">Account:</span>{' '}
                {status.account_id ? <code className="text-xs">{status.account_id}</code> : 'Not created'}
              </div>
              <div>
                <span className="font-medium">Details submitted:</span>{' '}
                {status.details_submitted ? 'Yes' : 'No'}
              </div>
              <div>
                <span className="font-medium">Payouts enabled:</span>{' '}
                {status.payouts_enabled ? 'Yes' : 'No'}
              </div>
              {status.requirements_due && (
                <div className="text-sm text-yellow-700">Outstanding requirements: {status.requirements_due}</div>
              )}
            </div>
          )}

          <div className="flex gap-3">
            <Button onClick={ensureAccount} disabled={busy} variant="secondary">Create/Ensure Account</Button>
            <Button onClick={startOnboarding} disabled={busy || !status?.account_id} variant="primary">Start Onboarding</Button>
            <Button onClick={openDashboard} disabled={busy || !status?.account_id} variant="ghost">Open Stripe Dashboard</Button>
          </div>
        </Card>
      </section>
    </Layout>
  )
}
