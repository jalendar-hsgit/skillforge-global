'use client';

import { useState, useEffect } from 'react';
import Head from 'next/head';
import Layout from '@/components/Layout';
import { API_BASE } from '@/lib/apiBase';
import { Line, Pie, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { TrendingUp, BarChart3, PieChart as PieChartIcon, Calendar, Target, Zap } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface Stats {
  total_applications: number;
  by_status: Record<string, number>;
  response_rate: number;
  avg_response_time_days?: number;
  avg_salary_min?: number;
  avg_salary_max?: number;
  applications_this_month: number;
  offers_received: number;
  interviews_scheduled: number;
  overdue_follow_ups: number;
}

interface Application {
  id: number;
  company_name: string;
  position_title: string;
  status: string;
  application_date: string;
  salary_min?: number;
  salary_max?: number;
  interviews: any[];
}

export default function JobTrackerAnalytics() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Fetch stats
      const statsRes = await fetch(`${API_BASE}/api/v1x/job-applications/stats`, {
        credentials: 'include',
      });
      if (statsRes.ok) {
        setStats(await statsRes.json());
      }

      // Fetch all applications for additional analytics
      const appsRes = await fetch(`${API_BASE}/api/v1x/job-applications?limit=1000`, {
        credentials: 'include',
      });
      if (appsRes.ok) {
        setApplications(await appsRes.json());
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  // Process data for charts
  const getStatusChart = () => {
    if (!stats) return null;

    const labels = Object.keys(stats.by_status).map(s => s.charAt(0).toUpperCase() + s.slice(1));
    const data = Object.values(stats.by_status);

    return {
      labels,
      datasets: [{
        label: 'Applications by Status',
        data,
        backgroundColor: [
          '#f3f4f6',
          '#dbeafe',
          '#e9d5ff',
          '#fef3c7',
          '#c7d2fe',
          '#dcfce7',
          '#d1fae5',
          '#fee2e2',
        ],
        borderColor: [
          '#d1d5db',
          '#93c5fd',
          '#d8b4fe',
          '#fcd34d',
          '#a5b4fc',
          '#86efac',
          '#6ee7b7',
          '#fca5a5',
        ],
        borderWidth: 2,
      }],
    };
  };

  // Applications timeline
  const getTimelineChart = () => {
    if (!applications.length) return null;

    const appsByDate: Record<string, number> = {};
    applications.forEach(app => {
      const date = new Date(app.application_date).toLocaleDateString();
      appsByDate[date] = (appsByDate[date] || 0) + 1;
    });

    const dates = Object.keys(appsByDate).sort();
    const cumulative = dates.map((_, i) => 
      Object.values(appsByDate).slice(0, i + 1).reduce((a, b) => a + b, 0)
    );

    return {
      labels: dates.slice(-30), // Last 30 days
      datasets: [{
        label: 'Cumulative Applications',
        data: cumulative.slice(-30),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.3,
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      }],
    };
  };

  const statusChart = getStatusChart();
  const timelineChart = getTimelineChart();

  return (
    <>
      <Head>
        <title>Job Tracker Analytics | SkillForge Global</title>
      </Head>

      <Layout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-3 mb-8">
            <TrendingUp className="w-10 h-10 text-blue-600" />
            Job Search Analytics
          </h1>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600">Loading analytics...</p>
              </div>
            </div>
          ) : (
            <>
              {/* Top Metrics */}
              {stats && (
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg border border-blue-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm">Total Applications</p>
                        <p className="text-3xl font-bold text-blue-600">{stats.total_applications}</p>
                      </div>
                      <Target className="w-8 h-8 text-blue-300" />
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg border border-green-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm">Response Rate</p>
                        <p className="text-3xl font-bold text-green-600">{Math.round(stats.response_rate * 100)}%</p>
                      </div>
                      <TrendingUp className="w-8 h-8 text-green-300" />
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg border border-purple-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm">Avg Response Time</p>
                        <p className="text-3xl font-bold text-purple-600">
                          {stats.avg_response_time_days ? `${stats.avg_response_time_days}d` : 'N/A'}
                        </p>
                      </div>
                      <Calendar className="w-8 h-8 text-purple-300" />
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-6 rounded-lg border border-yellow-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm">Offers Received</p>
                        <p className="text-3xl font-bold text-yellow-600">{stats.offers_received}</p>
                      </div>
                      <Zap className="w-8 h-8 text-yellow-300" />
                    </div>
                  </div>
                </div>
              )}

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Status Distribution */}
                {statusChart && (
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <PieChartIcon className="w-5 h-5 text-purple-600" />
                      Status Distribution
                    </h2>
                    <div style={{ height: '300px', position: 'relative' }}>
                      <Pie data={statusChart} options={{ responsive: true, maintainAspectRatio: false }} />
                    </div>
                  </div>
                )}

                {/* Timeline */}
                {timelineChart && (
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-blue-600" />
                      Application Timeline
                    </h2>
                    <div style={{ height: '300px', position: 'relative' }}>
                      <Line data={timelineChart} options={{ responsive: true, maintainAspectRatio: false }} />
                    </div>
                  </div>
                )}
              </div>

              {/* Additional Metrics */}
              {stats && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">📊 This Month</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                        <span className="text-gray-600">Applications</span>
                        <span className="text-2xl font-bold text-blue-600">{stats.applications_this_month}</span>
                      </div>
                      <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                        <span className="text-gray-600">Interviews Scheduled</span>
                        <span className="text-2xl font-bold text-yellow-600">{stats.interviews_scheduled}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Overdue Follow-ups</span>
                        <span className="text-2xl font-bold text-red-600">{stats.overdue_follow_ups}</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">💰 Salary Insights</h3>
                    <div className="space-y-3">
                      {stats.avg_salary_min && (
                        <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                          <span className="text-gray-600">Average Min Salary</span>
                          <span className="text-2xl font-bold text-green-600">
                            ${Math.round(stats.avg_salary_min)}k
                          </span>
                        </div>
                      )}
                      {stats.avg_salary_max && (
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Average Max Salary</span>
                          <span className="text-2xl font-bold text-green-600">
                            ${Math.round(stats.avg_salary_max)}k
                          </span>
                        </div>
                      )}
                      {!stats.avg_salary_min && !stats.avg_salary_max && (
                        <p className="text-gray-500">No salary data available</p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Tips */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-bold text-blue-900 mb-3">💡 Tips to Improve Your Success Rate</h3>
                <ul className="space-y-2 text-blue-800">
                  <li>✅ Follow up 1 week after applying if no response</li>
                  <li>✅ Customize cover letters for each position (increase response rate by 20-30%)</li>
                  <li>✅ Apply to 5-10 quality positions per week</li>
                  <li>✅ Track interviews and prepare thoroughly (practice with friends)</li>
                  <li>✅ Keep records of contacts and conversations for future reference</li>
                </ul>
              </div>
            </>
          )}
        </div>
      </Layout>
    </>
  );
}
