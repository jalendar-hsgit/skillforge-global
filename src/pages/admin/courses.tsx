import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import AnalyticsCard from '@/components/admin/AnalyticsCard';

interface CourseAnalytic {
  id: number;
  title: string;
  enrollments: number;
  completions: number;
  completionRate: number;
  averageRating: number;
  revenue: number;
  students: number;
}

export default function CourseAnalyticsPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [courses, setCourses] = useState<CourseAnalytic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sortBy, setSortBy] = useState<'enrollments' | 'completion' | 'revenue' | 'rating'>('enrollments');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (user && !['ADMIN', 'SUPERADMIN'].includes(user.role)) {
      router.push('/');
      return;
    }

    if (isAuthenticated && user?.id) {
      fetchCourseAnalytics();
    }
  }, [isAuthenticated, user?.id, user?.role]);

  const fetchCourseAnalytics = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiBase}/api/v1x/admin/analytics/courses`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to fetch course analytics');
      const data = await response.json();
      setCourses(data.courses || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading course analytics');
      console.error('Course analytics fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  let displayedCourses = courses.filter(c =>
    c.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (sortBy === 'enrollments') {
    displayedCourses.sort((a, b) => b.enrollments - a.enrollments);
  } else if (sortBy === 'completion') {
    displayedCourses.sort((a, b) => b.completionRate - a.completionRate);
  } else if (sortBy === 'revenue') {
    displayedCourses.sort((a, b) => b.revenue - a.revenue);
  } else if (sortBy === 'rating') {
    displayedCourses.sort((a, b) => b.averageRating - a.averageRating);
  }

  const totalEnrollments = courses.reduce((sum, c) => sum + c.enrollments, 0);
  const totalCompletions = courses.reduce((sum, c) => sum + c.completions, 0);
  const avgCompletionRate = courses.length > 0
    ? (courses.reduce((sum, c) => sum + c.completionRate, 0) / courses.length)
    : 0;
  const totalRevenue = courses.reduce((sum, c) => sum + c.revenue, 0);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading course analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Course Analytics - SkillForge Admin</title>
        <meta name="description" content="Course analytics and performance metrics" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-7xl mx-auto px-4">
          {/* Header & Navigation */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                📚 Course Analytics
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Performance metrics for all courses
              </p>
            </div>
            <Link href="/admin/dashboard">
              <button className="px-4 py-2 rounded-lg bg-gray-300 dark:bg-gray-700 hover:bg-gray-400 dark:hover:bg-gray-600">
                ← Back
              </button>
            </Link>
          </div>

          {error && (
            <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <AnalyticsCard
              title="Total Enrollments"
              value={totalEnrollments}
              icon="📝"
              color="blue"
            />
            <AnalyticsCard
              title="Total Completions"
              value={totalCompletions}
              icon="✅"
              color="green"
            />
            <AnalyticsCard
              title="Avg Completion Rate"
              value={`${Math.round(avgCompletionRate)}%`}
              icon="📊"
              color="purple"
            />
            <AnalyticsCard
              title="Total Revenue"
              value={`$${totalRevenue.toLocaleString()}`}
              icon="💰"
              color="green"
            />
          </div>

          {/* Controls */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Search */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Search Courses
                </label>
                <input
                  type="text"
                  placeholder="Search by course name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Sort */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Sort By
                </label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                >
                  <option value="enrollments">Most Enrollments</option>
                  <option value="completion">Highest Completion Rate</option>
                  <option value="revenue">Highest Revenue</option>
                  <option value="rating">Highest Rating</option>
                </select>
              </div>
            </div>
          </div>

          {/* Courses Table */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
            {displayedCourses.length === 0 ? (
              <div className="p-12 text-center text-gray-600 dark:text-gray-400">
                <p className="text-lg">No courses found</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-100 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Course Name
                      </th>
                      <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Enrollments
                      </th>
                      <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Completions
                      </th>
                      <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Completion %
                      </th>
                      <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Rating
                      </th>
                      <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Revenue
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {displayedCourses.map((course) => (
                      <tr
                        key={course.id}
                        className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                      >
                        <td className="px-6 py-4">
                          <div>
                            <p className="font-semibold text-gray-900 dark:text-white">
                              {course.title}
                            </p>
                            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                              {course.students} students
                            </p>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <span className="font-semibold text-gray-900 dark:text-white">
                            {course.enrollments}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <span className="font-semibold text-green-600 dark:text-green-400">
                            {course.completions}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-blue-500"
                                style={{ width: `${course.completionRate}%` }}
                              />
                            </div>
                            <span className="text-sm font-semibold text-gray-900 dark:text-white w-12">
                              {Math.round(course.completionRate)}%
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-1">
                            <span className="text-yellow-500">⭐</span>
                            <span className="font-semibold text-gray-900 dark:text-white">
                              {course.averageRating.toFixed(1)}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <span className="font-semibold text-green-600 dark:text-green-400">
                            ${course.revenue.toLocaleString()}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
