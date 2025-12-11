import Head from 'next/head'
import { useState } from 'react'
import { useRouter } from 'next/router'
import Layout from '@/components/Layout'
import { Card } from '@/components/Card'
import { Input } from '@/components/Input'
import { Button } from '@/components/Button'

export default function ForgotPasswordPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    setLoading(true)
    try {
      const r = await fetch('/api/session/forgot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })
      if (!r.ok) {
        const data = await r.json().catch(() => ({}))
        throw new Error(data.detail || 'Request failed')
      }
      setMessage('If an account with that email exists, you will receive password reset instructions.')
      // Optionally redirect to login after a short delay
      setTimeout(() => router.push('/login'), 2500)
    } catch (err: any) {
      setError(err?.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout maxWidth="md" showFooter={false}>
      <Head>
        <title>Forgot Password – SkillForge Global</title>
      </Head>

      <div className="min-h-screen flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold">Reset Your Password</h1>
            <p className="text-gray-400">Enter the email associated with your account.</p>
          </div>

          <Card className="p-6">
            {message && <div className="mb-4 text-sm text-green-400">{message}</div>}
            {error && <div className="mb-4 text-sm text-red-400">{error}</div>}

            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Email Address"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />

              <Button type="submit" loading={loading} variant="primary" className="w-full">
                {loading ? 'Sending...' : 'Send Reset Instructions'}
              </Button>
            </form>
          </Card>

        </div>
      </div>
    </Layout>
  )
}
