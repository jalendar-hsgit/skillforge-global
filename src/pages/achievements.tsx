import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import AchievementCard, { UserAchievement } from '@/components/AchievementCard';

interface AchievementStats {
  totalAchievements: number;
  unlockedCount: number;
  totalPoints: number;
  categories: string[];
}

export default function AchievementsPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [achievements, setAchievements] = useState<UserAchievement[]>([]);
  const [stats, setStats] = useState<AchievementStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'recent' | 'name' | 'category'>('recent');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (isAuthenticated && user?.id) {
      fetchAchievements();
    }
  }, [isAuthenticated, user?.id]);

  const fetchAchievements = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiBase}/api/v1x/achievements`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to fetch achievements');
      const data = await response.json();

      setAchievements(data.achievements || []);
      setStats(data.stats || {
        totalAchievements: data.achievements?.length || 0,
        unlockedCount: data.achievements?.filter((a: UserAchievement) => a.unlockedAt).length || 0,
        totalPoints: data.achievements?.reduce((sum: number, a: UserAchievement) => 
          sum + (a.unlockedAt ? a.achievement.points : 0), 0) || 0,
        categories: [...new Set(data.achievements?.map((a: UserAchievement) => a.achievement.category) || [])]
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading achievements');
      console.error('Achievement fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  let filteredAchievements = achievements;
  if (selectedCategory !== 'all') {
    filteredAchievements = achievements.filter(a => a.achievement.category === selectedCategory);
  }

  if (sortBy === 'name') {
    filteredAchievements.sort((a, b) => a.achievement.name.localeCompare(b.achievement.name));
  } else if (sortBy === 'category') {
    filteredAchievements.sort((a, b) => a.achievement.category.localeCompare(b.achievement.category));
  } else if (sortBy === 'recent') {
    filteredAchievements.sort((a, b) => {
      const aDate = a.unlockedAt ? new Date(a.unlockedAt).getTime() : 0;
      const bDate = b.unlockedAt ? new Date(b.unlockedAt).getTime() : 0;
      return bDate - aDate;
    });
  }

  const unlockedAchievements = filteredAchievements.filter(a => a.unlockedAt);
  const lockedAchievements = filteredAchievements.filter(a => !a.unlockedAt);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading achievements...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Achievements - SkillForge</title>
        <meta name="description" content="View your SkillForge achievements and progress" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              🏆 Achievements
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Track your accomplishments and unlock special badges
            </p>
          </div>

          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">Total Achievements</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {stats.totalAchievements}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">Unlocked</p>
                <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {stats.unlockedCount}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">Progress</p>
                <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {stats.totalAchievements > 0
                    ? Math.round((stats.unlockedCount / stats.totalAchievements) * 100)
                    : 0}%
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">Total Points</p>
                <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">
                  {stats.totalPoints}
                </p>
              </div>
            </div>
          )}

          {/* Progress Bar */}
          {stats && stats.totalAchievements > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-8">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900 dark:text-white">Overall Progress</h3>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {stats.unlockedCount} of {stats.totalAchievements}
                </span>
              </div>
              <div className="w-full h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-300"
                  style={{
                    width: `${stats.totalAchievements > 0
                      ? (stats.unlockedCount / stats.totalAchievements) * 100
                      : 0}%`
                  }}
                />
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Controls */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Category Filter */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Filter by Category
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Categories</option>
                  {stats?.categories.map(cat => (
                    <option key={cat} value={cat}>
                      {cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Sort By */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Sort By
                </label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                >
                  <option value="recent">Recently Unlocked</option>
                  <option value="name">Name (A-Z)</option>
                  <option value="category">Category</option>
                </select>
              </div>
            </div>
          </div>

          {/* Unlocked Achievements */}
          {unlockedAchievements.length > 0 && (
            <div className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <span className="text-3xl">⭐</span>
                Unlocked ({unlockedAchievements.length})
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                {unlockedAchievements.map((achievement) => (
                  <AchievementCard
                    key={achievement.achievement.id}
                    achievement={achievement}
                    size="medium"
                    showProgress={false}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Locked Achievements */}
          {lockedAchievements.length > 0 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <span className="text-3xl">🔒</span>
                Locked ({lockedAchievements.length})
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                {lockedAchievements.map((achievement) => (
                  <AchievementCard
                    key={achievement.achievement.id}
                    achievement={achievement}
                    size="medium"
                    showProgress={true}
                  />
                ))}
              </div>
            </div>
          )}

          {filteredAchievements.length === 0 && (
            <div className="text-center py-12">
              <p className="text-4xl mb-4">🎯</p>
              <p className="text-gray-600 dark:text-gray-400 text-lg">
                No achievements found for this filter
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
