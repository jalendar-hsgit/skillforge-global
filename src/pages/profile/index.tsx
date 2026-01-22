// src/pages/profile/index.tsx
import { useProtectedPage } from '@/lib/useProtectedPage'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import Layout from '@/components/Layout'
import ProfileCard from '@/components/ProfileCard'
import UserStatsCard from '@/components/UserStatsCard'
import BadgeList from '@/components/BadgeList'
import { User, Mail, MapPin, Zap } from 'lucide-react'

export default function ProfilePage() {
  const { user, loading } = useProtectedPage()

  if (loading) {
    return <LoadingSpinner message="Loading your profile..." />
  }

  if (!user) {
    return null // Redirect handled by hook
  }

  return (
    <Layout maxWidth="7xl">
      <div className="py-12">
        {/* Page Header */}
        <div className="mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent mb-2">
            Your Profile
          </h1>
          <p className="text-white/60">View and manage your account information and achievements</p>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content - Profile Card (Left, spans 2 cols on lg) */}
          <div className="lg:col-span-2">
            <ProfileCard />
          </div>

          {/* Sidebar - Quick Stats */}
          <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10 backdrop-blur-sm p-6 h-fit">
            <div className="flex items-center gap-2 mb-6">
              <Zap className="w-5 h-5 text-yellow-400" />
              <h3 className="text-lg font-bold text-white">Quick Stats</h3>
            </div>
            
            <div className="space-y-6">
              <div>
                <p className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-1">Member Since</p>
                <p className="text-lg font-semibold text-white">
                  {new Date().getFullYear() === 2024 ? 'Jan 2024' : 'Recently Joined'}
                </p>
              </div>
              
              <div className="h-px bg-gradient-to-r from-white/10 to-transparent" />
              
              <div>
                <p className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">Account Status</p>
                <span className="inline-flex items-center gap-2 bg-gradient-to-r from-emerald-500/20 to-emerald-600/20 text-emerald-300 px-3 py-1 rounded-full text-sm font-semibold border border-emerald-500/30">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  Active
                </span>
              </div>

              <div className="h-px bg-gradient-to-r from-white/10 to-transparent" />
              
              <div>
                <p className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3">Quick Actions</p>
                <div className="space-y-2">
                  <button className="w-full text-left text-white/70 hover:text-white text-sm font-medium p-2 hover:bg-white/5 rounded-lg transition-colors">
                    → Security Settings
                  </button>
                  <button className="w-full text-left text-white/70 hover:text-white text-sm font-medium p-2 hover:bg-white/5 rounded-lg transition-colors">
                    → Download Data
                  </button>
                  <button className="w-full text-left text-red-400/70 hover:text-red-300 text-sm font-medium p-2 hover:bg-red-500/10 rounded-lg transition-colors">
                    → Delete Account
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Section Below */}
        <div className="mt-16">
          <h2 className="text-3xl font-bold text-white mb-8">Your Statistics</h2>
          <UserStatsCard />
        </div>

        {/* Badges Section */}
        <div className="mt-16">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-white mb-2">Achievements</h2>
            <p className="text-white/60">Badges you've earned through learning and participation</p>
          </div>
          <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10 backdrop-blur-sm p-8">
            <BadgeList
              showEarned={true}
              showLocked={true}
              columns={4}
            />
          </div>
        </div>
      </div>
    </Layout>
  )
}
