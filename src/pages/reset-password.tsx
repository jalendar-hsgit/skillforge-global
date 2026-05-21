import Head from 'next/head'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Layout from '@/components/Layout'
import { Card } from '@/components/Card'
import { Input } from '@/components/Input'
import { Button } from '@/components/Button'

export default function ResetPasswordPage() {
  const router = useRouter()
  const { token } = router.query
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (!token) return
    // token present
  }, [token])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    if (password.length < 8) return setError('Password must be at least 8 characters')
    if (password !== confirm) return setError('Passwords do not match')
    if (!token || typeof token !== 'string') return setError('Missing reset token')

    setLoading(true)
    try {
      const r = await fetch('/api/session/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password }),
      })
      if (!r.ok) {
        const data = await r.json().catch(() => ({}))
        throw new Error(data.detail || 'Reset failed')
      }
      setSuccess(true)
      // Redirect to login after a brief pause
      setTimeout(() => router.push('/login'), 1800)
    } catch (err: any) {
      setError(err?.message || 'Reset failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout maxWidth="md" showFooter={false}>
      <Head>
        <title>Reset Password – SkillForge Global</title>
      </Head>
      <div className="min-h-screen flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold">Choose a New Password</h1>
            <p className="text-gray-400">Enter and confirm your new password.</p>
          </div>

          <Card className="p-6">
            {success && <div className="mb-4 text-sm text-green-400">Password updated. Redirecting to login…</div>}
            {error && <div className="mb-4 text-sm text-red-400">{error}</div>}

            <form onSubmit={handleSubmit} className="space-y-4">
              <Input label="New Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
              <Input label="Confirm Password" type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />

              <Button type="submit" loading={loading} variant="primary" className="w-full">
                {loading ? 'Updating...' : 'Update Password'}
              </Button>
            </form>
          </Card>
        </div>
      </div>
    </Layout>
  )
}
