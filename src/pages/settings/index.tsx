// src/pages/settings/index.tsx
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import Layout from '@/components/Layout'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { useProtectedPage } from '@/lib/useProtectedPage'
import { ROUTES } from '@/lib/routes'
import { Bell, Lock, User, Palette, Eye, LogOut, ChevronRight } from 'lucide-react'

interface UserSettings {
  emailNotifications: boolean
  pushNotifications: boolean
  twoFactorEnabled: boolean
  theme: 'light' | 'dark' | 'auto'
  language: string
  timezone: string
  profileVisibility: 'public' | 'private' | 'friends'
  activityStatus: boolean
}

export default function SettingsPage() {
  const router = useRouter()
  const { user, loading: authLoading } = useProtectedPage()
  const [loading, setLoading] = useState(true)
  const [settings, setSettings] = useState<UserSettings>({
    emailNotifications: true,
    pushNotifications: true,
    twoFactorEnabled: false,
    theme: 'auto',
    language: 'en',
    timezone: 'UTC',
    profileVisibility: 'public',
    activityStatus: true,
  })
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle')

  // Security: Redirect if not authenticated
  useEffect(() => {
    if (!authLoading) {
      if (!user) {
        router.push('/login?redirect=' + encodeURIComponent(router.asPath))
      } else {
        setLoading(false)
      }
    }
  }, [user, authLoading, router])

  // Security: Show loading while checking auth
  if (authLoading || loading) {
    return <LoadingSpinner message="Loading settings..." />
  }

  // Security: Don't render if not authenticated
  if (!user) {
    return null
  }

  const handleToggle = (key: keyof UserSettings) => {
    setSettings(prev => ({
      ...prev,
      [key]: typeof prev[key] === 'boolean' ? !prev[key] : prev[key]
    }))
  }

  const handleSelectChange = (key: keyof UserSettings, value: string) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }))
  }

  // Load settings from backend on mount
  useEffect(() => {
    if (user && !authLoading && !loading) {
      fetchSettings()
    }
  }, [user, authLoading, loading])

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/v1x/account/settings', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      })

      if (response.ok) {
        const data = await response.json()
        // Convert snake_case from API to camelCase for frontend
        setSettings({
          emailNotifications: data.email_notifications,
          pushNotifications: data.push_notifications,
          twoFactorEnabled: data.two_factor_enabled,
          theme: data.theme,
          language: data.language,
          timezone: data.timezone,
          profileVisibility: data.profile_visibility,
          activityStatus: data.activity_status,
        })
      }
    } catch (error) {
      console.error('Failed to load settings:', error)
    }
  }

  const handleSave = async () => {
    setSaveStatus('saving')
    try {
      // Convert camelCase to snake_case for API
      const payload = {
        email_notifications: settings.emailNotifications,
        push_notifications: settings.pushNotifications,
        two_factor_enabled: settings.twoFactorEnabled,
        theme: settings.theme,
        language: settings.language,
        timezone: settings.timezone,
        profile_visibility: settings.profileVisibility,
        activity_status: settings.activityStatus,
      }

      const response = await fetch('/api/v1x/account/settings', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
      })

      if (response.ok) {
        setSaveStatus('success')
        setTimeout(() => setSaveStatus('idle'), 2000)
      } else {
        setSaveStatus('error')
        setTimeout(() => setSaveStatus('idle'), 2000)
      }
    } catch (error) {
      console.error('Failed to save settings:', error)
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('idle'), 2000)
    }
  }

  return (
    <Layout maxWidth="2xl">
      <div className="py-12 flex flex-col items-center w-full">
        {/* Page Header */}
        <div className="w-full max-w-2xl mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Settings</h1>
          <p className="text-white/60">Manage your preferences and account security</p>
        </div>

        {/* Settings Container */}
        <div className="w-full max-w-2xl">
          {/* Notifications Section */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 mb-6">
            <div className="flex items-center gap-3 mb-6">
              <Bell className="w-6 h-6 text-blue-400" />
              <h2 className="text-xl font-bold text-white">Notifications</h2>
            </div>

            <div className="space-y-4">
              {/* Email Notifications */}
              <div className="flex items-center justify-between pb-4 border-b border-white/10">
                <div>
                  <p className="font-medium text-white">Email Notifications</p>
                  <p className="text-sm text-white/60">Receive updates about your courses and mentoring</p>
                </div>
                <button
                  onClick={() => handleToggle('emailNotifications')}
                  className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                    settings.emailNotifications
                      ? 'bg-gradient-to-r from-blue-600 to-cyan-600'
                      : 'bg-white/10'
                  }`}
                >
                  <span
                    className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                      settings.emailNotifications ? 'translate-x-7' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              {/* Push Notifications */}
              <div className="flex items-center justify-between pb-4 border-b border-white/10">
                <div>
                  <p className="font-medium text-white">Push Notifications</p>
                  <p className="text-sm text-white/60">Get instant alerts on your device</p>
                </div>
                <button
                  onClick={() => handleToggle('pushNotifications')}
                  className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                    settings.pushNotifications
                      ? 'bg-gradient-to-r from-blue-600 to-cyan-600'
                      : 'bg-white/10'
                  }`}
                >
                  <span
                    className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                      settings.pushNotifications ? 'translate-x-7' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              {/* Activity Status */}
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-white">Activity Status</p>
                  <p className="text-sm text-white/60">Show when you're online</p>
                </div>
                <button
                  onClick={() => handleToggle('activityStatus')}
                  className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                    settings.activityStatus
                      ? 'bg-gradient-to-r from-blue-600 to-cyan-600'
                      : 'bg-white/10'
                  }`}
                >
                  <span
                    className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                      settings.activityStatus ? 'translate-x-7' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>

          {/* Privacy & Security Section */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 mb-6">
            <div className="flex items-center gap-3 mb-6">
              <Lock className="w-6 h-6 text-green-400" />
              <h2 className="text-xl font-bold text-white">Privacy & Security</h2>
            </div>

            <div className="space-y-4">
              {/* Two Factor Authentication */}
              <div className="flex items-center justify-between pb-4 border-b border-white/10">
                <div>
                  <p className="font-medium text-white">Two-Factor Authentication</p>
                  <p className="text-sm text-white/60">Add an extra layer of security</p>
                </div>
                <button
                  onClick={() => handleToggle('twoFactorEnabled')}
                  className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                    settings.twoFactorEnabled
                      ? 'bg-gradient-to-r from-green-600 to-emerald-600'
                      : 'bg-white/10'
                  }`}
                >
                  <span
                    className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                      settings.twoFactorEnabled ? 'translate-x-7' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              {/* Profile Visibility */}
              <div className="pb-4 border-b border-white/10">
                <p className="font-medium text-white mb-3">Profile Visibility</p>
                <select
                  value={settings.profileVisibility}
                  onChange={(e) => handleSelectChange('profileVisibility', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500 transition-colors"
                >
                  <option value="public" className="bg-slate-900">Public - Everyone can see your profile</option>
                  <option value="friends" className="bg-slate-900">Friends Only - Only friends can see</option>
                  <option value="private" className="bg-slate-900">Private - Only you can see</option>
                </select>
              </div>

              {/* Password Change Link */}
              <Link href="/security/change-password">
                <button className="w-full flex items-center justify-between p-4 rounded-lg hover:bg-white/5 transition-colors">
                  <span className="text-white font-medium">Change Password</span>
                  <ChevronRight className="w-5 h-5 text-white/60" />
                </button>
              </Link>
            </div>
          </div>

          {/* Preferences Section */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 mb-6">
            <div className="flex items-center gap-3 mb-6">
              <Palette className="w-6 h-6 text-purple-400" />
              <h2 className="text-xl font-bold text-white">Preferences</h2>
            </div>

            <div className="space-y-4">
              {/* Theme */}
              <div className="pb-4 border-b border-white/10">
                <p className="font-medium text-white mb-3">Theme</p>
                <select
                  value={settings.theme}
                  onChange={(e) => handleSelectChange('theme', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500 transition-colors"
                >
                  <option value="auto" className="bg-slate-900">Auto (Match system)</option>
                  <option value="dark" className="bg-slate-900">Dark</option>
                  <option value="light" className="bg-slate-900">Light</option>
                </select>
              </div>

              {/* Language */}
              <div className="pb-4 border-b border-white/10">
                <p className="font-medium text-white mb-3">Language</p>
                <select
                  value={settings.language}
                  onChange={(e) => handleSelectChange('language', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500 transition-colors"
                >
                  <option value="en" className="bg-slate-900">English</option>
                  <option value="es" className="bg-slate-900">Español</option>
                  <option value="fr" className="bg-slate-900">Français</option>
                  <option value="de" className="bg-slate-900">Deutsch</option>
                </select>
              </div>

              {/* Timezone */}
              <div>
                <p className="font-medium text-white mb-3">Timezone</p>
                <select
                  value={settings.timezone}
                  onChange={(e) => handleSelectChange('timezone', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500 transition-colors"
                >
                  <option value="UTC" className="bg-slate-900">UTC</option>
                  <option value="EST" className="bg-slate-900">Eastern Time</option>
                  <option value="CST" className="bg-slate-900">Central Time</option>
                  <option value="MST" className="bg-slate-900">Mountain Time</option>
                  <option value="PST" className="bg-slate-900">Pacific Time</option>
                </select>
              </div>
            </div>
          </div>

          {/* Account Section */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 mb-6">
            <div className="flex items-center gap-3 mb-6">
              <User className="w-6 h-6 text-orange-400" />
              <h2 className="text-xl font-bold text-white">Account</h2>
            </div>

            <div className="space-y-3">
              {/* Profile Link */}
              <Link href={ROUTES.profile}>
                <button className="w-full flex items-center justify-between p-4 rounded-lg hover:bg-white/5 transition-colors border border-white/10">
                  <span className="text-white font-medium">View Profile</span>
                  <ChevronRight className="w-5 h-5 text-white/60" />
                </button>
              </Link>

              {/* Logout Link */}
              <Link href={ROUTES.logout}>
                <button className="w-full flex items-center justify-between p-4 rounded-lg hover:bg-red-600/10 transition-colors border border-red-500/20">
                  <span className="text-red-400 font-medium">Logout</span>
                  <LogOut className="w-5 h-5 text-red-400" />
                </button>
              </Link>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex gap-4">
            <button
              onClick={handleSave}
              disabled={saveStatus === 'saving'}
              className={`flex-1 py-3 rounded-lg font-medium transition-all ${
                saveStatus === 'success'
                  ? 'bg-green-600/20 text-green-400 border border-green-500/30'
                  : saveStatus === 'error'
                  ? 'bg-red-600/20 text-red-400 border border-red-500/30'
                  : 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white hover:shadow-lg hover:shadow-cyan-500/30'
              }`}
            >
              {saveStatus === 'saving'
                ? 'Saving...'
                : saveStatus === 'success'
                ? '✓ Saved'
                : saveStatus === 'error'
                ? '✗ Error'
                : 'Save Settings'}
            </button>
            <Link href={ROUTES.dashboard}>
              <button className="flex-1 py-3 rounded-lg font-medium bg-white/10 text-white border border-white/20 hover:bg-white/20 transition-colors">
                Cancel
              </button>
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  )
}
