import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth'
import { Button } from '@/components/Button'
import { Input } from '@/components/Input'

type PlatformSettings = {
  platform_name: string
  support_email: string
  allow_new_registrations: boolean
  mentor_approval_required: boolean
  maintenance_mode: boolean
  featured_courses: string[]
}

export default function AdminSettings({ me }: AdminSSRProps) {
  const router = useRouter()
  const [settings, setSettings] = useState<PlatformSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    loadSettings()
  }, [])

  async function loadSettings() {
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/settings`, {
        credentials: 'include'
      })

      if (res.status === 403) {
        setError('Access denied. Admin privileges required.')
        return
      }

      if (res.status === 401) {
        router.push('/login?redirect=/admin/settings')
        return
      }

      if (!res.ok) {
        throw new Error('Failed to load settings')
      }

      const data = await res.json()
      setSettings(data)
    } catch (err: any) {
      console.error(err)
      setError(err?.message || 'Failed to load settings')
    } finally {
      setLoading(false)
    }
  }

  async function handleSave() {
    if (!settings) return

    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(settings)
      })

      if (res.status === 403) {
        setError('Only superadmins can update settings.')
        return
      }

      if (!res.ok) {
        throw new Error('Failed to save settings')
      }

      setSuccess('Settings saved successfully!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err: any) {
      console.error(err)
      setError(err?.message || 'Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  function updateSetting<K extends keyof PlatformSettings>(
    key: K,
    value: PlatformSettings[K]
  ) {
    if (!settings) return
    setSettings({ ...settings, [key]: value })
  }

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-techGray">Loading settings...</div>
        </div>
      </Layout>
    )
  }

  if (error && !settings) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="rounded-xl border border-red-500/30 p-8 bg-red-500/10">
            <p className="text-red-300">{error}</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <Head><title>Admin Settings – SkillForge Global</title></Head>
      <section className="mx-auto max-w-5xl px-6 pt-36 pb-20">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Platform Settings</h1>
            <p className="text-techGray">
              Configure global platform settings · Signed in as {me.email} ({me.role})
            </p>
            {me.role !== 'SUPERADMIN' && (
              <p className="text-yellow-400 text-sm mt-2">
                ⚠️ Only superadmins can save changes
              </p>
            )}
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 rounded-lg border border-red-500/30 p-4 bg-red-500/10 text-red-300">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-6 rounded-lg border border-green-500/30 p-4 bg-green-500/10 text-green-300">
            ✅ {success}
          </div>
        )}

        {settings && (
          <div className="space-y-6">
            {/* General Settings */}
            <div className="rounded-xl border border-white/10 p-6 bg-white/[0.04]">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span>⚙️</span>
                General Settings
              </h2>
              <div className="space-y-4">
                <Input
                  label="Platform Name"
                  type="text"
                  value={settings.platform_name}
                  onChange={(e) => updateSetting('platform_name', e.target.value)}
                  placeholder="SkillForge Global"
                  className="bg-white/5 border-white/10"
                />
                <Input
                  label="Support Email"
                  type="email"
                  value={settings.support_email}
                  onChange={(e) => updateSetting('support_email', e.target.value)}
                  placeholder="support@skillforge.com"
                  className="bg-white/5 border-white/10"
                />
              </div>
            </div>

            {/* Feature Toggles */}
            <div className="rounded-xl border border-white/10 p-6 bg-white/[0.04]">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span>🎛️</span>
                Feature Controls
              </h2>
              <div className="space-y-4">
                <label className="flex items-center justify-between p-4 rounded-lg border border-white/10 bg-white/[0.02] hover:bg-white/[0.04] cursor-pointer transition">
                  <div>
                    <div className="font-medium">New User Registrations</div>
                    <div className="text-sm text-techGray mt-1">
                      Allow new users to sign up for accounts
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.allow_new_registrations}
                    onChange={(e) => updateSetting('allow_new_registrations', e.target.checked)}
                    className="w-5 h-5 rounded border-white/20 bg-white/5 text-forgePurple focus:ring-forgePurple focus:ring-offset-0"
                  />
                </label>

                <label className="flex items-center justify-between p-4 rounded-lg border border-white/10 bg-white/[0.02] hover:bg-white/[0.04] cursor-pointer transition">
                  <div>
                    <div className="font-medium">Mentor Approval Required</div>
                    <div className="text-sm text-techGray mt-1">
                      Require admin approval before mentors can accept sessions
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.mentor_approval_required}
                    onChange={(e) => updateSetting('mentor_approval_required', e.target.checked)}
                    className="w-5 h-5 rounded border-white/20 bg-white/5 text-forgePurple focus:ring-forgePurple focus:ring-offset-0"
                  />
                </label>

                <label className="flex items-center justify-between p-4 rounded-lg border border-yellow-500/30 bg-yellow-500/5 hover:bg-yellow-500/10 cursor-pointer transition">
                  <div>
                    <div className="font-medium text-yellow-400">🚧 Maintenance Mode</div>
                    <div className="text-sm text-techGray mt-1">
                      Show maintenance page to all non-admin users
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.maintenance_mode}
                    onChange={(e) => updateSetting('maintenance_mode', e.target.checked)}
                    className="w-5 h-5 rounded border-yellow-500/30 bg-yellow-500/10 text-yellow-500 focus:ring-yellow-500 focus:ring-offset-0"
                  />
                </label>
              </div>
            </div>

            {/* Featured Courses */}
            <div className="rounded-xl border border-white/10 p-6 bg-white/[0.04]">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span>⭐</span>
                Featured Courses
              </h2>
              <div className="space-y-3">
                {settings.featured_courses.length === 0 ? (
                  <div className="text-sm text-techGray p-4 rounded-lg border border-white/10 bg-white/[0.02] text-center">
                    No featured courses. Add course slugs below.
                  </div>
                ) : (
                  settings.featured_courses.map((slug, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-3 p-3 rounded-lg border border-white/10 bg-white/[0.02]"
                    >
                      <span className="text-techGray">#{index + 1}</span>
                      <input
                        type="text"
                        value={slug}
                        onChange={(e) => {
                          const newCourses = [...settings.featured_courses]
                          newCourses[index] = e.target.value
                          updateSetting('featured_courses', newCourses)
                        }}
                        className="flex-1 bg-white/5 border border-white/10 rounded px-3 py-2 text-sm"
                        placeholder="course-slug"
                      />
                      <button
                        onClick={() => {
                          const newCourses = settings.featured_courses.filter((_, i) => i !== index)
                          updateSetting('featured_courses', newCourses)
                        }}
                        className="px-3 py-2 rounded bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition text-sm"
                      >
                        Remove
                      </button>
                    </div>
                  ))
                )}
                <button
                  onClick={() => {
                    updateSetting('featured_courses', [...settings.featured_courses, ''])
                  }}
                  className="w-full px-4 py-2 rounded-lg border border-white/10 bg-white/[0.02] hover:bg-white/[0.04] text-sm text-techGray transition"
                >
                  + Add Featured Course
                </button>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex items-center justify-between pt-4 border-t border-white/10">
              <button
                onClick={loadSettings}
                className="px-6 py-3 rounded-lg border border-white/10 hover:bg-white/5 transition"
              >
                Reset Changes
              </button>
              <Button
                onClick={handleSave}
                loading={saving}
                disabled={saving || me.role !== 'SUPERADMIN'}
                variant="primary"
                className="bg-gradient-to-r from-forgePurple to-neuralBlue"
              >
                {saving ? 'Saving...' : 'Save Settings'}
              </Button>
            </div>

            {/* Info Footer */}
            <div className="rounded-lg border border-green-500/30 p-4 bg-green-500/5">
              <div className="text-sm text-green-300">
                <strong>✅ Database Persistence:</strong> All settings are now stored in the database and will persist across server restarts.
                Changes are logged in the audit trail for security.
              </div>
            </div>
          </div>
        )}
      </section>
    </Layout>
  )
}

export const getServerSideProps = requireAdminSSR
