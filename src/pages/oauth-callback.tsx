import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import Layout from '@/components/Layout'
import { Card } from '@/components/Card'

export default function OAuthCallback() {
  const router = useRouter()
  const { code, state, provider } = router.query
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function finish() {
      // Only proceed when query populated
      if (!provider || !code) return
      try {
        const expected = sessionStorage.getItem('oauth_state')
        if (state && expected && state !== expected) {
          setError('OAuth state mismatch')
          setLoading(false)
          return
        }

        // Exchange code for app session via server-side proxy
        const resp = await fetch(`/api/session/oauth/${provider}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code, redirect_uri: `${window.location.origin}/oauth-callback?provider=${provider}` }),
          credentials: 'include',
        })

        if (!resp.ok) {
          const d = await resp.json().catch(() => ({}))
          throw new Error(d.detail || 'OAuth exchange failed')
        }

        // If backend set cookie, user is logged in — redirect home
        window.location.replace('/dashboard')
      } catch (e: any) {
        setError(e?.message || 'OAuth failed')
      } finally {
        setLoading(false)
      }
    }
    finish()
  }, [code, state, provider])

  return (
    <Layout maxWidth="md" showFooter={false}>
      <div className="min-h-screen flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <Card className="p-6 text-center">
            {loading && <div>Finishing sign-in…</div>}
            {error && <div className="text-red-400">{error}</div>}
          </Card>
        </div>
      </div>
    </Layout>
  )
}
