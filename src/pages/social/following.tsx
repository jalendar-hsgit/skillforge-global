import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { PageHeader, PageContainer, LoadingState, EmptyState } from '@/components/PageLayout';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';

interface UserProfile {
  id: number;
  username: string;
  name: string;
  avatar_url?: string;
  bio?: string;
  level?: number;
  xp?: number;
  followers_count: number;
  following_count: number;
  is_following: boolean;
  followed_at?: string;
}

type TabType = 'followers' | 'following' | 'suggested';

export default function SocialFollowingPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('following');
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [suggestedUsers, setSuggestedUsers] = useState<UserProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [followingInProgress, setFollowingInProgress] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [stats, setStats] = useState({ followers: 0, following: 0 });

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    fetchData();
  }, [isAuthenticated, activeTab]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };

      if (activeTab === 'followers') {
        const response = await fetch(`${apiBase}/api/v1x/users/${user?.id}/followers`, { headers });
        if (response.ok) {
          const data = await response.json();
          setUsers(data.followers || []);
          setStats(prev => ({ ...prev, followers: data.total || 0 }));
        }
      } else if (activeTab === 'following') {
        const response = await fetch(`${apiBase}/api/v1x/users/${user?.id}/following`, { headers });
        if (response.ok) {
          const data = await response.json();
          setUsers(data.following || []);
          setStats(prev => ({ ...prev, following: data.total || 0 }));
        }
      } else {
        // Fetch suggested users
        const response = await fetch(`${apiBase}/api/v1x/users/suggested?limit=20`, { headers });
        if (response.ok) {
          const data = await response.json();
          setSuggestedUsers(data.users || []);
        }
      }
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async (userId: number) => {
    try {
      setFollowingInProgress(userId);
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiBase}/api/v1x/users/${userId}/follow`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        // Update local state
        if (activeTab === 'suggested') {
          setSuggestedUsers(suggestedUsers.map(u => 
            u.id === userId ? { ...u, is_following: true } : u
          ));
        } else {
          setUsers(users.map(u => 
            u.id === userId ? { ...u, is_following: true } : u
          ));
        }
        setStats(prev => ({ ...prev, following: prev.following + 1 }));
      }
    } catch (err) {
      console.error('Follow error:', err);
    } finally {
      setFollowingInProgress(null);
    }
  };

  const handleUnfollow = async (userId: number) => {
    try {
      setFollowingInProgress(userId);
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiBase}/api/v1x/users/${userId}/follow`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        if (activeTab === 'following') {
          setUsers(users.filter(u => u.id !== userId));
          setStats(prev => ({ ...prev, following: prev.following - 1 }));
        } else {
          setUsers(users.map(u => 
            u.id === userId ? { ...u, is_following: false } : u
          ));
        }
      }
    } catch (err) {
      console.error('Unfollow error:', err);
    } finally {
      setFollowingInProgress(null);
    }
  };

  const filteredUsers = searchQuery
    ? users.filter(u => 
        u.username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        u.name?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : users;

  const tabs = [
    { id: 'following', label: 'Following', count: stats.following, icon: '👥' },
    { id: 'followers', label: 'Followers', count: stats.followers, icon: '🤝' },
    { id: 'suggested', label: 'Discover', count: null, icon: '🔍' },
  ];

  return (
    <Layout>
      <Head>
        <title>Following - SkillForge</title>
        <meta name="description" content="Manage your connections on SkillForge" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          {/* Header */}
          <PageHeader
            title="My Connections"
            subtitle="Connect with fellow learners and grow your network"
            icon="🤝"
          />

          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8 mb-8">
            <PageContainer variant="glass" className="text-center">
              <div className="text-3xl font-bold text-white">{stats.following}</div>
              <div className="text-sm text-white/60">Following</div>
            </PageContainer>
            <PageContainer variant="glass" className="text-center">
              <div className="text-3xl font-bold text-white">{stats.followers}</div>
              <div className="text-sm text-white/60">Followers</div>
            </PageContainer>
            <PageContainer variant="glass" className="text-center">
              <div className="text-3xl font-bold text-green-400">+12</div>
              <div className="text-sm text-white/60">This Week</div>
            </PageContainer>
            <PageContainer variant="glass" className="text-center">
              <div className="text-3xl font-bold text-blue-400">1</div>
              <div className="text-sm text-white/60">Your Level</div>
            </PageContainer>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as TabType)}
                className={`flex items-center gap-2 px-5 py-3 rounded-xl font-semibold transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white shadow-lg shadow-purple-500/25'
                    : 'bg-white/10 text-white/70 hover:bg-white/20 border border-white/10'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
                {tab.count !== null && (
                  <span className={`px-2 py-0.5 rounded-full text-sm ${
                    activeTab === tab.id ? 'bg-white/20' : 'bg-white/10'
                  }`}>
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Search */}
          {activeTab !== 'suggested' && (
            <div className="mb-6">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="🔍 Search users..."
                className="w-full px-4 py-3 bg-white/10 text-white rounded-xl border border-white/20 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none placeholder-white/40"
              />
            </div>
          )}

          {error && (
            <div className="bg-red-500/20 border border-red-500/30 text-red-200 px-6 py-4 rounded-xl mb-6">
              {error}
            </div>
          )}

          {/* Content */}
          {loading ? (
            <LoadingState message="Loading connections..." />
          ) : (
            <>
              {activeTab === 'suggested' ? (
                <SuggestedUsersSection 
                  users={suggestedUsers}
                  onFollow={handleFollow}
                  followingInProgress={followingInProgress}
                />
              ) : filteredUsers.length === 0 ? (
                <EmptyState
                  icon={activeTab === 'followers' ? '🤝' : '👥'}
                  title={activeTab === 'followers' ? 'No followers yet' : 'Not following anyone'}
                  description={activeTab === 'followers' 
                    ? 'Share your achievements and engage with the community to gain followers!'
                    : 'Discover interesting people and follow them to see their activity.'
                  }
                  action={
                    <button
                      onClick={() => setActiveTab('suggested')}
                      className="px-6 py-3 bg-gradient-to-r from-forgePurple to-neuralBlue text-white rounded-xl font-semibold hover:opacity-90 transition"
                    >
                      Discover People
                    </button>
                  }
                />
              ) : (
                <div className="space-y-4">
                  {filteredUsers.map((userProfile) => (
                    <UserCard
                      key={userProfile.id}
                      user={userProfile}
                      onFollow={() => handleFollow(userProfile.id)}
                      onUnfollow={() => handleUnfollow(userProfile.id)}
                      isFollowingInProgress={followingInProgress === userProfile.id}
                      showFollowButton={activeTab !== 'following' || !userProfile.is_following}
                    />
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}

// User Card Component
interface UserCardProps {
  user: UserProfile;
  onFollow: () => void;
  onUnfollow: () => void;
  isFollowingInProgress: boolean;
  showFollowButton?: boolean;
}

const UserCard: React.FC<UserCardProps> = ({ 
  user, 
  onFollow, 
  onUnfollow, 
  isFollowingInProgress,
  showFollowButton = true 
}) => {
  return (
    <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-xl p-5 border border-white/10 transition-all hover:border-purple-500/30 hover:shadow-lg group">
      <div className="flex items-center gap-4">
        {/* Avatar */}
        <Link href={`/profile/${user.username}`} className="relative flex-shrink-0">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-xl font-bold shadow-lg overflow-hidden group-hover:scale-105 transition-transform">
              {user.avatar_url ? (
                <img src={user.avatar_url} alt={user.name} className="w-full h-full object-cover" />
              ) : (
                user.name?.[0]?.toUpperCase() || 'U'
              )}
            </div>
            {user.level && user.level >= 10 && (
              <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-xs font-bold shadow-lg">
                {user.level}
              </div>
            )}
        </Link>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <Link href={`/profile/${user.username}`} className="block">
              <h3 className="font-bold text-white group-hover:text-purple-400 transition-colors truncate">
                {user.name || user.username}
              </h3>
              <p className="text-sm text-white/50">@{user.username}</p>
          </Link>
          {user.bio && (
            <p className="text-sm text-white/70 mt-1 line-clamp-1">{user.bio}</p>
          )}
          <div className="flex gap-4 mt-2 text-xs text-white/50">
            <span>{user.followers_count || 0} followers</span>
            <span>{user.following_count || 0} following</span>
          </div>
        </div>

        {/* Follow Button */}
        {showFollowButton && (
          <button
            onClick={user.is_following ? onUnfollow : onFollow}
            disabled={isFollowingInProgress}
            className={`px-5 py-2.5 rounded-xl font-semibold transition-all flex items-center gap-2 ${
              user.is_following
                ? 'bg-white/10 text-white/70 hover:bg-red-500/20 hover:text-red-400 border border-white/10'
                : 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white hover:opacity-90 shadow-lg shadow-purple-500/25'
            } disabled:opacity-50`}
          >
            {isFollowingInProgress ? (
              <div className="w-4 h-4 border-2 border-current/30 border-t-current rounded-full animate-spin" />
            ) : user.is_following ? (
              <>
                <span>✓</span>
                <span>Following</span>
              </>
            ) : (
              <>
                <span>+</span>
                <span>Follow</span>
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
};

// Suggested Users Section
interface SuggestedUsersSectionProps {
  users: UserProfile[];
  onFollow: (userId: number) => void;
  followingInProgress: number | null;
}

const SuggestedUsersSection: React.FC<SuggestedUsersSectionProps> = ({ 
  users, 
  onFollow, 
  followingInProgress 
}) => {
  if (users.length === 0) {
    return (
      <EmptyState
        icon="🔍"
        title="No suggestions available"
        description="We'll suggest more people as our community grows!"
      />
    );
  }

  return (
    <div>
      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span>🌟</span> People You Might Know
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {users.map((userProfile) => (
          <div
            key={userProfile.id}
            className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-xl p-5 border border-white/10 transition-all hover:border-purple-500/30 hover:shadow-lg"
          >
            <div className="flex items-center gap-4 mb-4">
              <Link href={`/profile/${userProfile.username}`} className="w-16 h-16 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-2xl font-bold shadow-lg overflow-hidden">
                  {userProfile.avatar_url ? (
                    <img src={userProfile.avatar_url} alt={userProfile.name} className="w-full h-full object-cover" />
                  ) : (
                    userProfile.name?.[0]?.toUpperCase() || 'U'
                  )}
              </Link>
              <div className="flex-1 min-w-0">
                <h4 className="font-bold text-white truncate">{userProfile.name || userProfile.username}</h4>
                <p className="text-sm text-white/50">@{userProfile.username}</p>
                {userProfile.level && (
                  <span className="inline-block mt-1 px-2 py-0.5 bg-white/10 rounded-full text-xs text-white/70">
                    Level {userProfile.level}
                  </span>
                )}
              </div>
            </div>
            
            {userProfile.bio && (
              <p className="text-sm text-white/60 mb-4 line-clamp-2">{userProfile.bio}</p>
            )}
            
            <button
              onClick={() => onFollow(userProfile.id)}
              disabled={followingInProgress === userProfile.id || userProfile.is_following}
              className={`w-full py-2.5 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 ${
                userProfile.is_following
                  ? 'bg-green-500/20 text-green-400 cursor-default'
                  : 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white hover:opacity-90 shadow-lg shadow-purple-500/25'
              } disabled:opacity-50`}
            >
              {followingInProgress === userProfile.id ? (
                <div className="w-4 h-4 border-2 border-current/30 border-t-current rounded-full animate-spin" />
              ) : userProfile.is_following ? (
                <>
                  <span>✓</span>
                  <span>Following</span>
                </>
              ) : (
                <>
                  <span>+</span>
                  <span>Follow</span>
                </>
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
