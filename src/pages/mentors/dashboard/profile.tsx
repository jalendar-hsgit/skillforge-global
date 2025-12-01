import Head from 'next/head'
import Layout from '@/components/Layout'
import AdminHeader from '@/components/AdminHeader'
import { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/router'

export default function MentorProfile() {
  const router = useRouter()
  const [bio, setBio] = useState('')
  const [expertiseInput, setExpertiseInput] = useState('')
  const [hourlyRate, setHourlyRate] = useState<number | ''>('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const apiBase = useMemo(() => process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001', [])

  useEffect(() => {
    // Prefill using overview endpoint if available
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch(`${apiBase}/api/v1x/mentor-portal/dashboard/overview`, { credentials: 'include' })
        if (res.status === 401) {
          router.push('/login?redirect=/mentors/dashboard/profile')
          return
        }
        if (res.status === 403) {
          setError('Your mentor account is not approved yet.')
          return
        }
        if (!res.ok) {
          setError('Failed to load profile details')
          return
        }
        const data = await res.json()
        // Attempt to infer fields if present
        if (data.profile) {
          setBio(data.profile.bio || '')
          setExpertiseInput((data.profile.expertise || []).join(', '))
          setHourlyRate(typeof data.profile.hourly_rate === 'number' ? data.profile.hourly_rate : '')
        } else if (data.mentor) {
          // some payloads may include mentor object
          setBio(data.mentor.bio || '')
          setExpertiseInput((data.mentor.expertise || []).join(', '))
          setHourlyRate(typeof data.mentor.hourly_rate === 'number' ? data.mentor.hourly_rate : '')
        }
      } catch (e: any) {
        setError(e?.message || 'Failed to load')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [apiBase, router])

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    setSuccess(null)
    try {
      const body = {
        bio: bio || '',
        expertise: expertiseInput
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
        hourly_rate: typeof hourlyRate === 'number' ? hourlyRate : Number(hourlyRate) || 0,
      }

      const res = await fetch(`${apiBase}/api/v1x/mentor-portal/profile`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(body),
      })

      if (res.status === 401) {
        router.push('/login?redirect=/mentors/dashboard/profile')
        return
      }

      if (!res.ok) {
        const t = await res.text()
        throw new Error(t || 'Failed to save profile')
      }

      setSuccess('Profile updated successfully')
    } catch (e: any) {
      setError(e?.message || 'Failed to save profile')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Layout>
      <Head>
        <title>Edit Profile – Mentor Dashboard</title>
      </Head>

      <AdminHeader title="Edit Mentor Profile" backUrl="/mentors/dashboard" />

      <div className="container mx-auto px-4 py-8 max-w-3xl">
        {loading ? (
          <div className="text-center py-12 text-techGray">Loading profile...</div>
        ) : (
          <form onSubmit={onSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-500/15 border border-red-500/30 text-red-300 rounded-lg p-3 text-sm">{error}</div>
            )}
            {success && (
              <div className="bg-green-500/15 border border-green-500/30 text-green-300 rounded-lg p-3 text-sm">{success}</div>
            )}

            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <label className="block text-sm font-medium text-techGray mb-2">Bio</label>
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                rows={6}
                placeholder="Tell students about your experience, specialties, and what to expect from sessions."
                className="w-full rounded-lg bg-black/30 border border-white/10 text-white p-3 focus:outline-none focus:ring-2 focus:ring-techBlue"
              />
            </div>

            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <label className="block text-sm font-medium text-techGray mb-2">Expertise (comma separated)</label>
              <input
                type="text"
                value={expertiseInput}
                onChange={(e) => setExpertiseInput(e.target.value)}
                placeholder="React, Node.js, System Design"
                className="w-full rounded-lg bg-black/30 border border-white/10 text-white p-3 focus:outline-none focus:ring-2 focus:ring-techBlue"
              />
              <p className="text-xs text-techGray mt-2">Example: JavaScript, React, System Design</p>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <label className="block text-sm font-medium text-techGray mb-2">Hourly Rate (USD)</label>
              <input
                type="number"
                min={0}
                step={1}
                value={hourlyRate}
                onChange={(e) => setHourlyRate(e.target.value === '' ? '' : Number(e.target.value))}
                placeholder="60"
                className="w-full rounded-lg bg-black/30 border border-white/10 text-white p-3 focus:outline-none focus:ring-2 focus:ring-techBlue"
              />
            </div>

            <div className="flex items-center gap-3">
              <button
                type="submit"
                disabled={saving}
                className={`px-5 py-2 rounded-lg font-medium transition-colors ${saving ? 'bg-techBlue/50 text-white/70' : 'bg-techBlue hover:bg-techBlue/80 text-white'}`}
              >
                {saving ? 'Saving…' : 'Save Profile'}
              </button>
              <button
                type="button"
                onClick={() => router.push('/mentors/dashboard')}
                className="px-5 py-2 rounded-lg font-medium bg-white/10 hover:bg-white/20 text-white"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </Layout>
  )
}
