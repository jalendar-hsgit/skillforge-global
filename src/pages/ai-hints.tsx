import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import SectionHeading from '@/components/SectionHeading';
import Card from '@/components/Card';
import { Lightbulb, BookOpen, Code, ExternalLink, ThumbsUp, ThumbsDown, Zap, TrendingUp } from 'lucide-react';

interface Hint {
  id: number;
  challenge_id: number;
  hint_type: string;
  title: string;
  content: string;
  explanation?: string;
  target_difficulty: string;
  code_example?: string;
  code_language: string;
  quality: string;
  is_premium_only: boolean;
  cost_coins: number;
  times_shown?: number;
  times_helpful?: number;
  helpful_score?: number;
  resource_links: string[];
}

interface HintQuota {
  id: number;
  hints_requested_today: number;
  hints_quota_per_day: number;
  remaining_today: number;
  hints_requested_this_month: number;
  hints_quota_per_month: number;
  remaining_this_month: number;
  is_unlimited: boolean;
}

const HintIcon = ({ type }: { type: string }) => {
  const icons: Record<string, string> = {
    EXPLANATION: '📚',
    APPROACH: '📈',
    CODE: '💻',
    OPTIMIZATION: '⚡',
    debugging_hint: '🐛',
  };
  return <span>{icons[type] || '💡'}</span>;
};

export default function AIHintsPage() {
  const router = useRouter();
  const [hints, setHints] = useState<Hint[]>([]);
  const [quota, setQuota] = useState<HintQuota | null>(null);
  const [history, setHistory] = useState<HintUsage[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedHint, setSelectedHint] = useState<Hint | null>(null);
  const [activeTab, setActiveTab] = useState<'available' | 'history'>('available');
  const [hintRatings, setHintRatings] = useState<Record<number, number>>({});
  const [showRatingForm, setShowRatingForm] = useState<number | null>(null);

  useEffect(() => {
    fetchQuota();
    fetchHistory();
  }, []);

  const fetchQuota = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1x/hints/quota`, {
        credentials: 'include',
      });
      if (res.ok) {
        const data = await res.json();
        setQuota(data.quota);
      }
    } catch (error) {
      console.error('Failed to fetch quota:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1x/hints/history?limit=20`, {
        credentials: 'include',
      });
      if (res.ok) {
        const data = await res.json();
        setHistory(data.history || []);
      }
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

  const requestHint = async (challengeId: number, hintType?: string) => {
    try {
      let url = `${API_BASE}/api/v1x/hints/request/${challengeId}`;
      if (hintType) {
        url += `?hint_type=${hintType}`;
      }

      const res = await fetch(url, {
        method: 'POST',
        credentials: 'include',
      });

      if (res.ok) {
        const data = await res.json();
        setSelectedHint(data.hint);
        setHints([data.hint]);
        fetchQuota();
      } else {
        const error = await res.json();
        alert(error.detail || 'Failed to get hint');
      }
    } catch (error) {
      console.error('Failed to request hint:', error);
      alert('Error requesting hint');
    }
  };

  const rateHint = async (hintId: number, isHelpful: boolean, rating: number) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1x/hints/rate/${hintId}`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          is_helpful: isHelpful,
          rating: rating,
        }),
      });

      if (res.ok) {
        setHintRatings((prev) => ({ ...prev, [hintId]: rating }));
        setShowRatingForm(null);
        alert('Thank you for your feedback!');
      }
    } catch (error) {
      console.error('Failed to rate hint:', error);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors: Record<string, string> = {
      very_easy: 'text-green-400',
      easy: 'text-green-500',
      moderate: 'text-yellow-500',
      hard: 'text-orange-500',
      very_hard: 'text-red-500',
    };
    return colors[difficulty] || 'text-gray-400';
  };

  const getQualityBadge = (quality: string) => {
    const colors: Record<string, string> = {
      excellent: 'bg-gradient-to-r from-green-600 to-emerald-600',
      good: 'bg-gradient-to-r from-blue-600 to-cyan-600',
      fair: 'bg-gradient-to-r from-yellow-600 to-orange-600',
      poor: 'bg-gradient-to-r from-red-600 to-pink-600',
    };
    return colors[quality] || 'bg-gradient-to-r from-gray-600 to-slate-600';
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black py-12">
          <div className="max-w-6xl mx-auto px-4 text-center">
            <p className="text-gray-400">Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black py-12">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="mb-12">
            <SectionHeading>AI Hints Assistant</SectionHeading>
            <p className="text-gray-400 text-lg max-w-2xl">
              Get intelligent hints for coding challenges. Our AI provides targeted guidance based on your learning style and progress.
            </p>
          </div>

          {/* Quota Status */}
          {quota && (
            <Card className="mb-8 bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30">
              <div className="p-6">
                <h3 className="text-xl font-bold mb-4 text-blue-300">Daily Quota Status</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <p className="text-gray-400 text-sm mb-2">Today's Hints</p>
                    <div className="flex items-end gap-2">
                      <span className="text-3xl font-bold text-blue-400">
                        {quota.remainingToday}
                      </span>
                      <span className="text-gray-500 mb-1">/ {quota.hintsQuotaPerDay}</span>
                    </div>
                    <div className="w-full bg-gray-800 rounded-full h-2 mt-3">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-blue-400 h-2 rounded-full"
                        style={{
                          width: `${((quota.hintsQuotaPerDay - quota.remainingToday) / quota.hintsQuotaPerDay) * 100}%`,
                        }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <p className="text-gray-400 text-sm mb-2">Monthly Hints</p>
                    <div className="flex items-end gap-2">
                      <span className="text-3xl font-bold text-purple-400">
                        {quota.remainingThisMonth}
                      </span>
                      <span className="text-gray-500 mb-1">/ {quota.hintsQuotaPerMonth}</span>
                    </div>
                  </div>

                  {quota.isUnlimited && (
                    <div className="bg-gradient-to-r from-yellow-600/30 to-orange-600/30 rounded-lg p-4 border border-yellow-500/30">
                      <p className="text-yellow-300 font-semibold">🌟 Unlimited Access</p>
                      <p className="text-gray-400 text-sm">Premium member benefit</p>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          )}

          {/* Tabs */}
          <div className="flex gap-4 mb-8 border-b border-gray-700">
            <button
              onClick={() => setActiveTab('available')}
              className={`px-4 py-3 font-semibold border-b-2 transition-all ${
                activeTab === 'available'
                  ? 'text-blue-400 border-blue-400'
                  : 'text-gray-400 border-transparent hover:text-gray-300'
              }`}
            >
              How to Request Hints
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`px-4 py-3 font-semibold border-b-2 transition-all ${
                activeTab === 'history'
                  ? 'text-blue-400 border-blue-400'
                  : 'text-gray-400 border-transparent hover:text-gray-300'
              }`}
            >
              Your Hint History ({history.length})
            </button>
          </div>

          {/* Available Hints Tab */}
          {activeTab === 'available' && (
            <Card className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 border border-gray-700">
              <div className="p-8">
                <h3 className="text-2xl font-bold mb-6 text-white">
                  Request AI Hints for Your Challenges
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                  <div className="bg-gray-900/50 rounded-lg p-6 border border-gray-700">
                    <h4 className="text-lg font-semibold text-gray-200 mb-3 flex items-center gap-2">
                      💡 How It Works
                    </h4>
                    <ul className="space-y-3 text-gray-400 text-sm">
                      <li className="flex gap-2">
                        <span className="text-blue-400 font-bold">1.</span>
                        <span>Navigate to any coding challenge</span>
                      </li>
                      <li className="flex gap-2">
                        <span className="text-blue-400 font-bold">2.</span>
                        <span>Click "Get Hint" to request AI assistance</span>
                      </li>
                      <li className="flex gap-2">
                        <span className="text-blue-400 font-bold">3.</span>
                        <span>Review the hint and try solving independently</span>
                      </li>
                      <li className="flex gap-2">
                        <span className="text-blue-400 font-bold">4.</span>
                        <span>Rate the hint's helpfulness</span>
                      </li>
                    </ul>
                  </div>

                  <div className="bg-gray-900/50 rounded-lg p-6 border border-gray-700">
                    <h4 className="text-lg font-semibold text-gray-200 mb-3 flex items-center gap-2">
                      🎯 Hint Types Available
                    </h4>
                    <ul className="space-y-2 text-gray-400 text-sm">
                      <li className="flex items-center gap-2">
                        <HintIcon type="concept_explanation" />
                        Concept Explanations
                      </li>
                      <li className="flex items-center gap-2">
                        <HintIcon type="approach_suggestion" />
                        Approach Suggestions
                      </li>
                      <li className="flex items-center gap-2">
                        <HintIcon type="common_mistakes" />
                        Common Mistakes to Avoid
                      </li>
                      <li className="flex items-center gap-2">
                        <HintIcon type="step_by_step" />
                        Step-by-Step Guidance
                      </li>
                      <li className="flex items-center gap-2">
                        <HintIcon type="code_pattern" />
                        Code Patterns & Examples
                      </li>
                      <li className="flex items-center gap-2">
                        <HintIcon type="debugging_hint" />
                        Debugging Techniques
                      </li>
                    </ul>
                  </div>
                </div>

                {selectedHint && (
                  <Card className="bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-purple-500/30 mb-8">
                    <div className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <HintIcon type={selectedHint.type} />
                          <div>
                            <h4 className="text-xl font-bold text-white">{selectedHint.title}</h4>
                            <p className="text-gray-400 text-sm">Type: {selectedHint.type.replace(/_/g, ' ')}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`text-xs font-semibold ${getDifficultyColor(selectedHint.difficulty)}`}>
                            {selectedHint.difficulty.replace(/_/g, ' ').toUpperCase()}
                          </span>
                          <span className={`px-2 py-1 rounded text-xs font-semibold text-white ${getQualityBadge(selectedHint.quality)}`}>
                            {selectedHint.quality.toUpperCase()}
                          </span>
                        </div>
                      </div>

                      <div className="bg-gray-900/50 rounded-lg p-4 mb-4 border border-gray-700">
                        <p className="text-gray-300 leading-relaxed">{selectedHint.content}</p>
                      </div>

                      {selectedHint.explanation && (
                        <div className="mb-4 pb-4 border-b border-gray-700">
                          <p className="text-gray-400 text-sm mb-2 font-semibold">Why This Helps:</p>
                          <p className="text-gray-400">{selectedHint.explanation}</p>
                        </div>
                      )}

                      {selectedHint.hasCodeExample && selectedHint.codeExample && (
                        <div className="mb-4">
                          <p className="text-gray-400 text-sm mb-2 font-semibold">Code Example ({selectedHint.codeLanguage}):</p>
                          <pre className="bg-black/50 rounded-lg p-4 overflow-x-auto text-sm text-gray-300 border border-gray-700">
                            <code>{selectedHint.codeExample}</code>
                          </pre>
                        </div>
                      )}

                      {/* Rating Section */}
                      <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700">
                        <p className="text-gray-300 font-semibold mb-3">Was this hint helpful?</p>
                        {showRatingForm === selectedHint.id ? (
                          <div className="space-y-3">
                            <div className="flex gap-2">
                              {[1, 2, 3, 4, 5].map((rating) => (
                                <button
                                  key={rating}
                                  onClick={() => rateHint(selectedHint.id, rating >= 4, rating)}
                                  className={`px-3 py-1 rounded font-semibold transition-all ${
                                    hintRatings[selectedHint.id] === rating
                                      ? 'bg-blue-600 text-white'
                                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                  }`}
                                >
                                  {'⭐'.repeat(rating)}
                                </button>
                              ))}
                            </div>
                            <button
                              onClick={() => setShowRatingForm(null)}
                              className="text-gray-400 text-sm hover:text-gray-300"
                            >
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <div className="flex gap-2">
                            <Button
                              variant="secondary"
                              onClick={() => setShowRatingForm(selectedHint.id)}
                              className="flex-1"
                            >
                              Rate This Hint
                            </Button>
                            {selectedHint.helpfulScore && (
                              <div className="flex items-center gap-2 px-4 text-sm text-gray-400">
                                <span>Helpful Score:</span>
                                <span className="font-bold text-blue-400">
                                  {(selectedHint.helpfulScore * 100).toFixed(0)}%
                                </span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </Card>
                )}

                <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-6">
                  <h4 className="text-lg font-semibold text-blue-300 mb-4">💻 Ready to Practice?</h4>
                  <p className="text-gray-300 mb-4">
                    Go to any coding challenge and click the hint button to get started. Our AI will provide personalized guidance based on your skill level and learning progress.
                  </p>
                  <Button variant="primary" onClick={() => router.push('/paths')}>
                    Browse Challenges →
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* History Tab */}
          {activeTab === 'history' && (
            <Card className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 border border-gray-700">
              <div className="p-8">
                <h3 className="text-2xl font-bold mb-6 text-white">
                  Your Hint History
                </h3>

                {history.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-gray-400 mb-4">No hints viewed yet</p>
                    <p className="text-gray-500 text-sm">
                      Start by requesting hints for coding challenges to see your history here.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {history.map((usage) => (
                      <div
                        key={usage.id}
                        className="bg-gray-900/50 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-all"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="text-gray-300 font-semibold">
                              Challenge #{usage.challengeId}
                            </p>
                            <p className="text-gray-500 text-sm">
                              Viewed: {new Date(usage.viewedAt).toLocaleString()}
                            </p>
                            <div className="flex gap-4 mt-2 text-sm">
                              <span className="text-gray-400">
                                ⏱️ {usage.timeOnHintSeconds}s on hint
                              </span>
                              {usage.challengeSolvedAfter !== undefined && (
                                <span className={usage.challengeSolvedAfter ? 'text-green-400' : 'text-orange-400'}>
                                  {usage.challengeSolvedAfter ? '✅ Solved' : '⏳ In Progress'}
                                </span>
                              )}
                              {usage.timeToSolveMinutes && (
                                <span className="text-gray-400">
                                  ⏲️ Solved in {usage.timeToSolveMinutes}m
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  );
}
