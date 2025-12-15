import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { apiCall } from '@/lib/api';

interface Contest {
  id: number;
  title: string;
  description: string;
  status: string;
  category: string;
  difficulty: string;
  start_time: string;
  end_time: string;
  registration_deadline: string;
  total_participants: number;
  total_prize_pool: number;
  banner_image: string | null;
  is_featured: boolean;
}

interface ContestFilters {
  status: string;
  category: string;
  difficulty: string;
  sortBy: string;
}

const ContestBrowserPage: React.FC = () => {
  const [contests, setContests] = useState<Contest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [filters, setFilters] = useState<ContestFilters>({
    status: '',
    category: '',
    difficulty: '',
    sortBy: 'start_time',
  });

  // Fetch contests
  useEffect(() => {
    const fetchContests = async () => {
      try {
        setLoading(true);
        setError('');

        const params = new URLSearchParams();
        if (filters.status) params.append('status_filter', filters.status);
        if (filters.category) params.append('category', filters.category);
        params.append('sort_by', filters.sortBy);

        const data = await apiCall(`/api/v1x/contests?${params.toString()}`, {
          method: 'GET',
        });

        setContests(data || []);
      } catch (err: any) {
        setError('Failed to load contests');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchContests();
  }, [filters]);

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'upcoming':
        return 'bg-blue-100 text-blue-800';
      case 'finished':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'hard':
        return 'text-red-600';
      case 'expert':
        return 'text-purple-600';
      default:
        return 'text-gray-600';
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

  return (
    <Layout>
      <div className="max-w-6xl mx-auto py-12">
        <h1 className="text-4xl font-bold mb-8">🏆 Contests & Competitions</h1>

        {/* Filters */}
        <Card className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Status</label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">All Contests</option>
                <option value="upcoming">Upcoming</option>
                <option value="active">Active</option>
                <option value="finished">Finished</option>
              </select>
            </div>

            {/* Category Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Category</label>
              <select
                value={filters.category}
                onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">All Categories</option>
                <option value="dsa">Data Structures</option>
                <option value="algorithms">Algorithms</option>
                <option value="web">Web Development</option>
                <option value="ml">Machine Learning</option>
                <option value="systems">Systems Design</option>
              </select>
            </div>

            {/* Difficulty Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Difficulty</label>
              <select
                value={filters.difficulty}
                onChange={(e) => setFilters({ ...filters, difficulty: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">All Levels</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
                <option value="expert">Expert</option>
              </select>
            </div>

            {/* Sort By */}
            <div>
              <label className="block text-sm font-medium mb-2">Sort By</label>
              <select
                value={filters.sortBy}
                onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="start_time">Start Time</option>
                <option value="prize_pool">Prize Pool</option>
                <option value="participants">Participants</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12 text-gray-600">
            Loading contests...
          </div>
        )}

        {/* Contests Grid */}
        {!loading && contests.length === 0 && (
          <div className="text-center py-12 text-gray-600">
            No contests found. Try adjusting your filters.
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {contests.map((contest) => (
            <Link key={contest.id} href={`/contests/${contest.id}`}>
              <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
                {/* Banner Image */}
                {contest.banner_image && (
                  <div className="mb-4 -mx-6 -mt-6">
                    <img
                      src={contest.banner_image}
                      alt={contest.title}
                      className="w-full h-40 object-cover"
                    />
                  </div>
                )}

                {/* Featured Badge */}
                {contest.is_featured && (
                  <div className="mb-3">
                    <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-xs font-semibold">
                      ⭐ Featured
                    </span>
                  </div>
                )}

                {/* Title */}
                <h3 className="text-xl font-bold mb-2">{contest.title}</h3>

                {/* Description */}
                <p className="text-gray-600 mb-4 line-clamp-2">{contest.description}</p>

                {/* Status & Category */}
                <div className="flex gap-2 mb-4 flex-wrap">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadgeColor(contest.status)}`}>
                    {contest.status.charAt(0).toUpperCase() + contest.status.slice(1)}
                  </span>
                  <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-semibold">
                    {contest.category}
                  </span>
                  <span className={`px-3 py-1 bg-gray-100 rounded-full text-xs font-semibold ${getDifficultyColor(contest.difficulty)}`}>
                    {contest.difficulty.toUpperCase()}
                  </span>
                </div>

                {/* Timing */}
                <div className="bg-gray-50 rounded-lg p-3 mb-4 text-sm">
                  <div className="text-gray-600 mb-1">
                    <span className="font-semibold">Starts:</span> {formatDate(contest.start_time)}
                  </div>
                  <div className="text-gray-600 mb-1">
                    <span className="font-semibold">Ends:</span> {formatDate(contest.end_time)}
                  </div>
                  <div className="text-gray-600">
                    <span className="font-semibold">Register by:</span> {formatDate(contest.registration_deadline)}
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-2 mb-4 bg-gray-50 rounded-lg p-3">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">{contest.total_participants}</p>
                    <p className="text-xs text-gray-600">Participants</p>
                  </div>
                  <div className="text-center border-l border-r border-gray-300">
                    <p className="text-2xl font-bold text-green-600">💰</p>
                    <p className="text-xs text-gray-600">{contest.total_prize_pool.toLocaleString()}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">🎯</p>
                    <p className="text-xs text-gray-600">Prize Pool</p>
                  </div>
                </div>

                {/* View Button */}
                <Button className="w-full bg-blue-600 text-white">
                  View Contest →
                </Button>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </Layout>
  );
};

export default ContestBrowserPage;
