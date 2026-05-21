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
  skills?: string[]
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
        const data = await res.json()
        console.log('Profile data:', data)
        setProfile(data)
      } else {
        setError('Failed to load profile')
      }
    } catch (err) {
      console.error('Error loading profile:', err)
      setError('Error loading profile')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10 backdrop-blur-sm p-8 text-center">
        <div className="text-white/60">Loading profile...</div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="bg-gradient-to-br from-red-500/10 to-red-600/5 rounded-xl border border-red-500/20 backdrop-blur-sm p-6 flex items-center gap-3">
        <AlertCircle className="w-5 h-5 text-red-400" />
        <div className="text-red-300">{error || 'Failed to load profile'}</div>
      </div>
    )
  }

  return (
    <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10 backdrop-blur-sm overflow-hidden">
      {/* Header with Edit Button */}
      <div className="flex items-center justify-between p-6 border-b border-white/10">
        <h2 className="text-2xl font-bold text-white">Profile</h2>
        <Link href="/profile/edit">
          <button className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-4 py-2 rounded-lg transition-all font-medium shadow-lg shadow-blue-500/20">
            <Edit className="w-4 h-4" />
            Edit
          </button>
        </Link>
      </div>

      <div className="p-8">
        {/* Avatar & Name Section */}
        <div className="flex items-start gap-6 mb-8 pb-8 border-b border-white/10">
          {profile.avatar_url ? (
            <img
              src={profile.avatar_url}
              alt={profile.name}
              className="w-24 h-24 rounded-full object-cover border-2 border-blue-500/50 shadow-lg shadow-blue-500/20"
            />
          ) : (
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center border border-white/10">
              <User className="w-12 h-12 text-white/60" />
            </div>
          )}
          <div className="flex-1">
            <h3 className="text-3xl font-bold text-white mb-1">
              {profile.name || 'User'}
            </h3>
            <p className="text-white/60 text-sm font-medium">{profile.email}</p>
            <div className="mt-4 space-y-2">
              {profile.phone && (
                <div className="flex items-center gap-2 text-white/70">
                  <Phone className="w-5 h-5 text-blue-400" />
                  <span>{profile.phone}</span>
                </div>
              )}
              {profile.location && (
                <div className="flex items-center gap-2 text-white/70">
                  <MapPin className="w-5 h-5 text-blue-400" />
                  <span>{profile.location}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Bio Section */}
        {profile.bio && (
          <div className="mb-8 pb-8 border-b border-white/10">
            <h4 className="text-xs font-bold text-white/70 mb-3 uppercase tracking-wider">
              About
            </h4>
            <p className="text-white/80 leading-relaxed">{profile.bio}</p>
          </div>
        )}

        {/* Skills Section */}
        {profile.skills && profile.skills.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-white/70 mb-4 uppercase tracking-wider">
              Skills
            </h4>
            <div className="flex flex-wrap gap-2">
              {profile.skills.map((skill) => (
                <span
                  key={skill}
                  className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-300 px-3 py-1 rounded-full text-sm font-medium border border-blue-500/30 hover:border-blue-500/50 transition-all"
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
