import React, { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { apiCall } from '@/lib/api';

interface Badge {
  id: number;
  name: string;
  description: string;
  icon_url: string;
  icon_emoji?: string;
  category: string;
  rarity: string;
  points_value: number;
}

interface UserBadge {
  id: number;
  badge: Badge;
  first_earned_at: string;
  last_earned_at: string;
  tier: number;
  earn_count: number;
}

interface BadgeProgress {
  id: number;
  badge_id: number;
  current_value: number;
  target_value: number;
  progress_percentage: number;
  is_completed: boolean;
}

interface UserStats {
  total_badges: number;
  total_achievements: number;
  total_points: number;
  earned_badges: UserBadge[];
  in_progress: BadgeProgress[];
  achievements: any[];
}

const AchievementsPage: React.FC = () => {
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'earned' | 'progress'>('earned');

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await apiCall('GET', '/badges/user/stats');
      setStats(response);
    } catch (error) {
      console.error('Failed to load achievements:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRarityColor = (rarity: string) => {
    const colors: { [key: string]: string } = {
      common: 'text-gray-400',
      uncommon: 'text-green-400',
      rare: 'text-blue-400',
      epic: 'text-purple-400',
      legendary: 'text-yellow-400',
    };
    return colors[rarity] || 'text-gray-400';
  };

  const getRarityBg = (rarity: string) => {
    const bgs: { [key: string]: string } = {
      common: 'bg-gray-800 border-gray-600',
      uncommon: 'bg-green-900 border-green-600',
      rare: 'bg-blue-900 border-blue-600',
      epic: 'bg-purple-900 border-purple-600',
      legendary: 'bg-yellow-900 border-yellow-600',
    };
    return bgs[rarity] || 'bg-gray-800 border-gray-600';
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
              <span className="text-3xl">🏆</span>
              Achievements & Badges
            </h1>
            <p className="text-gray-400">
              Unlock badges and achievements by completing challenges, contests, and more
            </p>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin">
                <div className="w-8 h-8 border-4 border-gray-600 border-t-yellow-500 rounded-full"></div>
              </div>
              <p className="text-gray-400 mt-4">Loading achievements...</p>
            </div>
          ) : !stats ? (
            <div className="text-center py-12">
              <p className="text-gray-400">Failed to load achievements</p>
            </div>
          ) : (
            <>
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="text-3xl font-bold text-yellow-400">
                    {stats.total_badges}
                  </div>
                  <div className="text-gray-400 text-sm mt-2">Badges Earned</div>
                </div>
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="text-3xl font-bold text-blue-400">
                    {stats.total_achievements}
                  </div>
                  <div className="text-gray-400 text-sm mt-2">Achievements</div>
                </div>
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="text-3xl font-bold text-green-400">
                    {stats.total_points}
                  </div>
                  <div className="text-gray-400 text-sm mt-2">Total Points</div>
                </div>
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="text-3xl font-bold text-purple-400">
                    {stats.in_progress.length}
                  </div>
                  <div className="text-gray-400 text-sm mt-2">In Progress</div>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex gap-4 mb-6 border-b border-gray-700">
                <button
                  onClick={() => setActiveTab('earned')}
                  className={`px-6 py-3 font-semibold transition ${
                    activeTab === 'earned'
                      ? 'border-b-2 border-yellow-400 text-yellow-400'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Earned Badges ({stats.total_badges})
                </button>
                <button
                  onClick={() => setActiveTab('progress')}
                  className={`px-6 py-3 font-semibold transition ${
                    activeTab === 'progress'
                      ? 'border-b-2 border-blue-400 text-blue-400'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  In Progress ({stats.in_progress.length})
                </button>
              </div>

              {/* Earned Badges */}
              {activeTab === 'earned' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {stats.earned_badges.length === 0 ? (
                    <div className="col-span-full text-center py-12">
                      <p className="text-gray-400">
                        No badges earned yet. Start solving challenges!
                      </p>
                    </div>
                  ) : (
                    stats.earned_badges.map((userBadge) => (
                      <div
                        key={userBadge.id}
                        className={`rounded-lg p-6 border-2 ${getRarityBg(userBadge.badge.rarity)}`}
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="text-5xl">{userBadge.badge.icon_emoji || '🏅'}</div>
                          <span className={`text-xs font-bold uppercase ${getRarityColor(userBadge.badge.rarity)}`}>
                            {userBadge.badge.rarity}
                          </span>
                        </div>
                        <h3 className="text-lg font-bold text-white mb-2">
                          {userBadge.badge.name}
                        </h3>
                        <p className="text-sm text-gray-300 mb-4">
                          {userBadge.badge.description}
                        </p>
                        <div className="flex justify-between items-center text-xs text-gray-400">
                          <span>+{userBadge.badge.points_value} points</span>
                          {userBadge.earn_count > 1 && (
                            <span className="bg-yellow-900 text-yellow-200 px-2 py-1 rounded">
                              ×{userBadge.earn_count}
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500 mt-3">
                          Earned {new Date(userBadge.first_earned_at).toLocaleDateString()}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* In Progress Badges */}
              {activeTab === 'progress' && (
                <div className="space-y-4">
                  {stats.in_progress.length === 0 ? (
                    <div className="text-center py-12">
                      <p className="text-gray-400">All badges earned! Keep going to unlock more.</p>
                    </div>
                  ) : (
                    stats.in_progress.map((progress) => (
                      <div key={progress.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="text-lg font-bold text-white">
                            Badge #{progress.badge_id}
                          </h3>
                          <span className="text-sm text-blue-400 font-semibold">
                            {progress.current_value} / {progress.target_value}
                          </span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-3">
                          <div
                            className="bg-blue-500 h-3 rounded-full transition-all"
                            style={{ width: `${progress.progress_percentage}%` }}
                          ></div>
                        </div>
                        <div className="text-xs text-gray-400 mt-2">
                          {Math.round(progress.progress_percentage)}% Complete
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default AchievementsPage;
