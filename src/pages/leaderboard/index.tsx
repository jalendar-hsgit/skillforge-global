import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import type { GetServerSideProps } from 'next';
import Layout from '@/components/Layout';
import { PageHeader, PageContainer, PageSection, PageGrid, LoadingState, EmptyState } from '@/components/PageLayout';
import { StatCard } from '@/components/Cards';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import { requireAuthSSR } from '@/lib/auth';

interface LeaderboardUser {
  id: number;
  name: string;
  username: string;
  avatar_url?: string;
  coin_balance: number;
  achievement_count: number;
  total_points: number;
  level: number;
  streak_days: number;
  rank: number;
}

interface LeaderboardResponse {
  top_by_coins: LeaderboardUser[];
  top_by_achievements: LeaderboardUser[];
  top_by_points: LeaderboardUser[];
  user_rank: {
    coin_rank: number;
    achievement_rank: number;
    points_rank: number;
    total_users: number;
  };
}

type PeriodType = 'week' | 'month' | 'all-time';
type LeaderboardType = 'coins' | 'achievements' | 'points';

export const getServerSideProps: GetServerSideProps = requireAuthSSR();

export default function LeaderboardPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [data, setData] = useState<LeaderboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [period, setPeriod] = useState<PeriodType>('month');
  const [leaderboardType, setLeaderboardType] = useState<LeaderboardType>('points');

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

  const displayList = 
    leaderboardType === 'coins' ? (data?.top_by_coins || []) :
    leaderboardType === 'achievements' ? (data?.top_by_achievements || []) :
    (data?.top_by_points || []);

  const userRankValue = 
    leaderboardType === 'coins' ? data?.user_rank?.coin_rank :
    leaderboardType === 'achievements' ? data?.user_rank?.achievement_rank :
    data?.user_rank?.points_rank;

  const getMedalEmoji = (rank: number) => {
    switch (rank) {
      case 1: return '🥇';
      case 2: return '🥈';
      case 3: return '🥉';
      default: return '';
    }
  };

  const getRankBadge = (rank: number) => {
    if (rank <= 3) {
      const colors = ['from-yellow-500 to-amber-500', 'from-gray-300 to-gray-400', 'from-orange-400 to-orange-600'];
      return (
        <div className={`flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br ${colors[rank - 1]} shadow-lg`}>
          <span className="text-xl font-bold text-white">{rank}</span>
        </div>
      );
    }
    return (
      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-white/10 border border-white/20">
        <span className="text-lg font-semibold text-white/70">{rank}</span>
      </div>
    );
  };

  const tabs = [
    { id: 'points', label: 'Total Points', icon: '⭐' },
    { id: 'coins', label: 'Coins', icon: '💰' },
    { id: 'achievements', label: 'Achievements', icon: '🏆' },
  ];

  const periods = [
    { id: 'week', label: 'This Week' },
    { id: 'month', label: 'This Month' },
    { id: 'all-time', label: 'All Time' },
  ];

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
          <LoadingState message="Loading leaderboard..." />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <Head>
        <title>Leaderboard - SkillForge</title>
        <meta name="description" content="View the SkillForge global leaderboard" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <PageHeader
            title="Leaderboard"
            subtitle="See who's leading the SkillForge community"
            icon="🏆"
          />

          {/* User Rank Card */}
          {userRankValue && user && (
            <PageContainer variant="glass" className="mb-8">
              <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex items-center gap-6">
                  <div className="relative">
                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-forgePurple to-neuralBlue flex items-center justify-center text-3xl font-bold">
                      {user.full_name?.[0] || 'U'}
                    </div>
                    <div className="absolute -bottom-2 -right-2 w-8 h-8 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-sm font-bold shadow-lg">
                      #{userRankValue}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white mb-1">Your Ranking</h3>
                    <p className="text-white/60">
                      You're in the top {Math.round((userRankValue / (data?.user_rank?.total_users || 1)) * 100)}% of users
                    </p>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white">{data?.user_rank?.points_rank || '-'}</div>
                    <div className="text-sm text-white/60">Points Rank</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white">{data?.user_rank?.coin_rank || '-'}</div>
                    <div className="text-sm text-white/60">Coins Rank</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white">{data?.user_rank?.achievement_rank || '-'}</div>
                    <div className="text-sm text-white/60">Achievements Rank</div>
                  </div>
                </div>
              </div>
            </PageContainer>
          )}

          {error && (
            <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-6 py-4 rounded-xl mb-6">
              {error}
            </div>
          )}

          {/* Top 3 Spotlight */}
          {displayList.length >= 3 && (
            <div className="mb-12">
              <h2 className="text-2xl font-bold text-white mb-6 text-center">🌟 Top Champions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Second Place */}
                <div className="order-2 md:order-1 md:mt-8">
                  <TopPlayerCard player={displayList[1]} rank={2} type={leaderboardType} />
                </div>
                {/* First Place */}
                <div className="order-1 md:order-2">
                  <TopPlayerCard player={displayList[0]} rank={1} type={leaderboardType} isChampion />
                </div>
                {/* Third Place */}
                <div className="order-3 md:mt-12">
                  <TopPlayerCard player={displayList[2]} rank={3} type={leaderboardType} />
                </div>
              </div>
            </div>
          )}

          {/* Controls */}
          <PageContainer variant="card" className="mb-8">
            <div className="flex flex-col md:flex-row gap-6">
              {/* Leaderboard Type Tabs */}
              <div className="flex-1">
                <label className="block text-sm font-semibold text-white/80 mb-3">
                  Category
                </label>
                <div className="flex gap-2">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setLeaderboardType(tab.id as LeaderboardType)}
                      className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-semibold transition-all ${
                        leaderboardType === tab.id
                          ? 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white shadow-lg shadow-purple-500/30'
                          : 'bg-white/10 text-white/70 hover:bg-white/20 border border-white/10'
                      }`}
                    >
                      <span>{tab.icon}</span>
                      <span className="hidden sm:inline">{tab.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Time Period */}
              <div className="md:w-48">
                <label className="block text-sm font-semibold text-white/80 mb-3">
                  Time Period
                </label>
                <select
                  value={period}
                  onChange={(e) => setPeriod(e.target.value as PeriodType)}
                  className="w-full px-4 py-3 rounded-xl border border-white/20 bg-white/10 text-white focus:ring-2 focus:ring-forgePurple focus:border-transparent"
                >
                  {periods.map((p) => (
                    <option key={p.id} value={p.id} className="bg-gray-800">
                      {p.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </PageContainer>

          {/* Leaderboard Table */}
          <PageContainer variant="card">
            {displayList.length === 0 ? (
              <EmptyState
                icon="📊"
                title="No data available"
                description="No leaderboard data for this period yet. Start earning points!"
              />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="px-4 py-4 text-left text-sm font-semibold text-white/60 w-16">
                        Rank
                      </th>
                      <th className="px-4 py-4 text-left text-sm font-semibold text-white/60">
                        Player
                      </th>
                      <th className="px-4 py-4 text-center text-sm font-semibold text-white/60 hidden sm:table-cell">
                        Level
                      </th>
                      <th className="px-4 py-4 text-center text-sm font-semibold text-white/60 hidden md:table-cell">
                        🔥 Streak
                      </th>
                      <th className="px-4 py-4 text-right text-sm font-semibold text-white/60">
                        {leaderboardType === 'coins' ? '💰 Coins' : 
                         leaderboardType === 'achievements' ? '🏆 Achievements' : '⭐ Points'}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {displayList.slice(3).map((player, index) => {
                      const rank = index + 4;
                      const isCurrentUser = user?.id === player.id;

                      return (
                        <tr
                          key={player.id}
                          className={`transition-colors ${
                            isCurrentUser
                              ? 'bg-gradient-to-r from-forgePurple/20 to-neuralBlue/20'
                              : 'hover:bg-white/5'
                          }`}
                        >
                          <td className="px-4 py-4">
                            {getRankBadge(rank)}
                          </td>
                          <td className="px-4 py-4">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center font-semibold">
                                {player.avatar_url ? (
                                  <img src={player.avatar_url} alt={player.name} className="w-full h-full rounded-full object-cover" />
                                ) : (
                                  player.name?.[0] || 'U'
                                )}
                              </div>
                              <div>
                                <p className="font-semibold text-white flex items-center gap-2">
                                  {player.name || player.username}
                                  {isCurrentUser && (
                                    <span className="text-xs bg-gradient-to-r from-forgePurple to-neuralBlue text-white px-2 py-0.5 rounded-full">
                                      You
                                    </span>
                                  )}
                                </p>
                                <p className="text-xs text-white/50">@{player.username}</p>
                              </div>
                            </div>
                          </td>
                          <td className="px-4 py-4 text-center hidden sm:table-cell">
                            <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-white/10 text-sm font-semibold">
                              Lv. {player.level || 1}
                            </span>
                          </td>
                          <td className="px-4 py-4 text-center hidden md:table-cell">
                            <span className="text-orange-400 font-semibold">
                              {player.streak_days || 0} days
                            </span>
                          </td>
                          <td className="px-4 py-4 text-right">
                            <p className="text-xl font-bold text-white">
                              {leaderboardType === 'coins'
                                ? player.coin_balance?.toLocaleString()
                                : leaderboardType === 'achievements'
                                ? player.achievement_count
                                : player.total_points?.toLocaleString()}
                            </p>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </PageContainer>
        </div>
      </div>
    </Layout>
  );
}

// Top Player Card Component
function TopPlayerCard({ 
  player, 
  rank, 
  type, 
  isChampion = false 
}: { 
  player: LeaderboardUser; 
  rank: number; 
  type: LeaderboardType;
  isChampion?: boolean;
}) {
  const getMedalEmoji = (rank: number) => {
    switch (rank) {
      case 1: return '🥇';
      case 2: return '🥈';
      case 3: return '🥉';
      default: return '';
    }
  };

  const borderColors = [
    'border-yellow-400 shadow-yellow-400/30',
    'border-gray-400 shadow-gray-400/20',
    'border-orange-400 shadow-orange-400/20'
  ];

  const getValue = () => {
    if (type === 'coins') return player.coin_balance?.toLocaleString();
    if (type === 'achievements') return player.achievement_count;
    return player.total_points?.toLocaleString();
  };

  const getLabel = () => {
    if (type === 'coins') return 'Coins';
    if (type === 'achievements') return 'Achievements';
    return 'Points';
  };

  return (
    <div className={`
      relative bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl 
      rounded-2xl p-6 text-center border-2 ${borderColors[rank - 1]}
      ${isChampion ? 'shadow-2xl scale-105' : 'shadow-lg'}
      transition-all hover:scale-105 duration-300
    `}>
      {/* Medal */}
      <div className={`text-5xl mb-4 ${isChampion ? 'animate-bounce' : ''}`}>
        {getMedalEmoji(rank)}
      </div>

      {/* Avatar */}
      <div className={`mx-auto mb-4 ${isChampion ? 'w-24 h-24' : 'w-20 h-20'} rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-2xl font-bold border-4 border-white/20`}>
        {player.avatar_url ? (
          <img src={player.avatar_url} alt={player.name} className="w-full h-full rounded-full object-cover" />
        ) : (
          player.name?.[0] || 'U'
        )}
      </div>

      {/* Name */}
      <h3 className={`font-bold text-white mb-1 ${isChampion ? 'text-xl' : 'text-lg'}`}>
        {player.name || player.username}
      </h3>
      <p className="text-white/50 text-sm mb-4">@{player.username}</p>

      {/* Stats */}
      <div className="bg-white/10 rounded-xl p-4">
        <div className="text-3xl font-bold text-white mb-1">
          {getValue()}
        </div>
        <div className="text-sm text-white/60">{getLabel()}</div>
      </div>

      {/* Level Badge */}
      <div className="absolute top-4 right-4 px-3 py-1 bg-white/10 rounded-full text-sm font-semibold">
        Lv. {player.level || 1}
      </div>
    </div>
  );
}
