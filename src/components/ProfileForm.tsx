// src/components/ProfileForm.tsx
import { useState, useEffect } from 'react'
import { Save, AlertCircle, CheckCircle } from 'lucide-react'

interface UserProfile {
  id: number
  email: string
  name?: string
  bio?: string
  avatar_url?: string
  phone?: string
  location?: string
  skills: string[]
}

export default function ProfileForm() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [skillInput, setSkillInput] = useState('')

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch('/api/v1x/account/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        setProfile(await res.json())
      }
    } catch (err) {
      setError('Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!profile) return

    setSaving(true)
    setError('')
    setSuccess(false)

    try {
      const token = localStorage.getItem('token')
      const res = await fetch('/api/v1x/account/profile', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: profile.name,
          bio: profile.bio,
          phone: profile.phone,
          location: profile.location,
          skills: profile.skills
        })
      })

      if (res.ok) {
        const updated = await res.json()
        setProfile(updated)
        setSuccess(true)
        setTimeout(() => setSuccess(false), 3000)
      } else {
        setError('Failed to update profile')
      }
    } catch (err) {
      setError('Error saving profile. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const addSkill = () => {
    if (skillInput.trim() && profile) {
      if (!profile.skills.includes(skillInput.trim())) {
        setProfile({
          ...profile,
          skills: [...profile.skills, skillInput.trim()]
        })
      }
      setSkillInput('')
    }
  }

  const removeSkill = (skill: string) => {
    if (profile) {
      setProfile({
        ...profile,
        skills: profile.skills.filter(s => s !== skill)
      })
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading profile...</div>
  }

  if (!profile) {
    return <div className="text-center py-8 text-red-600">Failed to load profile</div>
  }

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-2xl font-bold mb-6">Edit Profile</h2>

      <div className="space-y-4">
        {/* Email (Read-only) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Email
          </label>
          <input
            type="email"
            value={profile.email}
            disabled
            className="w-full border border-gray-300 rounded-lg px-4 py-2 bg-gray-50 text-gray-600"
          />
        </div>

        {/* Full Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Full Name
          </label>
          <input
            type="text"
            value={profile.name || ''}
            onChange={(e) => setProfile({ ...profile, name: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="John Doe"
          />
        </div>

        {/* Bio */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Bio
          </label>
          <textarea
            value={profile.bio || ''}
            onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent h-24"
            placeholder="Tell us about yourself..."
          />
          <p className="text-xs text-gray-500 mt-1">
            {(profile.bio || '').length}/500 characters
          </p>
        </div>

        {/* Phone */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Phone Number
          </label>
          <input
            type="tel"
            value={profile.phone || ''}
            onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="+1 (555) 123-4567"
          />
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <input
            type="text"
            value={profile.location || ''}
            onChange={(e) => setProfile({ ...profile, location: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="San Francisco, CA"
          />
        </div>

        {/* Skills */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Skills
          </label>
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={skillInput}
              onChange={(e) => setSkillInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addSkill()}
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Add a skill and press Enter"
            />
            <button
              onClick={addSkill}
              type="button"
              className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {profile.skills.map((skill) => (
              <div
                key={skill}
                className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center gap-2"
              >
                {skill}
                <button
                  onClick={() => removeSkill(skill)}
                  type="button"
                  className="text-blue-600 hover:text-blue-800 font-bold"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2 text-sm">
            <AlertCircle className="w-5 h-5" />
            {error}
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center gap-2 text-sm">
            <CheckCircle className="w-5 h-5" />
            Profile updated successfully!
          </div>
        )}

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <Save className="w-5 h-5" />
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  )
}
