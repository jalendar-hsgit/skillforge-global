import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';

interface LeaderboardUser {
  id: number;
  name: string;
  avatar?: string;
  coinBalance: number;
  achievementCount: number;
  totalPoints: number;
  rank?: number;
}

interface LeaderboardResponse {
  topByCoins: LeaderboardUser[];
  topByAchievements: LeaderboardUser[];
  userRank: {
    coinRank: number;
    achievementRank: number;
  };
}

type PeriodType = 'week' | 'month' | 'all-time';
type LeaderboardType = 'coins' | 'achievements';

export default function LeaderboardPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [data, setData] = useState<LeaderboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [period, setPeriod] = useState<PeriodType>('month');
  const [leaderboardType, setLeaderboardType] = useState<LeaderboardType>('coins');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (isAuthenticated && user?.id) {
      fetchLeaderboard();
    }
  }, [isAuthenticated, user?.id, period]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(
        `${apiBase}/api/v1x/leaderboard?period=${period}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (!response.ok) throw new Error('Failed to fetch leaderboard');
      const leaderboardData = await response.json();
      setData(leaderboardData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading leaderboard');
      console.error('Leaderboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const displayList = leaderboardType === 'coins'
    ? (data?.topByCoins || [])
    : (data?.topByAchievements || []);

  const userRankValue = leaderboardType === 'coins'
    ? data?.userRank.coinRank
    : data?.userRank.achievementRank;

  const getMedalEmoji = (rank: number) => {
    switch (rank) {
      case 1: return '🥇';
      case 2: return '🥈';
      case 3: return '🥉';
      default: return '•';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading leaderboard...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Leaderboard - SkillForge</title>
        <meta name="description" content="View the SkillForge global leaderboard" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
              <span className="text-3xl">🏆</span>
              Leaderboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              See who's at the top of the community
            </p>
          </div>

          {/* User's Rank Card */}
          {userRankValue && user && (
            <div className="bg-blue-50 dark:bg-blue-900/30 border-2 border-blue-200 dark:border-blue-800 rounded-lg p-6 mb-8">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-blue-700 dark:text-blue-300 mb-1">
                    Your Rank
                  </p>
                  <p className="text-3xl font-bold text-blue-900 dark:text-blue-100">
                    #{userRankValue}
                  </p>
                </div>
                <div className="text-5xl">
                  {userRankValue <= 3 ? getMedalEmoji(userRankValue) : '📊'}
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-blue-700 dark:text-blue-300 mb-1">
                    {leaderboardType === 'coins' ? 'Your Coins' : 'Your Achievements'}
                  </p>
                  <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                    {leaderboardType === 'coins' ? user.coins || 0 : user.achievements || 0}
                  </p>
                </div>
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
              {/* Leaderboard Type */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Leaderboard Type
                </label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setLeaderboardType('coins')}
                    className={`flex-1 px-3 py-2 rounded-lg font-semibold transition ${
                      leaderboardType === 'coins'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200'
                    }`}
                  >
                    💰 Coins
                  </button>
                  <button
                    onClick={() => setLeaderboardType('achievements')}
                    className={`flex-1 px-3 py-2 rounded-lg font-semibold transition ${
                      leaderboardType === 'achievements'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200'
                    }`}
                  >
                    🏆 Achievements
                  </button>
                </div>
              </div>

              {/* Time Period */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Time Period
                </label>
                <select
                  value={period}
                  onChange={(e) => setPeriod(e.target.value as PeriodType)}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                >
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                  <option value="all-time">All Time</option>
                </select>
              </div>
            </div>
          </div>

          {/* Leaderboard List */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
            {displayList.length === 0 ? (
              <div className="p-12 text-center text-gray-600 dark:text-gray-400">
                <p className="text-lg">No data available for this period</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-100 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 w-12">
                        Rank
                      </th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                        User
                      </th>
                      <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">
                        {leaderboardType === 'coins' ? '💰 Coins' : '🏆 Achievements'}
                      </th>
                      <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Total Points
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {displayList.map((player, index) => {
                      const rank = index + 1;
                      const isCurrentUser = user?.id === player.id;

                      return (
                        <tr
                          key={player.id}
                          className={`transition-colors ${
                            isCurrentUser
                              ? 'bg-blue-50 dark:bg-blue-900/20 font-semibold'
                              : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                          }`}
                        >
                          <td className="px-6 py-4">
                            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700">
                              <span className="text-lg font-bold">
                                {getMedalEmoji(rank)}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              {player.avatar && (
                                <img
                                  src={player.avatar}
                                  alt={player.name}
                                  className="w-8 h-8 rounded-full"
                                />
                              )}
                              <div>
                                <p className="font-semibold text-gray-900 dark:text-white">
                                  {player.name}
                                  {isCurrentUser && (
                                    <span className="ml-2 text-xs bg-blue-500 text-white px-2 py-1 rounded-full">
                                      You
                                    </span>
                                  )}
                                </p>
                                <p className="text-xs text-gray-600 dark:text-gray-400">
                                  #{rank}
                                </p>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
                              {leaderboardType === 'coins'
                                ? player.coinBalance.toLocaleString()
                                : player.achievementCount}
                            </p>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {player.totalPoints.toLocaleString()}
                            </p>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Top 3 Spotlight */}
          {displayList.length >= 3 && (
            <div className="mt-12">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
                🌟 Top 3 Champions
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {displayList.slice(0, 3).map((player, index) => (
                  <div
                    key={player.id}
                    className={`rounded-lg p-6 text-center border-2 transition-transform hover:scale-105 ${
                      index === 0
                        ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-300 dark:border-yellow-700'
                        : index === 1
                        ? 'bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600'
                        : 'bg-orange-50 dark:bg-orange-900/20 border-orange-300 dark:border-orange-700'
                    }`}
                  >
                    <div className="text-6xl mb-3">
                      {getMedalEmoji(index + 1)}
                    </div>
                    <p className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                      {player.name}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      #{index + 1} Player
                    </p>
                    <div className="space-y-2">
                      <div className="bg-white dark:bg-gray-800 rounded px-3 py-2">
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          {leaderboardType === 'coins' ? 'Coins' : 'Achievements'}
                        </p>
                        <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                          {leaderboardType === 'coins'
                            ? player.coinBalance.toLocaleString()
                            : player.achievementCount}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
