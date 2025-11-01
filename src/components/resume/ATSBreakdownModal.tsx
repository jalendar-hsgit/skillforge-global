import { TrendingUp, AlertCircle, CheckCircle, XCircle, Zap, Target, FileText } from 'lucide-react';
import { useState, useEffect } from 'react';
import ModalShell from './ModalShell';

interface ATSBreakdown {
  overall_score: number;
  formatting_score: number;
  keyword_score: number;
  content_score: number;
  missing_keywords: string[];
  issues: Array<{
    severity: 'high' | 'medium' | 'low';
    message: string;
    suggestion: string;
  }>;
  recommendations: string[];
}

interface ATSBreakdownModalProps {
  resumeId: string;
  onClose: () => void;
}

export default function ATSBreakdownModal({ resumeId, onClose }: ATSBreakdownModalProps) {
  const [breakdown, setBreakdown] = useState<ATSBreakdown | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBreakdown();
  }, [resumeId]);

  const fetchBreakdown = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/session/resume-ai/ats-score/${resumeId}`, {
        credentials: 'include',
      });

      if (!response.ok) throw new Error('Failed to fetch ATS breakdown');

      const data = await response.json();
      setBreakdown({
        overall_score: data.score || 0,
        formatting_score: data.formatting_score || 0,
        keyword_score: data.keyword_score || 0,
        content_score: data.content_score || 0,
        missing_keywords: data.missing_keywords || [],
        issues: data.issues || [],
        recommendations: data.recommendations || [],
      });
    } catch (err: any) {
      setError(err.message || 'Failed to load ATS breakdown');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'from-green-500/30 to-green-600/20 border-green-400/50';
    if (score >= 60) return 'from-yellow-500/30 to-yellow-600/20 border-yellow-400/50';
    return 'from-red-500/30 to-red-600/20 border-red-400/50';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'medium':
        return <AlertCircle className="w-5 h-5 text-yellow-400" />;
      case 'low':
        return <AlertCircle className="w-5 h-5 text-blue-400" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-500/20 border-red-500/50';
      case 'medium':
        return 'bg-yellow-500/20 border-yellow-500/50';
      case 'low':
        return 'bg-blue-500/20 border-blue-500/50';
      default:
        return 'bg-gray-500/20 border-gray-500/50';
    }
  };

  return (
    <ModalShell
      isOpen={true}
      onClose={onClose}
      title="ATS Analysis"
      icon={<Target className="w-6 h-6 text-white" />}
      accent="purple"
      size="xl"
    >
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-forgePurple/20 border-t-forgePurple mx-auto mb-4"></div>
                <p className="text-techGray font-medium">Analyzing your resume...</p>
              </div>
            </div>
          ) : error ? (
            <div className="bg-red-500/20 border-2 border-red-500/50 rounded-2xl p-6 text-center">
              <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
              <p className="text-red-200 font-medium">{error}</p>
            </div>
          ) : breakdown ? (
            <div className="space-y-6">
              {/* Overall Score */}
              <div className={`bg-gradient-to-br ${getScoreBg(breakdown.overall_score)} border-2 rounded-2xl p-6`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-bold uppercase tracking-wider text-white/80 mb-1">Overall ATS Score</p>
                    <p className="text-sm text-white/70">How well your resume passes automated screening</p>
                  </div>
                  <div className="text-center">
                    <div className={`text-6xl font-black ${getScoreColor(breakdown.overall_score)}`}>
                      {breakdown.overall_score}%
                    </div>
                    <p className="text-xs text-white/60 font-medium mt-1">
                      {breakdown.overall_score >= 80 ? 'Excellent' : breakdown.overall_score >= 60 ? 'Good' : 'Needs Work'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Score Breakdown */}
              <div className="grid grid-cols-3 gap-4">
                {/* Formatting Score */}
                <div className="bg-white/5 border border-white/10 rounded-xl p-5 hover:bg-white/10 transition-all">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="p-2 bg-blue-500/20 rounded-lg">
                      <FileText className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-white">Formatting</p>
                      <p className="text-xs text-techGray/70">Layout & Structure</p>
                    </div>
                  </div>
                  <div className={`text-4xl font-black ${getScoreColor(breakdown.formatting_score)}`}>
                    {breakdown.formatting_score}%
                  </div>
                  <div className="mt-3 h-2 bg-white/10 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-blue-500 to-blue-400 transition-all duration-500"
                      style={{ width: `${breakdown.formatting_score}%` }}
                    />
                  </div>
                </div>

                {/* Keyword Score */}
                <div className="bg-white/5 border border-white/10 rounded-xl p-5 hover:bg-white/10 transition-all">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="p-2 bg-purple-500/20 rounded-lg">
                      <Zap className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-white">Keywords</p>
                      <p className="text-xs text-techGray/70">Industry Terms</p>
                    </div>
                  </div>
                  <div className={`text-4xl font-black ${getScoreColor(breakdown.keyword_score)}`}>
                    {breakdown.keyword_score}%
                  </div>
                  <div className="mt-3 h-2 bg-white/10 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-purple-500 to-purple-400 transition-all duration-500"
                      style={{ width: `${breakdown.keyword_score}%` }}
                    />
                  </div>
                </div>

                {/* Content Score */}
                <div className="bg-white/5 border border-white/10 rounded-xl p-5 hover:bg-white/10 transition-all">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="p-2 bg-green-500/20 rounded-lg">
                      <TrendingUp className="w-5 h-5 text-green-400" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-white">Content</p>
                      <p className="text-xs text-techGray/70">Quality & Depth</p>
                    </div>
                  </div>
                  <div className={`text-4xl font-black ${getScoreColor(breakdown.content_score)}`}>
                    {breakdown.content_score}%
                  </div>
                  <div className="mt-3 h-2 bg-white/10 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-green-500 to-green-400 transition-all duration-500"
                      style={{ width: `${breakdown.content_score}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Missing Keywords */}
              {breakdown.missing_keywords.length > 0 && (
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-2xl p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <AlertCircle className="w-6 h-6 text-yellow-400" />
                    <h3 className="text-lg font-black text-white">Missing Keywords ({breakdown.missing_keywords.length})</h3>
                  </div>
                  <p className="text-sm text-techGray/80 mb-4">
                    Adding these keywords could improve your ATS score and match rate
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {breakdown.missing_keywords.map((keyword, index) => (
                      <span
                        key={index}
                        className="px-4 py-2 bg-yellow-500/20 border border-yellow-500/40 rounded-lg text-sm font-bold text-yellow-300 hover:bg-yellow-500/30 transition-all cursor-pointer"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Issues */}
              {breakdown.issues.length > 0 && (
                <div className="space-y-3">
                  <h3 className="text-lg font-black text-white flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-forgePurple" />
                    Issues Found ({breakdown.issues.length})
                  </h3>
                  {breakdown.issues.map((issue, index) => (
                    <div
                      key={index}
                      className={`${getSeverityBg(issue.severity)} border-2 rounded-xl p-4 hover:scale-[1.01] transition-all`}
                    >
                      <div className="flex items-start gap-3">
                        {getSeverityIcon(issue.severity)}
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-xs font-bold uppercase tracking-wider text-white/80">
                              {issue.severity} Priority
                            </span>
                          </div>
                          <p className="text-sm font-bold text-white mb-2">{issue.message}</p>
                          <p className="text-xs text-techGray/80 leading-relaxed">
                            💡 <strong>Suggestion:</strong> {issue.suggestion}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Recommendations */}
              {breakdown.recommendations.length > 0 && (
                <div className="bg-green-500/10 border border-green-500/30 rounded-2xl p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <CheckCircle className="w-6 h-6 text-green-400" />
                    <h3 className="text-lg font-black text-white">Recommendations</h3>
                  </div>
                  <ul className="space-y-3">
                    {breakdown.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <span className="text-green-400 mt-0.5">✓</span>
                        <p className="text-sm text-white/90 leading-relaxed">{rec}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Pro Tip */}
              <div className="bg-neuralBlue/10 border border-neuralBlue/30 rounded-2xl p-6">
                <p className="text-sm text-techGray/90 leading-relaxed text-center">
                  💡 <strong className="text-white">Pro Tip:</strong> ATS systems prioritize resumes with clear formatting, 
                  relevant keywords, and quantifiable achievements. Aim for a score above 75% for best results.
                </p>
              </div>
            </div>
          ) : null}
    </ModalShell>
  );
}
