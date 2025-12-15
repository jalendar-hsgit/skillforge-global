import Head from 'next/head'
import Link from 'next/link'
import { useRouter } from 'next/router'
import Layout from '@/components/Layout'
import { Card } from '@/components/Card'
import { Input } from '@/components/Input'
import { Button } from '@/components/Button'
import { useState } from 'react'

export default function SignupPage() {
  const router = useRouter()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    // Validation
    if (!name.trim()) return setError('Please enter your name')
    if (!/^\S+@\S+\.\S+$/.test(email)) return setError('Please enter a valid email')
    if (password.length < 8) return setError('Password must be at least 8 characters')
    if (password !== confirmPassword) return setError('Passwords do not match')

    setLoading(true)

    try {
      const response = await fetch('/api/session/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: name })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Signup failed')
      }
      
      // Redirect to login page after successful signup
      router.push('/login?signup=success')
    } catch (err: any) {
      setError(err?.message || 'Email already in use')
    } finally {
      setLoading(false)
    }
  }

  function startOAuth(provider: 'google' | 'github') {
    const clientId = (provider === 'google')
      ? (process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || 'demo_google_client_id')
      : (process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID || 'demo_github_client_id');
    const redirect = `${window.location.origin}/oauth-callback?provider=${provider}`;
    const state = Math.random().toString(36).slice(2);
    sessionStorage.setItem('oauth_state', state);

    if (provider === 'google') {
      const scope = encodeURIComponent('openid email profile');
      const url = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&response_type=code&scope=${scope}&redirect_uri=${encodeURIComponent(redirect)}` + `&state=${state}`;
      window.location.href = url;
    } else {
      const scope = encodeURIComponent('read:user user:email');
      const url = `https://github.com/login/oauth/authorize?client_id=${clientId}&scope=${scope}&redirect_uri=${encodeURIComponent(redirect)}` + `&state=${state}`;
      window.location.href = url;
    }
  }

  return (
    <Layout maxWidth="md" showFooter={false}>
      <Head><title>Sign Up – SkillForge Global</title></Head>
      
      <div className="min-h-screen flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-forgePurple to-neuralBlue bg-clip-text text-transparent mb-2">
              Start Your Journey
            </h1>
            <p className="text-gray-400">
              Create your account and unlock your potential
            </p>
            <div className="mt-3 text-xs text-gray-500">
              New accounts start as regular users. Contact admin for role upgrades.
            </div>
          </div>

          {/* Signup Card */}
          <Card className="p-8 backdrop-blur-lg bg-white/5 border border-white/10">
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-lg mb-6 flex items-start gap-3">
                <span className="text-xl">⚠️</span>
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <Input
                type="text"
                label="Full Name"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                autoComplete="name"
                className="bg-white/5 border-white/10 text-white placeholder-gray-500"
              />

              <Input
                type="email"
                label="Email Address"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                className="bg-white/5 border-white/10 text-white placeholder-gray-500"
              />

              <Input
                type="password"
                label="Password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="new-password"
                className="bg-white/5 border-white/10 text-white placeholder-gray-500"
              />

              <Input
                type="password"
                label="Confirm Password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                autoComplete="new-password"
                className="bg-white/5 border-white/10 text-white placeholder-gray-500"
              />

              <div className="text-xs text-gray-400">
                By signing up, you agree to our{' '}
                <Link href="/terms" className="text-forgePurple hover:text-neuralBlue">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link href="/privacy" className="text-forgePurple hover:text-neuralBlue">
                  Privacy Policy
                </Link>
              </div>

              <Button
                type="submit"
                loading={loading}
                disabled={loading}
                variant="primary"
                className="w-full bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90 transition-opacity"
              >
                {loading ? 'Creating account...' : 'Create Account'}
              </Button>
            </form>

            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-[#0B0A13] text-gray-400">Or sign up with</span>
              </div>
            </div>

            {/* Social Signup */}
            <div className="grid grid-cols-2 gap-4">
              <button 
                type="button"
                onClick={() => startOAuth('google')}
                className="flex items-center justify-center gap-2 px-4 py-2 border border-white/10 rounded-lg hover:bg-white/5 transition-colors"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
                </svg>
                <span className="text-sm">Google</span>
              </button>
              <button 
                type="button"
                onClick={() => startOAuth('github')}
                className="flex items-center justify-center gap-2 px-4 py-2 border border-white/10 rounded-lg hover:bg-white/5 transition-colors"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
                </svg>
                <span className="text-sm">GitHub</span>
              </button>
            </div>
          </Card>

          {/* Login Link */}
          <p className="text-center mt-6 text-gray-400">
            Already have an account?{' '}
            <Link href="/login" className="text-forgePurple hover:text-neuralBlue font-semibold transition-colors">
              Log in
            </Link>
          </p>

          {/* Trust Indicators */}
          <div className="mt-8 text-center">
            <p className="text-xs text-gray-500 mb-3">Trusted by learners worldwide</p>
            <div className="flex items-center justify-center gap-6 text-gray-600">
              <div className="flex items-center gap-1">
                <span className="text-lg">🔒</span>
                <span className="text-xs">Secure</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="text-lg">⚡</span>
                <span className="text-xs">Fast Setup</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="text-lg">🎓</span>
                <span className="text-xs">50k+ Students</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
