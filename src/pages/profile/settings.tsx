// src/pages/profile/settings.tsx
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { ArrowLeft, AlertCircle, CheckCircle, Lock, Bell, Eye } from 'lucide-react'
import { useProtectedPage } from '@/lib/useProtectedPage'

interface AccountSettings {
  bio_visibility: 'public' | 'private' | 'mentors_only'
  receive_notifications: boolean
  email_notifications: boolean
  newsletter: boolean
  two_factor_enabled: boolean
}

export default function SettingsPage() {
  const router = useRouter()
  const { user, loading: authLoading, isAuthorized } = useProtectedPage()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [settings, setSettings] = useState<AccountSettings>({
    bio_visibility: 'public',
    receive_notifications: true,
    email_notifications: true,
    newsletter: false,
    two_factor_enabled: false
  })

  // Security: Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login?redirect=' + encodeURIComponent(router.asPath))
    }
  }, [user, authLoading, router])

  useEffect(() => {
    if (authLoading) return
    
    if (!user) {
      return // Will redirect above
    }
    
    // User is authenticated, load settings
    // Load settings from localStorage as fallback
    const saved = localStorage.getItem('accountSettings')
    if (saved) {
      setSettings(JSON.parse(saved))
    }
    setLoading(false)
  }, [router])

  const handleSave = async () => {
    setSaving(true)
    try {
      // Save to localStorage for now
      localStorage.setItem('accountSettings', JSON.stringify(settings))
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      console.error('Error saving settings:', err)
    } finally {
      setSaving(false)
    }
  }

  // Security: Show loading while checking auth
  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading settings...</p>
        </div>
      </div>
    )
  }

  // Security: Don't render if not authenticated
  if (!user) {
    return null
  }

  const SettingToggle = ({ label, description, icon: Icon, value, onChange }: any) => (
    <div className="flex items-start justify-between p-4 bg-gray-50 rounded-lg">
      <div className="flex items-start gap-3">
        <Icon className="w-5 h-5 text-gray-600 mt-1" />
        <div>
          <p className="font-medium text-gray-900">{label}</p>
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        </div>
      </div>
      <button
        onClick={() => onChange(!value)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          value ? 'bg-blue-600' : 'bg-gray-300'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            value ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  )

  const SelectSetting = ({ label, description, icon: Icon, value, options, onChange }: any) => (
    <div className="flex items-start justify-between p-4 bg-gray-50 rounded-lg">
      <div className="flex items-start gap-3">
        <Icon className="w-5 h-5 text-gray-600 mt-1" />
        <div>
          <p className="font-medium text-gray-900">{label}</p>
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        </div>
      </div>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
      >
        {options.map((opt: any) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Back Button */}
        <Link href="/profile">
          <button className="flex items-center gap-2 text-blue-600 hover:text-blue-800 font-medium mb-6 transition-colors">
            <ArrowLeft className="w-5 h-5" />
            Back to Profile
          </button>
        </Link>

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Account Settings</h1>
          <p className="text-gray-600 mt-2">Manage your privacy, notifications, and security preferences</p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            Settings saved successfully!
          </div>
        )}

        {/* Privacy Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6 overflow-hidden">
          <div className="bg-gray-100 px-6 py-4 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <Eye className="w-5 h-5 text-gray-600" />
              <h2 className="text-lg font-bold text-gray-900">Privacy</h2>
            </div>
          </div>
          <div className="p-6 space-y-4">
            <SelectSetting
              label="Profile Visibility"
              description="Control who can see your profile and information"
              icon={Eye}
              value={settings.bio_visibility}
              options={[
                { value: 'public', label: 'Public - Anyone can see' },
                { value: 'mentors_only', label: 'Mentors Only' },
                { value: 'private', label: 'Private - Only you can see' }
              ]}
              onChange={(value: string) => setSettings({ ...settings, bio_visibility: value as any })}
            />
          </div>
        </div>

        {/* Notifications Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6 overflow-hidden">
          <div className="bg-gray-100 px-6 py-4 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <Bell className="w-5 h-5 text-gray-600" />
              <h2 className="text-lg font-bold text-gray-900">Notifications</h2>
            </div>
          </div>
          <div className="p-6 space-y-4">
            <SettingToggle
              label="In-App Notifications"
              description="Receive notifications within the SkillForge app"
              icon={Bell}
              value={settings.receive_notifications}
              onChange={(value: boolean) => setSettings({ ...settings, receive_notifications: value })}
            />
            <hr />
            <SettingToggle
              label="Email Notifications"
              description="Receive email updates about your sessions and messages"
              icon={Bell}
              value={settings.email_notifications}
              onChange={(value: boolean) => setSettings({ ...settings, email_notifications: value })}
            />
            <hr />
            <SettingToggle
              label="Newsletter"
              description="Subscribe to our weekly newsletter with tips and updates"
              icon={Bell}
              value={settings.newsletter}
              onChange={(value: boolean) => setSettings({ ...settings, newsletter: value })}
            />
          </div>
        </div>

        {/* Security Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6 overflow-hidden">
          <div className="bg-gray-100 px-6 py-4 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <Lock className="w-5 h-5 text-gray-600" />
              <h2 className="text-lg font-bold text-gray-900">Security</h2>
            </div>
          </div>
          <div className="p-6 space-y-4">
            <SettingToggle
              label="Two-Factor Authentication"
              description="Add an extra layer of security to your account"
              icon={Lock}
              value={settings.two_factor_enabled}
              onChange={(value: boolean) => setSettings({ ...settings, two_factor_enabled: value })}
            />
            <hr />
            <div className="p-4 bg-gray-50 rounded-lg">
              <button className="text-blue-600 hover:text-blue-800 font-medium text-sm">
                → Change Password
              </button>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <button className="text-blue-600 hover:text-blue-800 font-medium text-sm">
                → View Active Sessions
              </button>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-lg transition-colors"
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </button>

        {/* Danger Zone */}
        <div className="mt-12 bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="font-bold text-red-900 mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            Danger Zone
          </h3>
          <p className="text-red-800 text-sm mb-4">
            These actions cannot be undone. Please be careful.
          </p>
          <button className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm">
            Delete Account Permanently
          </button>
        </div>
      </div>
    </div>
  )
}
