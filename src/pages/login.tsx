import { useState } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import Head from 'next/head'
import Layout from '@/components/Layout'
import { Input } from '@/components/Input'
import { Button } from '@/components/Button'
import { Card } from '@/components/Card'
import { fetchWithCsrf } from '@/lib/csrf'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [failedAttempts, setFailedAttempts] = useState(0)
  
  // Check for signup success message
  const showSignupSuccess = router.query.signup === 'success'

  // Security: Validate email format
  function isValidEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)

    // Security: Input validation
    if (!email.trim()) {
      setError('Email is required')
      setLoading(false)
      return
    }

    if (!isValidEmail(email)) {
      setError('Please enter a valid email address')
      setLoading(false)
      return
    }

    if (!password || password.length === 0) {
      setError('Password is required')
      setLoading(false)
      return
    }

    // Security: Rate limiting (client-side check)
    if (failedAttempts >= 5) {
      setError('Too many failed attempts. Please try again in 15 minutes.')
      setLoading(false)
      return
    }

    try {
      console.log('Starting login process...')
      
      // Use fetchWithCsrf for CSRF protection
      // Route through /api/session/login (Next.js proxy) to properly handle HttpOnly cookies
      const response = await fetchWithCsrf('/api/session/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
        credentials: 'include'
      })
      
      console.log('Login response status:', response.status)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error('Login failed:', errorData)
        setFailedAttempts(prev => prev + 1)
        throw new Error(errorData.detail || 'Login failed')
      }
      
      // Wait for login response
      const loginData = await response.json()
      console.log('Login successful:', loginData)
      
      // Small delay to ensure cookie is set
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // Check user role to determine redirect
      console.log('Fetching user info...')
      // Use /api/session/me (Next.js proxy) to properly read HttpOnly cookies
      const meResponse = await fetchWithCsrf('/api/session/me', { credentials: 'include' })
      console.log('Me response status:', meResponse.status)
      
      if (meResponse.ok) {
        const user = await meResponse.json()
        console.log('User data:', user)
        
        // Determine redirect URL
        let redirectUrl = '/dashboard'
        
        // If there's a redirect query param, use it (supports both 'next' and 'redirect')
        const nextUrl = router.query.next || router.query.redirect
        if (nextUrl && typeof nextUrl === 'string') {
          // Decode the URL in case it was encoded
          redirectUrl = decodeURIComponent(nextUrl)
          console.log('Using redirect param:', redirectUrl)
        } 
        // Redirect based on role
        else if (user.role === 'ADMIN' || user.role === 'SUPERADMIN') {
          redirectUrl = '/admin'
          console.log('Admin user, redirecting to:', redirectUrl)
        } else {
          console.log('Regular user, redirecting to:', redirectUrl)
        }
        
        console.log('Redirecting to:', redirectUrl)
        
        // Force a full page reload to ensure clean state
        window.location.replace(redirectUrl)
      } else {
        console.log('Me endpoint failed, redirecting to dashboard')
        // Fallback to dashboard if can't get user info
        window.location.replace('/dashboard')
      }
    } catch (err) {
      console.error('Login error:', err)
      const errorMsg = err instanceof Error ? err.message : 'Invalid email or password'
      setError(errorMsg)
      
      // Security: Increment failed attempts
      const newFailedAttempts = failedAttempts + 1
      setFailedAttempts(newFailedAttempts)
      
      // Security: Log security event (if backend supports it)
      if (newFailedAttempts % 3 === 0) {
        console.warn(`Failed login attempt for ${email} (attempt ${newFailedAttempts})`)
      }
      
      setLoading(false)
    }
    // Don't set loading to false here - let the page redirect
  }

  async function startOAuth(provider: 'google' | 'github') {
    // PKCE helpers
    function base64UrlEncode(buffer: ArrayBuffer) {
      const bytes = new Uint8Array(buffer)
      let str = ''
      for (let i = 0; i < bytes.byteLength; i++) str += String.fromCharCode(bytes[i])
      return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
    }

    async function sha256(plain: string) {
      const encoder = new TextEncoder()
      const data = encoder.encode(plain)
      return await crypto.subtle.digest('SHA-256', data)
    }

    function generateVerifier() {
      const array = new Uint8Array(64)
      crypto.getRandomValues(array)
      return base64UrlEncode(array.buffer)
    }

    const clientId = (provider === 'google')
      ? (process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || 'demo_google_client_id')
      : (process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID || 'demo_github_client_id');
    const redirect = `${window.location.origin}/oauth-callback?provider=${provider}`;

    const state = Math.random().toString(36).slice(2);
    sessionStorage.setItem('oauth_state', state);

    // PKCE: create verifier and challenge
    const verifier = generateVerifier()
    sessionStorage.setItem('pkce_verifier', verifier)
    const hashed = await sha256(verifier)
    const challenge = base64UrlEncode(hashed)

    if (provider === 'google') {
      const scope = encodeURIComponent('openid email profile');
      const url = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&response_type=code&scope=${scope}&redirect_uri=${encodeURIComponent(redirect)}` + `&state=${state}&code_challenge=${challenge}&code_challenge_method=S256`;
      window.location.href = url;
    } else {
      const scope = encodeURIComponent('read:user user:email');
      const url = `https://github.com/login/oauth/authorize?client_id=${clientId}&scope=${scope}&redirect_uri=${encodeURIComponent(redirect)}` + `&state=${state}&code_challenge=${challenge}&code_challenge_method=S256`;
      window.location.href = url;
    }
  }

  return (
    <Layout maxWidth="md" showFooter={false}>
      <Head>
        <title>Login – SkillForge Global</title>
      </Head>
      
      <div className="min-h-screen flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-forgePurple to-neuralBlue bg-clip-text text-transparent mb-2">
              Welcome Back
            </h1>
            <p className="text-gray-400">
              Log in to continue your learning journey
            </p>
          </div>

          {/* Login Card */}
          <Card className="p-8 backdrop-blur-lg bg-white/5 border border-white/10">
            {showSignupSuccess && (
              <div className="bg-green-500/10 border border-green-500/20 text-green-400 p-4 rounded-lg mb-6 flex items-start gap-3">
                <span className="text-xl">✅</span>
                <div>
                  <p className="font-semibold">Account created successfully!</p>
                  <p className="text-sm text-green-300 mt-1">Please log in with your credentials to continue.</p>
                </div>
              </div>
            )}
            
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-lg mb-6 flex items-start gap-3">
                <span className="text-xl">⚠️</span>
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
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
                autoComplete="current-password"
                className="bg-white/5 border-white/10 text-white placeholder-gray-500"
              />

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 text-gray-400 cursor-pointer">
                  <input type="checkbox" className="rounded border-gray-600 bg-white/5" />
                  Remember me
                </label>
                <Link href="/forgot-password" className="text-forgePurple hover:text-neuralBlue transition-colors">
                  Forgot password?
                </Link>
              </div>

              <Button
                type="submit"
                loading={loading}
                disabled={loading}
                variant="primary"
                className="w-full bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90 transition-opacity"
              >
                {loading ? 'Logging in...' : 'Log In'}
              </Button>
            </form>

            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-[#0B0A13] text-gray-400">Or continue with</span>
              </div>
            </div>

            {/* Social Login */}
            <div className="grid grid-cols-2 gap-4">
              <button onClick={() => startOAuth('google')} className="flex items-center justify-center gap-2 px-4 py-2 border border-white/10 rounded-lg hover:bg-white/5 transition-colors">
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
                </svg>
                <span className="text-sm">Google</span>
              </button>
              <button onClick={() => startOAuth('github')} className="flex items-center justify-center gap-2 px-4 py-2 border border-white/10 rounded-lg hover:bg-white/5 transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
                </svg>
                <span className="text-sm">GitHub</span>
              </button>
            </div>
          </Card>

          {/* Sign Up Link */}
          <p className="text-center mt-6 text-gray-400">
            Don't have an account?{' '}
            <Link href="/signup" className="text-forgePurple hover:text-neuralBlue font-semibold transition-colors">
              Sign up for free
            </Link>
          </p>
        </div>
      </div>
    </Layout>
  )
}
