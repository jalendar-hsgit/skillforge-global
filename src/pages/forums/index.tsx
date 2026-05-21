import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Layout from '@/components/Layout';
import { PageHeader, PageContainer, PageSection, LoadingState, EmptyState } from '@/components/PageLayout';
import { apiCall } from '@/lib/api';
import Link from 'next/link';

interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon_emoji?: string;
  thread_count: number;
  reply_count: number;
  last_activity_at?: string;
}

interface Thread {
  id: number;
  title: string;
  creator: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  category_id: number;
  view_count: number;
  reply_count: number;
  vote_count: number;
  status: string;
  thread_type: string;
  created_at: string;
  last_reply_at?: string;
  is_pinned: boolean;
}

interface ThreadListResponse {
  total: number;
  threads: Thread[];
}

const ForumsPage: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [threads, setThreads] = useState<Thread[]>([]);
  const [loading, setLoading] = useState(true);
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const [sortBy, setSortBy] = useState('recent');
  const [searchQuery, setSearchQuery] = useState('');
  const LIMIT = 20;

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    loadThreads();
  }, [selectedCategory, sortBy, skip]);

  const loadCategories = async () => {
    try {
      const response = await apiCall('/api/v1x/forums/categories');
      setCategories(response || []);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const loadThreads = async () => {
    try {
      setLoading(true);
      let url = `/api/v1x/forums/threads?skip=${skip}&limit=${LIMIT}&sort_by=${sortBy}`;
      if (selectedCategory) {
        url += `&category_id=${selectedCategory}`;
      }
      
      const response = await apiCall(url) as ThreadListResponse;
      setThreads(response.threads || []);
      setTotal(response.total || 0);
    } catch (error) {
      console.error('Failed to load threads:', error);
      setThreads([]);
    } finally {
      setLoading(false);
    }
  };

  const getThreadTypeIcon = (type: string) => {
    const icons: { [key: string]: string } = {
      question: '❓',
      discussion: '💬',
      announcement: '📢',
      resource: '📚',
      bug_report: '🐛',
    };
    return icons[type] || '📌';
  };

  const getStatusBadge = (status: string) => {
    const badges: { [key: string]: { bg: string; text: string; label: string } } = {
      open: { bg: 'bg-blue-500/20', text: 'text-blue-400', label: 'Open' },
      answered: { bg: 'bg-green-500/20', text: 'text-green-400', label: '✓ Answered' },
      closed: { bg: 'bg-gray-500/20', text: 'text-gray-400', label: 'Closed' },
      resolved: { bg: 'bg-green-500/20', text: 'text-green-400', label: '✓ Resolved' },
    };
    const badge = badges[status] || badges.open;
    return (
      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${badge.bg} ${badge.text}`}>
        {badge.label}
      </span>
    );
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    const days = Math.floor(diff / 86400);
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days}d ago`;
    if (days < 30) return `${Math.floor(days / 7)}w ago`;
    return date.toLocaleDateString();
  };

  const sortOptions = [
    { value: 'recent', label: '🕒 Most Recent', icon: '🕒' },
    { value: 'popular', label: '🔥 Most Popular', icon: '🔥' },
    { value: 'viewed', label: '👁️ Most Viewed', icon: '👁️' },
    { value: 'unanswered', label: '❓ Unanswered', icon: '❓' },
  ];

  const filteredThreads = searchQuery
    ? threads.filter(t => t.title.toLowerCase().includes(searchQuery.toLowerCase()))
    : threads;

  return (
    <Layout>
      <Head>
        <title>Forums - SkillForge</title>
        <meta name="description" content="Ask questions, share knowledge, and discuss with the SkillForge community" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
            <PageHeader
              title="Community Forums"
              subtitle="Ask questions, share knowledge, and discuss with fellow learners"
              icon="💬"
            />
            <Link href="/forums/create" className="px-6 py-3 bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90 text-white rounded-xl font-semibold transition-all shadow-lg shadow-purple-500/25 flex items-center gap-2">
                <span className="text-lg">✏️</span>
                New Thread
            </Link>
          </div>

          {/* Stats Bar */}
          <PageContainer variant="glass" className="mb-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-white">{total}</div>
                <div className="text-sm text-white/60">Total Threads</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white">{categories.length}</div>
                <div className="text-sm text-white/60">Categories</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-400">
                  {threads.filter(t => t.status === 'answered').length}
                </div>
                <div className="text-sm text-white/60">Answered</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400">
                  {threads.reduce((sum, t) => sum + t.reply_count, 0)}
                </div>
                <div className="text-sm text-white/60">Total Replies</div>
              </div>
            </div>
          </PageContainer>

          {/* Categories */}
          {categories.length > 0 && (
            <div className="mb-8">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <span>📂</span> Categories
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                <button
                  onClick={() => {
                    setSelectedCategory(null);
                    setSkip(0);
                  }}
                  className={`group p-4 rounded-xl text-left transition-all duration-300 ${
                    selectedCategory === null
                      ? 'bg-gradient-to-r from-forgePurple to-neuralBlue border-transparent shadow-lg shadow-purple-500/20'
                      : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
                  } border backdrop-blur-xl`}
                >
                  <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">📌</div>
                  <h3 className="font-bold text-white">All Topics</h3>
                  <p className="text-sm text-white/60 mt-1">{total} threads</p>
                </button>
                
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => {
                      setSelectedCategory(category.id);
                      setSkip(0);
                    }}
                    className={`group p-4 rounded-xl text-left transition-all duration-300 ${
                      selectedCategory === category.id
                        ? 'bg-gradient-to-r from-forgePurple to-neuralBlue border-transparent shadow-lg shadow-purple-500/20'
                        : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
                    } border backdrop-blur-xl`}
                  >
                    <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">
                      {category.icon_emoji || '📚'}
                    </div>
                    <h3 className="font-bold text-white">{category.name}</h3>
                    <p className="text-sm text-white/60 mt-1">{category.thread_count} threads</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Controls */}
          <PageContainer variant="card" className="mb-6">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="🔍 Search threads..."
                  className="w-full px-4 py-3 pl-4 bg-white/10 text-white rounded-xl border border-white/20 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none placeholder-white/40"
                />
              </div>

              {/* Sort */}
              <div className="flex gap-2">
                {sortOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => {
                      setSortBy(option.value);
                      setSkip(0);
                    }}
                    className={`px-4 py-2.5 rounded-xl font-medium transition-all whitespace-nowrap ${
                      sortBy === option.value
                        ? 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white shadow-lg'
                        : 'bg-white/10 text-white/70 hover:bg-white/20 border border-white/10'
                    }`}
                  >
                    <span className="hidden md:inline">{option.label}</span>
                    <span className="md:hidden">{option.icon}</span>
                  </button>
                ))}
              </div>
            </div>
          </PageContainer>

          {/* Threads List */}
          {loading ? (
            <LoadingState message="Loading threads..." />
          ) : filteredThreads.length === 0 ? (
            <EmptyState
              icon="📭"
              title="No threads found"
              description={selectedCategory ? 'Try another category or create a new thread.' : 'Be the first to start a discussion!'}
              action={
                <Link href="/forums/create" className="px-6 py-3 bg-gradient-to-r from-forgePurple to-neuralBlue text-white rounded-xl font-semibold hover:opacity-90 transition">
                    Create Thread
                </Link>
              }
            />
          ) : (
            <>
              <div className="space-y-4">
                {/* Pinned Threads */}
                {filteredThreads.filter(t => t.is_pinned).map((thread) => (
                  <ThreadCard key={thread.id} thread={thread} formatDate={formatDate} getThreadTypeIcon={getThreadTypeIcon} getStatusBadge={getStatusBadge} isPinned />
                ))}
                
                {/* Regular Threads */}
                {filteredThreads.filter(t => !t.is_pinned).map((thread) => (
                  <ThreadCard key={thread.id} thread={thread} formatDate={formatDate} getThreadTypeIcon={getThreadTypeIcon} getStatusBadge={getStatusBadge} />
                ))}
              </div>

              {/* Pagination */}
              <div className="mt-8 flex justify-between items-center">
                <button
                  onClick={() => setSkip(Math.max(0, skip - LIMIT))}
                  disabled={skip === 0}
                  className="px-6 py-3 bg-white/10 hover:bg-white/20 disabled:opacity-30 disabled:cursor-not-allowed text-white rounded-xl transition border border-white/10 font-semibold"
                >
                  ← Previous
                </button>
                
                <div className="flex items-center gap-2 text-white/60">
                  <span className="hidden sm:inline">Showing</span>
                  <span className="font-semibold text-white">{skip + 1}-{Math.min(skip + LIMIT, total)}</span>
                  <span>of</span>
                  <span className="font-semibold text-white">{total}</span>
                </div>
                
                <button
                  onClick={() => setSkip(skip + LIMIT)}
                  disabled={skip + LIMIT >= total}
                  className="px-6 py-3 bg-white/10 hover:bg-white/20 disabled:opacity-30 disabled:cursor-not-allowed text-white rounded-xl transition border border-white/10 font-semibold"
                >
                  Next →
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
};

// Thread Card Component
interface ThreadCardProps {
  thread: Thread;
  formatDate: (date: string) => string;
  getThreadTypeIcon: (type: string) => string;
  getStatusBadge: (status: string) => React.ReactNode;
  isPinned?: boolean;
}

const ThreadCard: React.FC<ThreadCardProps> = ({ thread, formatDate, getThreadTypeIcon, getStatusBadge, isPinned }) => {
  return (
    <Link 
      href={`/forums/${thread.id}`}
      className={`block bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-xl p-6 border transition-all duration-300 hover:scale-[1.01] hover:shadow-xl group ${
        isPinned ? 'border-yellow-500/30 shadow-lg shadow-yellow-500/10' : 'border-white/10 hover:border-purple-500/30'
      }`}
    >
        <div className="flex items-start gap-4">
          {/* Avatar & Type Icon */}
          <div className="relative flex-shrink-0">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-lg font-bold shadow-lg">
              {thread.creator.avatar_url ? (
                <img src={thread.creator.avatar_url} alt={thread.creator.username} className="w-full h-full rounded-xl object-cover" />
              ) : (
                thread.creator.username?.[0]?.toUpperCase() || 'U'
              )}
            </div>
            <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-gray-900 rounded-lg flex items-center justify-center text-sm border border-white/20">
              {getThreadTypeIcon(thread.thread_type)}
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start gap-2 flex-wrap mb-2">
              {isPinned && (
                <span className="px-2 py-0.5 bg-yellow-500/20 text-yellow-400 rounded-full text-xs font-semibold">
                  📌 Pinned
                </span>
              )}
              {getStatusBadge(thread.status)}
            </div>
            
            <h3 className="text-lg font-bold text-white group-hover:text-purple-400 transition-colors line-clamp-2 mb-2">
              {thread.title}
            </h3>
            
            <div className="flex items-center gap-3 text-sm text-white/50">
              <span className="font-medium text-white/70">{thread.creator.username}</span>
              <span>•</span>
              <span>{formatDate(thread.created_at)}</span>
              {thread.last_reply_at && (
                <>
                  <span>•</span>
                  <span className="text-green-400">Last reply {formatDate(thread.last_reply_at)}</span>
                </>
              )}
            </div>
          </div>

          {/* Stats */}
          <div className="flex gap-4 flex-shrink-0">
            <div className="text-center px-3 py-2 bg-white/5 rounded-lg">
              <p className="text-lg font-bold text-white">{thread.reply_count}</p>
              <p className="text-xs text-white/50">💬</p>
            </div>
            <div className="text-center px-3 py-2 bg-white/5 rounded-lg">
              <p className="text-lg font-bold text-white">{thread.view_count}</p>
              <p className="text-xs text-white/50">👁️</p>
            </div>
            {thread.vote_count > 0 && (
              <div className="text-center px-3 py-2 bg-green-500/10 rounded-lg">
                <p className="text-lg font-bold text-green-400">+{thread.vote_count}</p>
                <p className="text-xs text-white/50">👍</p>
              </div>
            )}
          </div>
        </div>
    </Link>
  );
};

export default ForumsPage;
