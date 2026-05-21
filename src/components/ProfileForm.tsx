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
    return (
      <div className="max-w-2xl mx-auto bg-gradient-to-br from-white/10 to-white/5 rounded-lg border border-white/10 backdrop-blur-sm p-8 text-center">
        <div className="text-white/60">Loading profile...</div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="max-w-2xl mx-auto bg-gradient-to-br from-red-500/10 to-red-600/5 rounded-lg border border-red-500/20 backdrop-blur-sm p-8 text-center">
        <div className="text-red-300">Failed to load profile</div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto bg-gradient-to-br from-white/10 to-white/5 rounded-lg border border-white/10 backdrop-blur-sm p-8">
      <h2 className="text-2xl font-bold text-white mb-6">Edit Profile</h2>

      <div className="space-y-5">
        {/* Email (Read-only) */}
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">
            Email
          </label>
          <input
            type="email"
            value={profile.email}
            disabled
            className="w-full border border-white/10 rounded-lg px-4 py-2 bg-white/5 text-white/60 backdrop-blur-sm"
          />
        </div>

        {/* Full Name */}
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">
            Full Name
          </label>
          <input
            type="text"
            value={profile.name || ''}
            onChange={(e) => setProfile({ ...profile, name: e.target.value })}
            className="w-full border border-white/10 rounded-lg px-4 py-2 bg-white/5 text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500 focus:border-blue-500/50 backdrop-blur-sm transition-colors"
            placeholder="John Doe"
          />
        </div>

        {/* Bio */}
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">
            Bio
          </label>
          <textarea
            value={profile.bio || ''}
            onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
            className="w-full border border-white/10 rounded-lg px-4 py-2 bg-white/5 text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500 focus:border-blue-500/50 backdrop-blur-sm h-24 transition-colors"
            placeholder="Tell us about yourself..."
          />
          <p className="text-xs text-white/50 mt-1">
            {(profile.bio || '').length}/500 characters
          </p>
        </div>

        {/* Phone */}
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">
            Phone Number
          </label>
          <input
            type="tel"
            value={profile.phone || ''}
            onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
            className="w-full border border-white/10 rounded-lg px-4 py-2 bg-white/5 text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500 focus:border-blue-500/50 backdrop-blur-sm transition-colors"
            placeholder="+1 (555) 123-4567"
          />
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">
            Location
          </label>
          <input
            type="text"
            value={profile.location || ''}
            onChange={(e) => setProfile({ ...profile, location: e.target.value })}
            className="w-full border border-white/10 rounded-lg px-4 py-2 bg-white/5 text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500 focus:border-blue-500/50 backdrop-blur-sm transition-colors"
            placeholder="San Francisco, CA"
          />
        </div>

        {/* Skills */}
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">
            Skills
          </label>
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={skillInput}
              onChange={(e) => setSkillInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addSkill()}
              className="flex-1 border border-white/10 rounded-lg px-4 py-2 bg-white/5 text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500 focus:border-blue-500/50 backdrop-blur-sm transition-colors"
              placeholder="Add a skill and press Enter"
            />
            <button
              onClick={addSkill}
              type="button"
              className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-4 py-2 rounded-lg font-medium transition-all"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {profile.skills.map((skill) => (
              <div
                key={skill}
                className="bg-gradient-to-r from-blue-600/30 to-blue-700/30 text-blue-300 px-3 py-1 rounded-full text-sm flex items-center gap-2 border border-blue-500/30 backdrop-blur-sm"
              >
                {skill}
                <button
                  onClick={() => removeSkill(skill)}
                  type="button"
                  className="text-blue-400 hover:text-blue-200 font-bold transition-colors"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-gradient-to-br from-red-500/10 to-red-600/5 border border-red-500/20 text-red-300 px-4 py-3 rounded-lg flex items-center gap-2 text-sm backdrop-blur-sm">
            <AlertCircle className="w-5 h-5" />
            {error}
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="bg-gradient-to-br from-green-500/10 to-green-600/5 border border-green-500/20 text-green-300 px-4 py-3 rounded-lg flex items-center gap-2 text-sm backdrop-blur-sm">
            <CheckCircle className="w-5 h-5" />
            Profile updated successfully!
          </div>
        )}

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-white/20 disabled:to-white/20 text-white font-medium py-2 px-4 rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20"
        >
          <Save className="w-5 h-5" />
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  )
}
