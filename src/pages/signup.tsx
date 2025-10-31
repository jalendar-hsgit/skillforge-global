import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState } from 'react'
import { apiPost } from '@/lib/api'

export default function SignupPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [pwd, setPwd] = useState('')
  const [msg, setMsg] = useState<string|null>(null)
  const [err, setErr] = useState<string|null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault(); setErr(null); setMsg(null)
    if (!name.trim()) return setErr('Add your name.')
    if (!/^\S+@\S+\.\S+$/.test(email)) return setErr('Invalid email.')
    if (pwd.length < 8) return setErr('Use 8+ characters.')
    try {
      const response = await fetch('/api/session/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password: pwd })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Signup failed')
      }
      
      setMsg('Account created.')
      setTimeout(()=>{ window.location.href = '/login' }, 600)
    } catch (err: any) {
      const errorMsg = err?.message || 'Email already used.'
      setErr(errorMsg)
    }
  }

  return (
    <Layout>
      <Head><title>Sign Up – SkillForge Global</title></Head>
      <div className="mx-auto max-w-md px-6 py-40">
        <h1 className="text-2xl font-semibold mb-6">Create your account</h1>
        <form className="space-y-3" onSubmit={onSubmit} noValidate>
          <input className="w-full h-12 rounded-md bg-white/5 border border-white/10 px-4" placeholder="Full Name" value={name} onChange={e=>setName(e.target.value)} />
          <input className="w-full h-12 rounded-md bg-white/5 border border-white/10 px-4" placeholder="Email" type="email" value={email} onChange={e=>setEmail(e.target.value)} />
          <input className="w-full h-12 rounded-md bg-white/5 border border-white/10 px-4" placeholder="Password" type="password" value={pwd} onChange={e=>setPwd(e.target.value)} />
          {err && <div className="text-sm text-red-400">{err}</div>}
          {msg && <div className="text-sm text-green-400">{msg}</div>}
          <button className="w-full h-12 rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue">Create account</button>
        </form>
      </div>
    </Layout>
  )
}
