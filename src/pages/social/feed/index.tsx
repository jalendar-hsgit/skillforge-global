import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { PageHeader, PageContainer, LoadingState, EmptyState } from '@/components/PageLayout';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';

interface FeedItem {
  id: number;
  type: 'post' | 'achievement' | 'course-completed' | 'skill-added' | 'level-up';
  author: {
    id: number;
    name: string;
    username?: string;
    avatar?: string;
  };
  content: string;
  timestamp: string;
  likes: number;
  comments: number;
  isLiked: boolean;
  image?: string;
  metadata?: {
    courseTitle?: string;
    skillName?: string;
    achievementName?: string;
    level?: number;
  };
}

export default function SocialFeedPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [postContent, setPostContent] = useState('');
  const [posting, setPosting] = useState(false);
  const [filter, setFilter] = useState<'all' | 'following' | 'achievements'>('all');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    fetchFeed();
  }, [isAuthenticated, filter]);

  const fetchFeed = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiBase}/api/v1x/social/feed?filter=${filter}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to fetch feed');
      const data = await response.json();
      setFeed(data.feed || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading feed');
      console.error('Feed fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePostSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!postContent.trim()) return;

    try {
      setPosting(true);
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiBase}/api/v1x/social/posts`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: postContent })
      });

      if (!response.ok) throw new Error('Failed to create post');
      setPostContent('');
      await fetchFeed();
    } catch (err) {
      console.error('Post creation error:', err);
    } finally {
      setPosting(false);
    }
  };

  const handleLike = async (postId: number) => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      await fetch(`${apiBase}/api/v1x/social/posts/${postId}/like`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setFeed(feed.map(item => 
        item.id === postId 
          ? { ...item, isLiked: !item.isLiked, likes: item.isLiked ? item.likes - 1 : item.likes + 1 }
          : item
      ));
    } catch (err) {
      console.error('Like error:', err);
    }
  };

  const filters = [
    { id: 'all', label: 'All Activity', icon: '📰' },
    { id: 'following', label: 'Following', icon: '👥' },
    { id: 'achievements', label: 'Achievements', icon: '🏆' },
  ];

  return (
    <Layout>
      <Head>
        <title>Social Feed - SkillForge</title>
        <meta name="description" content="Connect with learners and celebrate achievements" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8">
        <div className="max-w-3xl mx-auto px-4">
          {/* Header */}
          <div className="flex justify-between items-start mb-8">
            <PageHeader
              title="Social Feed"
              subtitle="Stay connected with your learning community"
              icon="🌟"
            />
            <Link href="/social/following">
              <a className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl transition border border-white/10 flex items-center gap-2">
                <span>👥</span>
                <span className="hidden sm:inline">Connections</span>
              </a>
            </Link>
          </div>

          {error && (
            <div className="bg-red-500/20 border border-red-500/30 text-red-200 px-6 py-4 rounded-xl mb-6">
              {error}
            </div>
          )}

          {/* Post Creator */}
          <PageContainer variant="glass" className="mb-8">
            <form onSubmit={handlePostSubmit}>
              <div className="flex gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-lg font-bold shadow-lg flex-shrink-0">
                  {user?.avatar ? (
                    <img src={user.avatar} alt={user.name} className="w-full h-full rounded-xl object-cover" />
                  ) : (
                    user?.name?.[0]?.toUpperCase() || 'U'
                  )}
                </div>
                <div className="flex-1">
                  <textarea
                    value={postContent}
                    onChange={(e) => setPostContent(e.target.value)}
                    placeholder="Share your learning journey, achievements, or ask a question..."
                    className="w-full px-4 py-3 bg-white/10 text-white rounded-xl border border-white/20 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none resize-none placeholder-white/40"
                    rows={3}
                  />
                  <div className="flex justify-between items-center mt-3">
                    <div className="flex gap-2">
                      <button type="button" className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition text-lg">
                        📷
                      </button>
                      <button type="button" className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition text-lg">
                        😊
                      </button>
                      <button type="button" className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition text-lg">
                        🏆
                      </button>
                    </div>
                    <button
                      type="submit"
                      disabled={!postContent.trim() || posting}
                      className="px-6 py-2.5 bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90 disabled:opacity-50 text-white font-semibold rounded-xl transition-all shadow-lg shadow-purple-500/25 flex items-center gap-2"
                    >
                      {posting ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Posting...
                        </>
                      ) : (
                        <>
                          <span>📤</span>
                          Post
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </form>
          </PageContainer>

          {/* Filters */}
          <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
            {filters.map((f) => (
              <button
                key={f.id}
                onClick={() => setFilter(f.id as typeof filter)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium transition-all whitespace-nowrap ${
                  filter === f.id
                    ? 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white shadow-lg'
                    : 'bg-white/10 text-white/70 hover:bg-white/20 border border-white/10'
                }`}
              >
                <span>{f.icon}</span>
                <span>{f.label}</span>
              </button>
            ))}
          </div>

          {/* Feed Items */}
          {loading ? (
            <LoadingState message="Loading feed..." />
          ) : feed.length === 0 ? (
            <EmptyState
              icon="📭"
              title="No posts yet"
              description="Be the first to share something with the community!"
              action={
                <Link href="/social/following">
                  <a className="px-6 py-3 bg-gradient-to-r from-forgePurple to-neuralBlue text-white rounded-xl font-semibold hover:opacity-90 transition">
                    Find People to Follow
                  </a>
                </Link>
              }
            />
          ) : (
            <div className="space-y-4">
              {feed.map((item) => (
                <FeedCard 
                  key={item.id} 
                  item={item} 
                  onLike={() => handleLike(item.id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

// Feed Card Component
interface FeedCardProps {
  item: FeedItem;
  onLike: () => void;
}

const FeedCard: React.FC<FeedCardProps> = ({ item, onLike }) => {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
    const days = Math.floor(diff / 86400);
    if (days === 1) return '1d';
    if (days < 7) return `${days}d`;
    return date.toLocaleDateString();
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'achievement': return '🏆';
      case 'course-completed': return '🎓';
      case 'skill-added': return '💡';
      case 'level-up': return '⬆️';
      default: return '📝';
    }
  };

  const getActivityLabel = (type: string, metadata?: FeedItem['metadata']) => {
    switch (type) {
      case 'achievement':
        return `🏆 Earned achievement: ${metadata?.achievementName || 'Achievement'}`;
      case 'course-completed':
        return `🎓 Completed course: ${metadata?.courseTitle || 'Course'}`;
      case 'skill-added':
        return `💡 Learned new skill: ${metadata?.skillName || 'Skill'}`;
      case 'level-up':
        return `⬆️ Reached Level ${metadata?.level || '?'}!`;
      default:
        return null;
    }
  };

  const activityLabel = getActivityLabel(item.type, item.metadata);

  return (
    <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-xl p-5 border border-white/10 transition-all hover:border-white/20">
      {/* Activity Badge */}
      {activityLabel && (
        <div className="mb-4 pb-4 border-b border-white/10">
          <span className="text-sm text-white/60">{activityLabel}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-start gap-4 mb-4">
        <Link href={`/profile/${item.author.username || item.author.id}`}>
          <a className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-lg font-bold shadow-lg flex-shrink-0 overflow-hidden hover:scale-105 transition-transform">
            {item.author.avatar ? (
              <img src={item.author.avatar} alt={item.author.name} className="w-full h-full object-cover" />
            ) : (
              item.author.name?.[0]?.toUpperCase() || 'U'
            )}
          </a>
        </Link>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <Link href={`/profile/${item.author.username || item.author.id}`}>
              <a className="font-bold text-white hover:text-purple-400 transition-colors">
                {item.author.name}
              </a>
            </Link>
            {item.author.username && (
              <span className="text-sm text-white/50">@{item.author.username}</span>
            )}
            <span className="text-sm text-white/40">·</span>
            <span className="text-sm text-white/40">{formatDate(item.timestamp)}</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="mb-4">
        <p className="text-white/90 whitespace-pre-wrap">{item.content}</p>
      </div>

      {/* Image */}
      {item.image && (
        <div className="mb-4 rounded-xl overflow-hidden">
          <img src={item.image} alt="Post" className="w-full h-auto" />
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-4 pt-4 border-t border-white/10">
        <button
          onClick={onLike}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition font-medium ${
            item.isLiked
              ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
              : 'bg-white/10 text-white/70 hover:bg-white/20'
          }`}
        >
          <span>{item.isLiked ? '❤️' : '🤍'}</span>
          <span>{item.likes}</span>
        </button>
        
        <button className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white/70 hover:bg-white/20 rounded-lg transition">
          <span>💬</span>
          <span>{item.comments}</span>
        </button>
        
        <button className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white/70 hover:bg-white/20 rounded-lg transition ml-auto">
          <span>🔗</span>
          <span>Share</span>
        </button>
      </div>
    </div>
  );
};
