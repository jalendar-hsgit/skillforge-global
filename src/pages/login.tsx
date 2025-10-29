import Head from 'next/head'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Layout from '@/components/Layout'
import { useMe } from '@/lib/useMe'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const { me } = useMe()

  // if already logged in, go to dashboard
  useEffect(() => {
    if (me) router.replace('/dashboard')
  }, [me, router])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      const r = await fetch('/api/session/login', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ email, password }),
        credentials: 'include',
      } as RequestInit)

      if (!r.ok) {
        const text = await r.text()
        throw new Error(text || 'Invalid email or password')
      }

      // do not wait for useMe, just go
      router.replace('/dashboard')
    } catch (err: any) {
      setError(err?.message || 'Login failed')
    }
  }

  return (
    <Layout>
      <Head><title>Login – SkillForge Global</title></Head>
      <main className="mx-auto max-w-md px-6 pt-36 pb-20">
        <h1 className="text-3xl font-semibold">Welcome back</h1>
        <p className="text-gray-500 mt-2">Login to continue learning</p>

        {error && (
          <div className="mt-4 rounded-md bg-red-50 p-3 text-red-700 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={onSubmit} className="mt-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-400 focus:border-indigo-500 focus:ring-indigo-500 text-sm"
              placeholder="you@example.com"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-400 focus:border-indigo-500 focus:ring-indigo-500 text-sm"
              placeholder="••••••••"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full rounded-lg bg-indigo-600 py-2 font-medium text-white hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-400"
          >
            Log in
          </button>
        </form>

        <p className="mt-4 text-sm text-gray-500">
          No account?{' '}
          <Link href="/signup" className="text-indigo-600 hover:underline">
            Sign up
          </Link>
        </p>
      </main>
    </Layout>
  )
}
