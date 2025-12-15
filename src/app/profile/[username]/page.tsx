/**
 * User Profile Page
 * Display public user profile with stats and activity
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';

interface UserProfile {
  id: number;
  username: string;
  bio?: string;
  location?: string;
  company?: string;
  job_title?: string;
  avatar_url?: string;
  cover_image_url?: string;
  website?: string;
  joined_date?: string;
  statistics: {
    challenges_completed: number;
    solutions_shared: number;
    current_streak: number;
    longest_streak: number;
    success_rate: number;
    global_rank?: number;
    total_coins: number;
  };
  badges: string[];
}

interface UserStats {
  user: string;
  challenges: {
    attempted: number;
    completed: number;
    perfect: number;
    success_rate: number;
    by_difficulty: {
      easy: number;
      medium: number;
      hard: number;
    };
  };
  solutions: {
    shared: number;
    helpful_votes: number;
    unhelpful_votes: number;
    avg_rating: number;
  };
  streaks: {
    current: number;
    longest: number;
  };
  languages: {
    most_used?: string;
    breakdown: Record<string, number>;
  };
  time: {
    total_minutes: number;
    avg_per_challenge: number;
  };
  coins: {
    earned: number;
    spent: number;
    balance: number;
  };
  ranking: {
    global_rank?: number;
    percentile?: number;
  };
}

export default function UserProfilePage() {
  const params = useParams();
  const username = params?.username as string;
  
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'stats' | 'activity'>('overview');

  useEffect(() => {
    if (!username) return;
    loadProfile();
  }, [username]);

  const loadProfile = async () => {
    try {
      setLoading(true);
      
      const profileRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/profiles/users/${username}`,
        { credentials: 'include' }
      );
      
      if (!profileRes.ok) {
        throw new Error('Failed to load profile');
      }
      
      const profileData = await profileRes.json();
      setProfile(profileData);

      // Try to load stats if available
      try {
        const statsRes = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/profiles/users/${username}/statistics`,
          { credentials: 'include' }
        );
        
        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }
      } catch (e) {
        console.log('Stats not available');
      }

      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Profile Not Found</h2>
          <p className="text-gray-600">{error || 'User profile could not be loaded'}</p>
        </div>
      </div>
    );
  }

  const coverImage = profile.cover_image_url || 'bg-gradient-to-r from-blue-500 to-purple-600';
  const badgeIcons: Record<string, string> = {
    'first_challenge': '🚀',
    'perfect_coder': '⭐',
    'speed_demon': '⚡',
    'languages_master': '🌍',
    'streak_champion': '🔥',
    'test_master': '✅',
    'community_hero': '🦸',
    'optimization_expert': '⚙️',
    'persistence': '💪',
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Cover Image */}
      <div
        className={`h-48 ${!profile.cover_image_url ? coverImage : ''} bg-cover bg-center`}
        style={profile.cover_image_url ? { backgroundImage: `url(${profile.cover_image_url})` } : {}}
      />

      {/* Profile Section */}
      <div className="max-w-4xl mx-auto px-4 -mt-24 relative z-10">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-6">
            {/* Avatar */}
            <div className="flex-shrink-0">
              <img
                src={profile.avatar_url || `https://ui-avatars.com/api/?name=${profile.username}&size=128`}
                alt={profile.username}
                className="w-32 h-32 rounded-full border-4 border-white shadow-md"
              />
            </div>

            {/* Profile Info */}
            <div className="flex-grow">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{profile.username}</h1>
              
              {profile.job_title && (
                <p className="text-lg text-gray-600 mb-1">{profile.job_title}</p>
              )}
              
              <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
                {profile.location && (
                  <div className="flex items-center gap-1">
                    📍 {profile.location}
                  </div>
                )}
                {profile.company && (
                  <div className="flex items-center gap-1">
                    💼 {profile.company}
                  </div>
                )}
                {profile.website && (
                  <a
                    href={profile.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-blue-600 hover:underline"
                  >
                    🔗 Website
                  </a>
                )}
              </div>

              {profile.bio && (
                <p className="text-gray-700 mb-4">{profile.bio}</p>
              )}

              {/* Quick Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {profile.statistics.challenges_completed}
                  </div>
                  <div className="text-xs text-gray-600">Challenges</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {profile.statistics.current_streak}
                  </div>
                  <div className="text-xs text-gray-600">Streak 🔥</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {profile.statistics.solutions_shared}
                  </div>
                  <div className="text-xs text-gray-600">Solutions</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">
                    {profile.statistics.total_coins}
                  </div>
                  <div className="text-xs text-gray-600">Coins</div>
                </div>
              </div>
            </div>

            {/* Rank Badge */}
            {profile.statistics.global_rank && (
              <div className="flex flex-col items-center justify-center text-center">
                <div className="text-sm text-gray-600">Global Rank</div>
                <div className="text-4xl font-bold text-blue-600">
                  #{profile.statistics.global_rank}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Badges */}
        {profile.badges && profile.badges.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Achievements</h2>
            <div className="flex flex-wrap gap-4">
              {profile.badges.map((badge, i) => (
                <div
                  key={i}
                  className="flex flex-col items-center gap-2 p-3 bg-gray-50 rounded-lg hover:shadow-md transition-shadow"
                  title={badge}
                >
                  <span className="text-3xl">{badgeIcons[badge] || '🏆'}</span>
                  <span className="text-xs text-gray-600 text-center">
                    {badge.replace(/_/g, ' ')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="flex border-b border-gray-200">
            {(['overview', 'stats', 'activity'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-4 px-6 font-medium transition-colors ${
                  activeTab === tab
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'overview' && (
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-4">Overview</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {profile.statistics.success_rate.toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">Success Rate</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {profile.statistics.longest_streak}
                    </div>
                    <div className="text-sm text-gray-600">Longest Streak</div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'stats' && stats && (
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-4">Detailed Statistics</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Challenges */}
                  <div>
                    <h4 className="font-bold text-gray-900 mb-3">Challenges</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Attempted:</span>
                        <span className="font-bold">{stats.challenges.attempted}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Completed:</span>
                        <span className="font-bold text-green-600">{stats.challenges.completed}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Perfect (100%):</span>
                        <span className="font-bold text-blue-600">{stats.challenges.perfect}</span>
                      </div>
                      <div className="mt-3 pt-3 border-t">
                        <div className="font-bold text-gray-900 mb-2">By Difficulty:</div>
                        <div className="flex justify-between text-xs">
                          <span>🟢 Easy: {stats.challenges.by_difficulty.easy}</span>
                          <span>🟡 Medium: {stats.challenges.by_difficulty.medium}</span>
                          <span>🔴 Hard: {stats.challenges.by_difficulty.hard}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Languages */}
                  <div>
                    <h4 className="font-bold text-gray-900 mb-3">Languages</h4>
                    <div className="space-y-2 text-sm">
                      {stats.languages.most_used && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Most Used:</span>
                          <span className="font-bold">{stats.languages.most_used}</span>
                        </div>
                      )}
                      <div className="mt-3 pt-3 border-t">
                        {Object.entries(stats.languages.breakdown || {}).map(([lang, count]) => (
                          <div key={lang} className="flex justify-between text-xs py-1">
                            <span>{lang}</span>
                            <span className="font-bold">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Solutions */}
                  <div>
                    <h4 className="font-bold text-gray-900 mb-3">Solutions</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Shared:</span>
                        <span className="font-bold">{stats.solutions.shared}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Helpful Votes:</span>
                        <span className="font-bold text-green-600">{stats.solutions.helpful_votes}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Avg Rating:</span>
                        <span className="font-bold">{stats.solutions.avg_rating.toFixed(2)}/5</span>
                      </div>
                    </div>
                  </div>

                  {/* Time */}
                  <div>
                    <h4 className="font-bold text-gray-900 mb-3">Time Spent</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total:</span>
                        <span className="font-bold">{stats.time.total_minutes}m</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Per Challenge Avg:</span>
                        <span className="font-bold">{stats.time.avg_per_challenge.toFixed(1)}m</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'activity' && (
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-4">Recent Activity</h3>
                <p className="text-gray-600">Activity feed coming soon</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
