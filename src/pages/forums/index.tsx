import React, { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
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
  const LIMIT = 20;

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    loadThreads();
  }, [selectedCategory, sortBy, skip]);

  const loadCategories = async () => {
    try {
      const response = await apiCall('GET', '/forums/categories');
      setCategories(response || []);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const loadThreads = async () => {
    try {
      setLoading(true);
      let url = `/forums/threads?skip=${skip}&limit=${LIMIT}&sort_by=${sortBy}`;
      if (selectedCategory) {
        url += `&category_id=${selectedCategory}`;
      }
      
      const response = await apiCall('GET', url) as ThreadListResponse;
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

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const days = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days}d ago`;
    if (days < 30) return `${Math.floor(days / 7)}w ago`;
    return date.toLocaleDateString();
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8 flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
                <span className="text-3xl">💬</span>
                Forums
              </h1>
              <p className="text-gray-400">Ask questions, share knowledge, and discuss</p>
            </div>
            <Link href="/forums/create">
              <a className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition">
                New Thread
              </a>
            </Link>
          </div>

          {/* Categories */}
          {categories.length > 0 && (
            <div className="mb-8">
              <h2 className="text-xl font-bold text-white mb-4">Categories</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <button
                  onClick={() => {
                    setSelectedCategory(null);
                    setSkip(0);
                  }}
                  className={`p-4 rounded-lg text-left transition ${
                    selectedCategory === null
                      ? 'bg-blue-600 border-blue-500'
                      : 'bg-gray-800 border-gray-700 hover:bg-gray-750'
                  } border-2`}
                >
                  <div className="text-2xl mb-2">📌</div>
                  <h3 className="font-bold text-white">All Categories</h3>
                  <p className="text-sm text-gray-400 mt-1">{total} threads</p>
                </button>
                
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => {
                      setSelectedCategory(category.id);
                      setSkip(0);
                    }}
                    className={`p-4 rounded-lg text-left transition ${
                      selectedCategory === category.id
                        ? 'bg-blue-600 border-blue-500'
                        : 'bg-gray-800 border-gray-700 hover:bg-gray-750'
                    } border-2`}
                  >
                    <div className="text-2xl mb-2">{category.icon_emoji || '📚'}</div>
                    <h3 className="font-bold text-white">{category.name}</h3>
                    <p className="text-sm text-gray-400 mt-1">{category.thread_count} threads</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Sorting */}
          <div className="mb-6 flex gap-4">
            <select
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value);
                setSkip(0);
              }}
              className="px-4 py-2 bg-gray-800 text-white rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
            >
              <option value="recent">Most Recent</option>
              <option value="popular">Most Popular</option>
              <option value="viewed">Most Viewed</option>
              <option value="unanswered">Unanswered</option>
            </select>
          </div>

          {/* Threads List */}
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin">
                <div className="w-8 h-8 border-4 border-gray-600 border-t-blue-500 rounded-full"></div>
              </div>
              <p className="text-gray-400 mt-4">Loading threads...</p>
            </div>
          ) : threads.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">
                No threads found. {selectedCategory ? 'Try another category.' : 'Be the first to create one!'}
              </p>
            </div>
          ) : (
            <>
              <div className="space-y-4">
                {threads.map((thread) => (
                  <Link key={thread.id} href={`/forums/${thread.id}`}>
                    <a className="block bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-blue-500 transition">
                      <div className="flex items-start justify-between gap-4">
                        {/* Icon and Title */}
                        <div className="flex-1">
                          <div className="flex items-start gap-3 mb-2">
                            <span className="text-2xl mt-1">{getThreadTypeIcon(thread.thread_type)}</span>
                            {thread.is_pinned && <span className="text-lg">📌</span>}
                            <div className="flex-1">
                              <h3 className="text-lg font-bold text-white hover:text-blue-400 break-words">
                                {thread.title}
                              </h3>
                              <p className="text-sm text-gray-400 mt-1">
                                by {thread.creator.username} · {formatDate(thread.created_at)}
                              </p>
                            </div>
                          </div>
                        </div>

                        {/* Stats */}
                        <div className="flex gap-6 text-right flex-shrink-0">
                          <div>
                            <p className="text-lg font-bold text-gray-300">{thread.reply_count}</p>
                            <p className="text-xs text-gray-400">Replies</p>
                          </div>
                          <div>
                            <p className="text-lg font-bold text-gray-300">{thread.view_count}</p>
                            <p className="text-xs text-gray-400">Views</p>
                          </div>
                          {thread.vote_count > 0 && (
                            <div>
                              <p className="text-lg font-bold text-green-400">{thread.vote_count}</p>
                              <p className="text-xs text-gray-400">Votes</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </a>
                  </Link>
                ))}
              </div>

              {/* Pagination */}
              <div className="mt-8 flex justify-between items-center">
                <button
                  onClick={() => setSkip(Math.max(0, skip - LIMIT))}
                  disabled={skip === 0}
                  className="px-6 py-2 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-white rounded-lg transition"
                >
                  Previous
                </button>
                
                <span className="text-gray-400">
                  Showing {Math.min(skip + LIMIT, total)} of {total}
                </span>
                
                <button
                  onClick={() => setSkip(skip + LIMIT)}
                  disabled={skip + LIMIT >= total}
                  className="px-6 py-2 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-white rounded-lg transition"
                >
                  Next
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default ForumsPage;
