import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { apiCall } from '@/lib/api';

interface Hint {
  id: number;
  challengeId: number;
  type: string;
  title: string;
  content: string;
  explanation?: string;
  difficulty: string;
  hasCodeExample: boolean;
  codeExample?: string;
  codeLanguage: string;
  resourceLinks: Array<{ title: string; url: string }>;
  quality: string;
  isPremiumOnly: boolean;
  timesShown: number;
  timesHelpful: number;
  helpfulScore: number;
  generatedAt: string;
}

interface Quota {
  hintsRequestedToday: number;
  hintsQuotaPerDay: number;
  remainingToday: number;
  hintsRequestedThisMonth: number;
  hintsQuotaPerMonth: number;
  remainingThisMonth: number;
  isUnlimited: boolean;
  dailyResetAt: string;
}

interface HintUsage {
  id: number;
  hintId: number;
  challengeId: number;
  viewedAt: string;
  timeOnHintSeconds: number;
  challengeSolvedAfter: boolean | null;
  timeToSolveMinutes: number | null;
  userTierAtTime: string;
}

const HintsPage: React.FC = () => {
  const router = useRouter();
  const { challengeId } = router.query;

  const [hints, setHints] = useState<Hint[]>([]);
  const [quota, setQuota] = useState<Quota | null>(null);
  const [selectedHint, setSelectedHint] = useState<Hint | null>(null);
  const [ratings, setRatings] = useState<{ [key: number]: boolean }>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [hintHistory, setHintHistory] = useState<HintUsage[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // Fetch hints for challenge
  const fetchHints = async () => {
    if (!challengeId) return;
    
    try {
      setLoading(true);
      const data = await apiCall(`/api/v1x/hints/challenge/${challengeId}`, {
        method: 'GET',
      });
      
      if (data.hints) {
        setHints(data.hints);
      }
    } catch (err) {
      setError('Failed to load hints');
    } finally {
      setLoading(false);
    }
  };

  // Fetch user quota
  const fetchQuota = async () => {
    try {
      const data = await apiCall('/api/v1x/hints/quota', {
        method: 'GET',
      });
      
      if (data.quota) {
        setQuota(data.quota);
      }
    } catch (err) {
      console.error('Failed to fetch quota:', err);
    }
  };

  // Fetch hint history
  const fetchHistory = async () => {
    try {
      const data = await apiCall('/api/v1x/hints/history', {
        method: 'GET',
      });
      
      if (data.history) {
        setHintHistory(data.history);
      }
    } catch (err) {
      console.error('Failed to fetch history:', err);
    }
  };

  useEffect(() => {
    fetchHints();
    fetchQuota();
  }, [challengeId]);

  // Request a hint
  const requestHint = async () => {
    if (!challengeId) return;

    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      const data = await apiCall(`/api/v1x/hints/request/${challengeId}`, {
        method: 'POST',
      });

      if (data.hint) {
        setSelectedHint(data.hint);
        setSuccess('Hint loaded successfully!');
        
        // Update quota
        if (quota) {
          setQuota({
            ...quota,
            remainingToday: data.quotaRemaining,
            hintsRequestedToday: quota.hintsRequestedToday + 1,
          });
        }

        // Refresh history
        fetchHistory();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to request hint');
    } finally {
      setLoading(false);
    }
  };

  // Rate hint
  const rateHint = async (isHelpful: boolean) => {
    if (!selectedHint) return;

    try {
      setLoading(true);
      const data = await apiCall(`/api/v1x/hints/rate/${selectedHint.id}`, {
        method: 'POST',
        body: JSON.stringify({
          is_helpful: isHelpful,
          rating: ratings[selectedHint.id] || 3,
        }),
      });

      setSuccess(`Thank you! Your feedback helps improve hints.`);
      setRatings({ ...ratings, [selectedHint.id]: isHelpful });
    } catch (err: any) {
      setError('Failed to save rating');
    } finally {
      setLoading(false);
    }
  };

  // Format difficulty badge color
  const getDifficultyColor = (difficulty: string) => {
    const colors: { [key: string]: string } = {
      very_easy: 'bg-green-100 text-green-800',
      easy: 'bg-green-100 text-green-800',
      moderate: 'bg-yellow-100 text-yellow-800',
      hard: 'bg-orange-100 text-orange-800',
      very_hard: 'bg-red-100 text-red-800',
    };
    return colors[difficulty] || 'bg-gray-100 text-gray-800';
  };

  // Format type badge
  const getTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      concept_explanation: 'bg-blue-100 text-blue-800',
      approach_suggestion: 'bg-purple-100 text-purple-800',
      step_by_step: 'bg-indigo-100 text-indigo-800',
      common_mistakes: 'bg-red-100 text-red-800',
      edge_cases: 'bg-orange-100 text-orange-800',
      code_pattern: 'bg-green-100 text-green-800',
      debugging_hint: 'bg-pink-100 text-pink-800',
      optimization_hint: 'bg-cyan-100 text-cyan-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">AI Hints</h1>
          <p className="text-gray-600">Get intelligent hints to help solve coding challenges</p>
        </div>

        {/* Quota Status */}
        {quota && (
          <Card className="mb-8">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm text-gray-600 mb-1">Daily Hints Remaining</p>
                <p className="text-2xl font-bold text-blue-600">
                  {quota.remainingToday} / {quota.hintsQuotaPerDay}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Monthly Usage</p>
                <p className="text-lg font-semibold text-gray-800">
                  {quota.hintsRequestedThisMonth} / {quota.hintsQuotaPerMonth}
                </p>
              </div>
              {quota.isUnlimited && (
                <div className="bg-purple-100 text-purple-800 px-4 py-2 rounded-lg font-semibold">
                  Premium: Unlimited
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Available Hints */}
        {!selectedHint && hints.length > 0 && (
          <Card className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Available Hints</h2>
            <div className="space-y-4">
              {hints.map((hint) => (
                <div
                  key={hint.id}
                  className="border-l-4 border-blue-500 pl-4 py-3 cursor-pointer hover:bg-gray-50 transition rounded"
                  onClick={() => setSelectedHint(hint)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-lg text-gray-800">{hint.title}</h3>
                    <div className="flex gap-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getTypeColor(hint.type)}`}>
                        {hint.type.replace(/_/g, ' ')}
                      </span>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getDifficultyColor(hint.difficulty)}`}>
                        {hint.difficulty.replace(/_/g, ' ')}
                      </span>
                    </div>
                  </div>
                  <p className="text-gray-600 text-sm mb-2 line-clamp-2">{hint.content}</p>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex gap-4">
                      <span>👁️ {hint.timesShown} viewed</span>
                      <span>👍 {hint.timesHelpful} helpful</span>
                      <span>⭐ {(hint.helpfulScore * 100).toFixed(0)}% helpful</span>
                    </div>
                    {hint.isPremiumOnly && <span className="text-yellow-600 font-semibold">Premium Only</span>}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Request Hint Button */}
        {!selectedHint && !loading && (
          <Card className="mb-8 text-center">
            <Button
              onClick={requestHint}
              disabled={!challengeId || (quota && quota.remainingToday === 0)}
            >
              {quota?.remainingToday === 0 ? 'Daily quota exceeded' : 'Request AI Hint'}
            </Button>
            {hints.length === 0 && (
              <p className="text-gray-500 mt-4">No hints available yet. Request one to get started!</p>
            )}
          </Card>
        )}

        {/* Selected Hint Display */}
        {selectedHint && (
          <Card className="mb-8">
            <div className="mb-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-3xl font-bold mb-2">{selectedHint.title}</h2>
                  <div className="flex gap-2 flex-wrap">
                    <span className={`px-3 py-1 text-sm font-medium rounded ${getTypeColor(selectedHint.type)}`}>
                      {selectedHint.type.replace(/_/g, ' ')}
                    </span>
                    <span className={`px-3 py-1 text-sm font-medium rounded ${getDifficultyColor(selectedHint.difficulty)}`}>
                      Difficulty: {selectedHint.difficulty.replace(/_/g, ' ')}
                    </span>
                    {selectedHint.isPremiumOnly && (
                      <span className="px-3 py-1 text-sm font-medium rounded bg-yellow-100 text-yellow-800">
                        Premium
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => setSelectedHint(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ✕
                </button>
              </div>

              {/* Hint Content */}
              <div className="bg-gray-50 p-6 rounded-lg mb-6">
                <p className="text-gray-800 text-lg leading-relaxed">{selectedHint.content}</p>
              </div>

              {/* Explanation */}
              {selectedHint.explanation && (
                <div className="mb-6">
                  <h3 className="font-semibold text-lg mb-2 text-gray-800">Why This Helps</h3>
                  <p className="text-gray-700">{selectedHint.explanation}</p>
                </div>
              )}

              {/* Code Example */}
              {selectedHint.codeExample && (
                <div className="mb-6">
                  <h3 className="font-semibold text-lg mb-2 text-gray-800">Code Example</h3>
                  <pre className="bg-gray-800 text-gray-100 p-4 rounded-lg overflow-x-auto">
                    <code>{selectedHint.codeExample}</code>
                  </pre>
                  <p className="text-sm text-gray-500 mt-2">Language: {selectedHint.codeLanguage}</p>
                </div>
              )}

              {/* Resource Links */}
              {selectedHint.resourceLinks && selectedHint.resourceLinks.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-lg mb-2 text-gray-800">Related Resources</h3>
                  <ul className="space-y-2">
                    {selectedHint.resourceLinks.map((link, idx) => (
                      <li key={idx}>
                        <a
                          href={link.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          {link.title} →
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Hint Stats */}
              <div className="border-t pt-6">
                <p className="text-sm text-gray-600 mb-4">
                  Was this hint helpful?
                </p>
                <div className="flex gap-4">
                  <Button
                    onClick={() => rateHint(true)}
                    disabled={loading}
                    className={ratings[selectedHint.id] === true ? 'bg-green-600 text-white' : ''}
                  >
                    👍 Helpful
                  </Button>
                  <Button
                    onClick={() => rateHint(false)}
                    disabled={loading}
                    className={ratings[selectedHint.id] === false ? 'bg-red-600 text-white' : ''}
                  >
                    👎 Not Helpful
                  </Button>
                </div>
                <div className="mt-4 text-sm text-gray-500">
                  <p>✓ {selectedHint.timesHelpful} found this helpful</p>
                  <p>✗ {selectedHint.timesUnhelpful} found this not helpful</p>
                </div>
              </div>
            </div>

            <div className="border-t pt-6 flex gap-4">
              <Button
                onClick={() => setSelectedHint(null)}
                className="flex-1 bg-gray-200 text-gray-800 hover:bg-gray-300"
              >
                Go Back
              </Button>
              {challengeId && (
                <Button
                  onClick={() => router.push(`/paths/${challengeId}`)}
                  className="flex-1"
                >
                  Return to Challenge
                </Button>
              )}
            </div>
          </Card>
        )}

        {/* History Section */}
        <Card className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Your Hint History</h2>
            <Button
              onClick={() => {
                setShowHistory(!showHistory);
                if (!showHistory) fetchHistory();
              }}
              className="bg-gray-200 text-gray-800"
            >
              {showHistory ? 'Hide' : 'Show'} History
            </Button>
          </div>

          {showHistory && (
            <div>
              {hintHistory.length > 0 ? (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {hintHistory.map((usage) => (
                    <div key={usage.id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <div>
                        <p className="font-semibold">Hint #{usage.hintId}</p>
                        <p className="text-sm text-gray-500">
                          Challenge #{usage.challengeId}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-600">
                          {new Date(usage.viewedAt).toLocaleDateString()}
                        </p>
                        {usage.challengeSolvedAfter && (
                          <p className="text-sm text-green-600 font-semibold">✓ Solved</p>
                        )}
                        {usage.challengeSolvedAfter === false && (
                          <p className="text-sm text-red-600">Not yet solved</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No hint history yet</p>
              )}
            </div>
          )}
        </Card>

        {/* Messages */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default HintsPage;
