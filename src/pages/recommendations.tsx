export const dynamic = 'force-dynamic'

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { API_BASE } from '@/lib/api';

interface Recommendation {
  id: number;
  challenge_id: number;
  algorithm: string;
  recommendation_reason: string;
  matching_percentage: number;
  rank: number;
  was_viewed: boolean;
  was_attempted: boolean;
  was_completed: boolean;
  is_dismissed: boolean;
}

interface Queue {
  challenge_id: number;
  score: number;
  position: number;
}

export default function RecommendationsPage() {
  const router = useRouter();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [queue, setQueue] = useState<Queue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tab, setTab] = useState<'recommendations' | 'queue'>('recommendations');
  const [stats, setStats] = useState({
    total_recommendations: 0,
    viewed: 0,
    attempted: 0,
    completed: 0,
    view_rate: 0,
    completion_rate: 0,
  });

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchRecommendations();
    fetchStats();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/v1x/recommendations/?page=1&page_size=10`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch recommendations');
      const data = await response.json();
      setRecommendations(data.recommendations);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchQueue = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1x/recommendations/queue`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setQueue(data.queue);
      }
    } catch (err) {
      console.error('Failed to fetch queue:', err);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1x/recommendations/stats`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const generateRecommendations = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/v1x/recommendations/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to generate recommendations');
      const data = await response.json();
      setRecommendations(data);
      fetchStats();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const dismissRecommendation = async (id: number) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1x/recommendations/${id}/dismiss`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        setRecommendations(recommendations.filter(r => r.id !== id));
      }
    } catch (err) {
      console.error('Failed to dismiss recommendation:', err);
    }
  };

  const refreshQueue = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1x/recommendations/queue/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setQueue(data.queue);
      }
    } catch (err) {
      console.error('Failed to refresh queue:', err);
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        {/* Header */}
        <div className="bg-white border-b border-slate-200">
          <div className="container mx-auto px-4 py-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold text-slate-900">🎯 Personalized Recommendations</h1>
                <p className="text-slate-600 mt-2">AI-powered challenges matched to your learning style</p>
              </div>
              <Button
                onClick={generateRecommendations}
                disabled={loading}
              >
                🔄 Generate New
              </Button>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <Card className="bg-white p-6">
              <div className="text-slate-600 text-sm font-semibold">Total Recommendations</div>
              <div className="text-3xl font-bold text-slate-900">{stats.total_recommendations}</div>
            </Card>
            <Card className="bg-white p-6">
              <div className="text-slate-600 text-sm font-semibold">View Rate</div>
              <div className="text-3xl font-bold text-blue-600">{(stats.view_rate * 100).toFixed(1)}%</div>
              <div className="text-xs text-slate-500 mt-1">{stats.viewed} viewed</div>
            </Card>
            <Card className="bg-white p-6">
              <div className="text-slate-600 text-sm font-semibold">Completion Rate</div>
              <div className="text-3xl font-bold text-green-600">{(stats.completion_rate * 100).toFixed(1)}%</div>
              <div className="text-xs text-slate-500 mt-1">{stats.completed} completed</div>
            </Card>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 mb-6 border-b border-slate-200">
            <button
              onClick={() => {
                setTab('recommendations');
                fetchRecommendations();
              }}
              className={`px-4 py-3 font-semibold border-b-2 transition ${
                tab === 'recommendations'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              📚 Recommendations ({recommendations.length})
            </button>
            <button
              onClick={() => {
                setTab('queue');
                fetchQueue();
              }}
              className={`px-4 py-3 font-semibold border-b-2 transition ${
                tab === 'queue'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              📋 Daily Queue ({queue.length})
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 text-red-700">
              {error}
            </div>
          )}

          {loading && tab === 'recommendations' ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin">⏳</div>
              <p className="text-slate-600 mt-2">Loading recommendations...</p>
            </div>
          ) : (
            <>
              {/* Recommendations Tab */}
              {tab === 'recommendations' && (
                <div className="space-y-4">
                  {recommendations.length === 0 ? (
                    <Card className="bg-white p-8 text-center">
                      <div className="text-4xl mb-4">🎯</div>
                      <h3 className="text-xl font-semibold text-slate-900 mb-2">No Recommendations Yet</h3>
                      <p className="text-slate-600 mb-4">Click "Generate New" to get personalized challenge recommendations</p>
                      <Button onClick={generateRecommendations}>Generate Recommendations</Button>
                    </Card>
                  ) : (
                    recommendations.map((rec) => (
                      <Card key={rec.id} className="bg-white p-6 border border-slate-200 hover:border-blue-300 transition">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className="text-2xl">
                                {rec.algorithm === 'collaborative_filtering' ? '🤝' : '⚡'}
                              </span>
                              <div>
                                <h3 className="font-semibold text-slate-900">Challenge #{rec.challenge_id}</h3>
                                <p className="text-sm text-slate-600">{rec.recommendation_reason}</p>
                              </div>
                            </div>
                            
                            <div className="flex items-center gap-4 mt-4">
                              <div className="flex-1">
                                <div className="text-xs text-slate-500 mb-1">Match Score</div>
                                <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                                  <div
                                    className="h-full bg-gradient-to-r from-blue-500 to-green-500"
                                    style={{ width: `${rec.matching_percentage}%` }}
                                  />
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="text-lg font-bold text-slate-900">{rec.matching_percentage.toFixed(0)}%</div>
                              </div>
                            </div>

                            <div className="flex gap-3 mt-4">
                              {rec.was_viewed && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">✓ Viewed</span>}
                              {rec.was_attempted && <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded">✓ Attempted</span>}
                              {rec.was_completed && <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">✓ Completed</span>}
                            </div>
                          </div>
                          
                          <button
                            onClick={() => dismissRecommendation(rec.id)}
                            className="ml-4 text-slate-400 hover:text-slate-600"
                            title="Dismiss this recommendation"
                          >
                            ✕
                          </button>
                        </div>
                      </Card>
                    ))
                  )}
                </div>
              )}

              {/* Queue Tab */}
              {tab === 'queue' && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold text-slate-900">Your Daily Challenge Queue</h2>
                    <Button onClick={refreshQueue} variant="outline">
                      🔄 Refresh Queue
                    </Button>
                  </div>

                  {queue.length === 0 ? (
                    <Card className="bg-white p-8 text-center">
                      <div className="text-4xl mb-4">📋</div>
                      <h3 className="text-xl font-semibold text-slate-900 mb-2">Queue is Empty</h3>
                      <p className="text-slate-600 mb-4">Generate recommendations first to populate your queue</p>
                      <Button onClick={generateRecommendations}>Generate Recommendations</Button>
                    </Card>
                  ) : (
                    queue.map((item) => (
                      <Card key={item.challenge_id} className="bg-white p-6 border border-slate-200">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-lg">
                              {item.position}
                            </div>
                            <div>
                              <div className="font-semibold text-slate-900">Challenge #{item.challenge_id}</div>
                              <div className="text-sm text-slate-600">Position {item.position} in queue</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-slate-900">{(item.score * 100).toFixed(0)}%</div>
                            <div className="text-xs text-slate-500">Match Score</div>
                          </div>
                        </div>
                      </Card>
                    ))
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}
