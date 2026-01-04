// src/components/ProfileCard.tsx
import { useState, useEffect } from 'react'
import { User, Mail, Phone, MapPin, Edit, AlertCircle } from 'lucide-react'
import Link from 'next/link'

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

export default function ProfileCard() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

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
      } else {
        setError('Failed to load profile')
      }
    } catch (err) {
      setError('Error loading profile')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading profile...</div>
  }

  if (!profile) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
        <AlertCircle className="w-5 h-5" />
        {error}
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header with Edit Button */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 className="text-2xl font-bold">Profile</h2>
        <Link href="/profile/edit">
          <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
            <Edit className="w-4 h-4" />
            Edit Profile
          </button>
        </Link>
      </div>

      <div className="p-6">
        {/* Avatar & Name Section */}
        <div className="flex items-start gap-6 mb-8 pb-8 border-b border-gray-200">
          {profile.avatar_url ? (
            <img
              src={profile.avatar_url}
              alt={profile.name}
              className="w-24 h-24 rounded-full object-cover border-4 border-blue-100"
            />
          ) : (
            <div className="w-24 h-24 rounded-full bg-blue-100 flex items-center justify-center">
              <User className="w-12 h-12 text-blue-600" />
            </div>
          )}
          <div className="flex-1">
            <h3 className="text-3xl font-bold text-gray-900">
              {profile.name || 'User'}
            </h3>
            <div className="mt-4 space-y-2">
              <div className="flex items-center gap-2 text-gray-600">
                <Mail className="w-5 h-5" />
                <span>{profile.email}</span>
              </div>
              {profile.phone && (
                <div className="flex items-center gap-2 text-gray-600">
                  <Phone className="w-5 h-5" />
                  <span>{profile.phone}</span>
                </div>
              )}
              {profile.location && (
                <div className="flex items-center gap-2 text-gray-600">
                  <MapPin className="w-5 h-5" />
                  <span>{profile.location}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Bio Section */}
        {profile.bio && (
          <div className="mb-8 pb-8 border-b border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
              About
            </h4>
            <p className="text-gray-700 leading-relaxed">{profile.bio}</p>
          </div>
        )}

        {/* Skills Section */}
        {profile.skills && profile.skills.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
              Skills
            </h4>
            <div className="flex flex-wrap gap-2">
              {profile.skills.map((skill) => (
                <span
                  key={skill}
                  className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
