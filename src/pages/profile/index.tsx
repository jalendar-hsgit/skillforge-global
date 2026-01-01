// src/pages/profile/index.tsx
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import ProfileCard from '@/components/ProfileCard'
import UserStatsCard from '@/components/UserStatsCard'

export default function ProfilePage() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
    } else {
      setIsAuthenticated(true)
      setLoading(false)
    }
  }, [router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your profile...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Your Profile</h1>
          <p className="text-gray-600 mt-2">View and manage your account information</p>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content - Profile Card (Left, spans 2 cols on lg) */}
          <div className="lg:col-span-2">
            <ProfileCard />
          </div>

          {/* Sidebar - Quick Stats */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-bold mb-4">Quick Stats</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Member Since</p>
                <p className="text-lg font-semibold text-gray-900">
                  {new Date().getFullYear() === 2024 ? 'Jan 2024' : 'Recently'}
                </p>
              </div>
              <hr />
              <div>
                <p className="text-sm text-gray-600 mb-2">Account Status</p>
                <span className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                  Active
                </span>
              </div>
              <hr />
              <div>
                <p className="text-sm text-gray-600 mb-3">Actions</p>
                <button className="w-full text-left text-blue-600 hover:text-blue-800 text-sm font-medium p-2 hover:bg-blue-50 rounded">
                  → View Security Settings
                </button>
                <button className="w-full text-left text-blue-600 hover:text-blue-800 text-sm font-medium p-2 hover:bg-blue-50 rounded">
                  → Download Your Data
                </button>
                <button className="w-full text-left text-red-600 hover:text-red-800 text-sm font-medium p-2 hover:bg-red-50 rounded">
                  → Delete Account
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Section Below */}
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-6">Your Statistics</h2>
          <UserStatsCard />
        </div>
      </div>
    </div>
  )
}
