import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Calendar, Users, Trophy, Clock, TrendingUp } from 'lucide-react';
import Link from 'next/link';

interface Contest {
  id: number;
  title: string;
  description: string;
  category: string;
  status: string;
  start_time: string;
  end_time: string;
  difficulty: string;
  participants: number;
  prize_pool: number;
  is_featured: boolean;
  is_registered: boolean;
}

export default function ContestsPage() {
  const [contests, setContests] = useState<Contest[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [category, setCategory] = useState('all');

  useEffect(() => {
    fetchContests();
  }, [filter, category]);

  const fetchContests = async () => {
    try {
      const token = localStorage.getItem('token');
      const url = new URL(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/contests`);
      
      if (filter !== 'all') {
        url.searchParams.append('status_filter', filter);
      }
      if (category !== 'all') {
        url.searchParams.append('category', category);
      }

      const res = await fetch(url.toString(), {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (res.ok) {
        const data = await res.json();
        setContests(Array.isArray(data) ? data : data.contests || []);
      }
    } catch (err) {
      console.error('Failed to fetch contests:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300';
      case 'UPCOMING':
        return 'bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300';
      case 'ENDED':
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300';
      default:
        return 'bg-purple-100 dark:bg-purple-900/20 text-purple-800 dark:text-purple-300';
    }
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const timeRemaining = (endDate: string) => {
    const now = new Date();
    const end = new Date(endDate);
    const diff = end.getTime() - now.getTime();

    if (diff < 0) return 'Ended';
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

    if (days > 0) return `${days}d ${hours}h left`;
    return `${hours}h left`;
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Coding Contests</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Compete, learn, and win prizes</p>
        </div>

        {/* Filters */}
        <div className="flex flex-col gap-4 mb-8">
          {/* Status Filter */}
          <div className="flex gap-2 overflow-x-auto pb-2">
            {[
              { value: 'all', label: 'All Contests' },
              { value: 'ACTIVE', label: 'Active' },
              { value: 'UPCOMING', label: 'Upcoming' },
              { value: 'ENDED', label: 'Ended' },
            ].map(tab => (
              <button
                key={tab.value}
                onClick={() => setFilter(tab.value)}
                className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition ${
                  filter === tab.value
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Category Filter */}
          <div className="flex gap-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 self-center">Category:</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
            >
              <option value="all">All Categories</option>
              <option value="programming">Programming</option>
              <option value="data-structures">Data Structures</option>
              <option value="algorithms">Algorithms</option>
              <option value="web-development">Web Development</option>
              <option value="machine-learning">Machine Learning</option>
            </select>
          </div>
        </div>

        {/* Contests Grid */}
        {contests.length === 0 ? (
          <div className="text-center py-12">
            <Trophy className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              No contests found matching your filters.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {contests.map(contest => (
              <Link key={contest.id} href={`/contests/${contest.id}`} className="block">
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-lg transition overflow-hidden h-full">
                    {/* Featured Badge */}
                    {contest.is_featured && (
                      <div className="h-1 bg-gradient-to-r from-yellow-400 to-orange-500"></div>
                    )}

                    <div className="p-6">
                      {/* Header */}
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex-1">
                          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                            {contest.title}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {contest.category}
                          </p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ml-2 ${getStatusColor(contest.status)}`}>
                          {contest.status}
                        </span>
                      </div>

                      {/* Description */}
                      <p className="text-gray-700 dark:text-gray-300 text-sm mb-4 line-clamp-2">
                        {contest.description}
                      </p>

                      {/* Difficulty */}
                      <div className="mb-4">
                        <span className={`inline-block px-3 py-1 rounded text-xs font-medium ${
                          contest.difficulty === 'EASY' ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300' :
                          contest.difficulty === 'MEDIUM' ? 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300' :
                          'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300'
                        }`}>
                          {contest.difficulty}
                        </span>
                      </div>

                      {/* Stats */}
                      <div className="grid grid-cols-3 gap-4 py-4 border-y border-gray-200 dark:border-gray-700 mb-4">
                        <div className="text-center">
                          <Users className="w-4 h-4 text-gray-400 mx-auto mb-1" />
                          <p className="text-lg font-bold text-gray-900 dark:text-white">
                            {contest.participants}
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">Participants</p>
                        </div>
                        <div className="text-center">
                          <Trophy className="w-4 h-4 text-yellow-500 mx-auto mb-1" />
                          <p className="text-lg font-bold text-gray-900 dark:text-white">
                            ${contest.prize_pool}
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">Prize Pool</p>
                        </div>
                        <div className="text-center">
                          <Clock className="w-4 h-4 text-blue-500 mx-auto mb-1" />
                          <p className="text-sm font-bold text-gray-900 dark:text-white">
                            {timeRemaining(contest.end_time)}
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">Remaining</p>
                        </div>
                      </div>

                      {/* Footer */}
                      <div className="flex justify-between items-center">
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          {formatDate(contest.start_time)}
                        </p>
                        {contest.is_registered ? (
                          <span className="px-4 py-2 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded font-medium text-sm">
                            Registered
                          </span>
                        ) : contest.status === 'ACTIVE' ? (
                          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium text-sm transition">
                            Register Now
                          </button>
                        ) : (
                          <button className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded font-medium text-sm">
                            View
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
