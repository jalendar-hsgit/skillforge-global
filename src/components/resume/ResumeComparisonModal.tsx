import { useState, useEffect } from 'react';
import { X, GitCompare, TrendingUp, TrendingDown, Minus, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/Button';
import { API_BASE } from '@/lib/apiBase';

interface Version {
  id: number;
  version_number: number;
  version_name: string;
  ats_score: number;
  word_count: number;
  skill_count: number;
  created_at: string;
  applications_sent: number;
  responses_received: number;
  interviews_secured: number;
}

interface ComparisonResult {
  differences: {
    added: Array<{ section: string; count?: number; items?: string[] }>;
    removed: Array<{ section: string; count?: number; items?: string[] }>;
    modified: Array<{ section: string; field: string; old_value: string; new_value: string }>;
  };
  score_change: number;
  metrics_change: {
    word_count_change: number;
    skill_count_change: number;
    ats_score_change: number;
  };
  recommendations: string[];
  better_version: string;
}

interface ScoreHistoryItem {
  version_id: number;
  version_name?: string;
  ats_score?: number;
  created_at: string;
}

interface ResumeComparisonModalProps {
  resumeId: number;
  isOpen: boolean;
  onClose: () => void;
  initialBaseVersionId?: number | null;
  initialComparedVersionId?: number | null;
}

export default function ResumeComparisonModal({ resumeId, isOpen, onClose, initialBaseVersionId = null, initialComparedVersionId = null }: ResumeComparisonModalProps) {
  const [versions, setVersions] = useState<Version[]>([]);
  const [selectedBase, setSelectedBase] = useState<number | null>(null);
  const [selectedCompared, setSelectedCompared] = useState<number | null>(null);
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scoreHistory, setScoreHistory] = useState<ScoreHistoryItem[]>([]);

  useEffect(() => {
    if (isOpen) {
      fetchVersions();
      fetchScoreHistory();
    }
  }, [isOpen, resumeId]);

  // Apply initial preselected versions when provided
  useEffect(() => {
    if (isOpen) {
      if (initialBaseVersionId) setSelectedBase(initialBaseVersionId);
      if (initialComparedVersionId) setSelectedCompared(initialComparedVersionId);
    }
  }, [isOpen, initialBaseVersionId, initialComparedVersionId]);

  const fetchVersions = async () => {
    try {
      const response = await fetch(`/api/session/v1x/resume-comparison/versions/${resumeId}`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        let detail = '';
        try {
          const ct = response.headers.get('content-type') || '';
          if (ct.includes('application/json')) {
            const j = await response.json();
            detail = (j && (j.detail || j.message)) ? `: ${j.detail || j.message}` : '';
          } else {
            const t = await response.text();
            detail = t ? `: ${t}` : '';
          }
        } catch (_) {}
        throw new Error(`Failed to load versions (${response.status})${detail}`);
      }
      
      const data = await response.json();
      setVersions(data);
      
      // Auto-select latest two versions if available and not preselected
      if (!initialBaseVersionId && !initialComparedVersionId) {
        if (data.length >= 2) {
          setSelectedBase(data[1].id);
          setSelectedCompared(data[0].id);
        } else if (data.length === 1) {
          setSelectedCompared(data[0].id);
        }
      }
    } catch (err: any) {
      console.error('Error fetching versions:', err);
      setError(err?.message || 'Failed to load versions');
    }
  };

  const fetchScoreHistory = async () => {
    try {
      const r = await fetch(`/api/session/v1x/resume-comparison/score-history/${resumeId}`, { credentials: 'include' });
      if (!r.ok) return; // optional; do not block UI on this
      const data = await r.json();
      setScoreHistory(Array.isArray(data) ? data : []);
    } catch (_) {
      // ignore errors for optional chart
    }
  };

  const handleCompare = async () => {
    if (!selectedBase || !selectedCompared) {
      setError('Please select two versions to compare');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/session/v1x/resume-comparison/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          base_version_id: selectedBase,
          compared_version_id: selectedCompared
        })
      });
      if (!response.ok) {
        let detail = '';
        try {
          const ct = response.headers.get('content-type') || '';
          if (ct.includes('application/json')) {
            const j = await response.json();
            detail = (j && (j.detail || j.message)) ? `: ${j.detail || j.message}` : '';
          } else {
            const t = await response.text();
            detail = t ? `: ${t}` : '';
          }
        } catch (_) {}
        throw new Error(`Failed to compare versions (${response.status})${detail}`);
      }

      const data = await response.json();
      setComparison(data);
    } catch (err: any) {
      console.error('Error comparing versions:', err);
      setError(err?.message || 'Failed to compare versions');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTrendIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="w-4 h-4 text-green-600" />;
    if (change < 0) return <TrendingDown className="w-4 h-4 text-red-600" />;
    return <Minus className="w-4 h-4 text-gray-400" />;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-fade-in">
      <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden border border-gray-200 animate-scale-in">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 px-6 py-5 flex items-center justify-between z-10 shadow-lg">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center shadow-glass">
              <GitCompare className="w-7 h-7 text-white drop-shadow-lg" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight drop-shadow-md">Resume Comparison</h2>
              <p className="text-sm text-white/90 font-medium">Compare versions to track improvements</p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            className="text-white/80 hover:text-white transition-all duration-200 hover:bg-white/20 rounded-lg p-2"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <div className="overflow-y-auto max-h-[calc(90vh-88px)]">

        <div className="p-6 space-y-6">
          {error && (
            <div className="mb-4 p-4 bg-gradient-to-r from-red-50 to-red-100 border-l-4 border-red-500 rounded-xl text-red-800 shadow-sm animate-slide-down">
              <p className="font-semibold">{error}</p>
            </div>
          )}

          {/* Version Selection */}
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div className="space-y-2">
              <label className="block text-sm font-bold text-gray-700 uppercase tracking-wide">
                Base Version (Older)
              </label>
              <select
                value={selectedBase || ''}
                onChange={(e) => setSelectedBase(Number(e.target.value))}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 font-medium text-gray-900"
              >
                <option value="" className="text-gray-500">Select version...</option>
                {versions.map((v) => (
                  <option key={v.id} value={v.id} className="font-medium">
                    {v.version_name} (v{v.version_number}) - ATS: {v.ats_score?.toFixed(0) || 'N/A'}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-bold text-gray-700 uppercase tracking-wide">
                Compared Version (Newer)
              </label>
              <select
                value={selectedCompared || ''}
                onChange={(e) => setSelectedCompared(Number(e.target.value))}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl bg-white shadow-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 font-medium text-gray-900"
              >
                <option value="" className="text-gray-500">Select version...</option>
                {versions.map((v) => (
                  <option key={v.id} value={v.id} className="font-medium">
                    {v.version_name} (v{v.version_number}) - ATS: {v.ats_score?.toFixed(0) || 'N/A'}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <Button
            onClick={handleCompare}
            disabled={!selectedBase || !selectedCompared || loading}
            className="w-full mb-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="animate-spin">⏳</span>
                Analyzing Differences...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <GitCompare className="w-5 h-5" />
                Compare Versions
              </span>
            )}
          </Button>

          {/* Comparison Results */}
          {comparison && (
            <div className="space-y-6">
              {/* Score Changes */}
              <div className="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 rounded-2xl p-6 shadow-lg border border-purple-200 animate-slide-up">
                <h3 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-4">
                  Performance Metrics
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-white rounded-xl p-5 shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-100">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-semibold text-gray-600 uppercase tracking-wide">ATS Score</span>
                      <div className="p-1.5 bg-gray-50 rounded-lg">
                        {getTrendIcon(comparison.metrics_change.ats_score_change)}
                      </div>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className={`text-3xl font-black ${getScoreColor(comparison.score_change)}`}>
                        {comparison.score_change > 0 ? '+' : ''}
                        {comparison.score_change.toFixed(1)}
                      </span>
                      <span className="text-sm font-medium text-gray-500">points</span>
                    </div>
                  </div>

                  <div className="bg-white rounded-xl p-5 shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-100">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Word Count</span>
                      <div className="p-1.5 bg-gray-50 rounded-lg">
                        {getTrendIcon(comparison.metrics_change.word_count_change)}
                      </div>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className={`text-3xl font-black ${
                        comparison.metrics_change.word_count_change > 0 ? 'text-green-600' :
                        comparison.metrics_change.word_count_change < 0 ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        {comparison.metrics_change.word_count_change > 0 ? '+' : ''}
                        {comparison.metrics_change.word_count_change}
                      </span>
                      <span className="text-sm font-medium text-gray-500">words</span>
                    </div>
                  </div>

                  <div className="bg-white rounded-xl p-5 shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-100">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Skills</span>
                      <div className="p-1.5 bg-gray-50 rounded-lg">
                        {getTrendIcon(comparison.metrics_change.skill_count_change)}
                      </div>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className={`text-3xl font-black ${
                        comparison.metrics_change.skill_count_change > 0 ? 'text-green-600' :
                        comparison.metrics_change.skill_count_change < 0 ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        {comparison.metrics_change.skill_count_change > 0 ? '+' : ''}
                        {comparison.metrics_change.skill_count_change}
                      </span>
                      <span className="text-sm font-medium text-gray-500">skills</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Score History (optional) */}
              {scoreHistory.length > 0 && (
                <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 animate-slide-up" style={{ animationDelay: '0.05s', animationFillMode: 'backwards' }}>
                  <h3 className="text-lg font-bold text-gray-900 mb-3">ATS Score History</h3>
                  <div className="h-32">
                    {(() => {
                      // Simple responsive sparkline
                      const w = 600; const h = 120; const pad = 16;
                      const points = scoreHistory.map((p) => ({
                        x: new Date(p.created_at).getTime(),
                        y: typeof p.ats_score === 'number' ? p.ats_score : null,
                      })).filter(p => p.y !== null) as {x:number;y:number}[];
                      if (points.length < 2) return <p className="text-sm text-gray-500">Not enough data</p>;
                      const xs = points.map(p=>p.x); const ys = points.map(p=>p.y);
                      const xMin = Math.min(...xs), xMax = Math.max(...xs);
                      const yMin = Math.min(...ys), yMax = Math.max(...ys);
                      const xScale = (x:number)=> pad + (w - 2*pad) * ((x - xMin) / Math.max(1, (xMax - xMin)));
                      const yScale = (y:number)=> h - pad - (h - 2*pad) * ((y - yMin) / Math.max(1, (yMax - yMin)));
                      const d = points.map((p,i)=> `${i===0?'M':'L'} ${xScale(p.x).toFixed(1)} ${yScale(p.y).toFixed(1)}`).join(' ');
                      return (
                        <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-full">
                          <defs>
                            <linearGradient id="gradLine" x1="0" x2="0" y1="0" y2="1">
                              <stop offset="0%" stopColor="#4f46e5"/>
                              <stop offset="100%" stopColor="#a855f7"/>
                            </linearGradient>
                          </defs>
                          <rect x="0" y="0" width={w} height={h} fill="#fafafa"/>
                          <path d={d} fill="none" stroke="url(#gradLine)" strokeWidth="3" strokeLinejoin="round" strokeLinecap="round" />
                        </svg>
                      );
                    })()}
                  </div>
                </div>
              )}

              {/* Differences */}
              <div className="animate-slide-up" style={{ animationDelay: '0.1s', animationFillMode: 'backwards' }}>
                <h3 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-4">
                  Content Changes
                </h3>
                <div className="space-y-4">
                  {comparison.differences.added.map((item, idx) => (
                    <div key={`added-${idx}`} className="flex items-start gap-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex-shrink-0 p-2 bg-green-100 rounded-lg">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-bold text-green-900 mb-1">Added to {item.section}</p>
                        {item.count && <p className="text-sm font-semibold text-green-700 mb-2">{item.count} items</p>}
                        {item.items && (
                          <ul className="mt-2 space-y-1 text-sm text-green-700">
                            {item.items.map((i, iidx) => (
                              <li key={iidx} className="flex items-start gap-2">
                                <span className="text-green-500 mt-1">•</span>
                                <span className="leading-relaxed">{i}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    </div>
                  ))}

                  {comparison.differences.removed.map((item, idx) => (
                    <div key={`removed-${idx}`} className="flex items-start gap-4 p-4 bg-gradient-to-r from-red-50 to-rose-50 border-l-4 border-red-500 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex-shrink-0 p-2 bg-red-100 rounded-lg">
                        <XCircle className="w-5 h-5 text-red-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-bold text-red-900 mb-1">Removed from {item.section}</p>
                        {item.count && <p className="text-sm font-semibold text-red-700 mb-2">{item.count} items</p>}
                        {item.items && (
                          <ul className="mt-2 space-y-1 text-sm text-red-700">
                            {item.items.map((i, iidx) => (
                              <li key={iidx} className="flex items-start gap-2 opacity-75">
                                <span className="text-red-500 mt-1">•</span>
                                <span className="leading-relaxed line-through">{i}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    </div>
                  ))}

                  {comparison.differences.modified.map((item, idx) => (
                    <div key={`modified-${idx}`} className="flex items-start gap-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex-shrink-0 p-2 bg-blue-100 rounded-lg">
                        <AlertCircle className="w-5 h-5 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-bold text-blue-900 mb-3">Modified {item.field}</p>
                        <div className="space-y-2">
                          <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                            <span className="text-xs font-bold text-red-600 uppercase tracking-wide">Before:</span>
                            <p className="text-sm text-red-700 mt-1 line-through opacity-75 leading-relaxed">
                              {item.old_value.length > 150 ? item.old_value.substring(0, 150) + '...' : item.old_value}
                            </p>
                          </div>
                          <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                            <span className="text-xs font-bold text-green-600 uppercase tracking-wide">After:</span>
                            <p className="text-sm text-green-700 mt-1 font-medium leading-relaxed">
                              {item.new_value.length > 150 ? item.new_value.substring(0, 150) + '...' : item.new_value}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendations */}
              {comparison.recommendations.length > 0 && (
                <div className="animate-slide-up" style={{ animationDelay: '0.2s', animationFillMode: 'backwards' }}>
                  <h3 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 mb-4">
                    AI Recommendations
                  </h3>
                  <div className="space-y-3">
                    {comparison.recommendations.map((rec, idx) => (
                      <div key={idx} className="flex items-start gap-4 p-4 bg-gradient-to-r from-purple-50 to-pink-50 border-l-4 border-purple-500 rounded-xl shadow-md hover:shadow-lg transition-all duration-300">
                        <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center shadow-lg">
                          <span className="text-white font-bold text-sm">{idx + 1}</span>
                        </div>
                        <p className="text-purple-900 leading-relaxed font-medium pt-1">{rec}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {versions.length === 0 && !loading && (
            <div className="text-center py-12">
              <GitCompare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Versions Yet</h3>
              <p className="text-gray-600">Save a version of your resume to start tracking changes</p>
            </div>
          )}
        </div>
        </div>
      </div>
    </div>
  );
};
