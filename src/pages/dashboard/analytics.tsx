import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Layout from "../../components/Layout";
import { Card } from "../../components/Card";
import { Button } from "../../components/Button";
import { Line } from "react-chartjs-2";
import { Chart, registerables, ChartOptions } from "chart.js";
import { Download, TrendingUp, Eye, Share2, FileText } from "lucide-react";
Chart.register(...registerables);

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

interface ATSScore {
  score: number;
  date: string;
}

interface Analytics {
  id: string;
  resume_id: string;
  user_id: string;
  views: number;
  downloads: number;
  shares: number;
  template_id: string;
  ats_scores: ATSScore[];
  last_viewed?: string;
  last_downloaded?: string;
  last_shared?: string;
  created_at: string;
  updated_at: string;
}

const fetchAnalytics = async (resumeId: string): Promise<Analytics> => {
  const res = await fetch(`${API_BASE}/api/v1x/resume-analytics/${resumeId}`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error("Failed to fetch analytics");
  return await res.json();
};

const exportToCSV = (analytics: Analytics) => {
  const rows = [
    ['Metric', 'Value'],
    ['Views', analytics.views],
    ['Downloads', analytics.downloads],
    ['Shares', analytics.shares],
    ['Template', analytics.template_id || 'N/A'],
    ['Last Viewed', analytics.last_viewed || 'Never'],
    ['Last Downloaded', analytics.last_downloaded || 'Never'],
    ['Last Shared', analytics.last_shared || 'Never'],
    [''],
    ['ATS Score History'],
    ['Date', 'Score'],
    ...analytics.ats_scores.map(s => [new Date(s.date).toLocaleDateString(), s.score])
  ];
  
  const csvContent = rows.map(row => row.join(',')).join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `resume-analytics-${analytics.resume_id}.csv`;
  a.click();
  URL.revokeObjectURL(url);
};

export default function ResumeAnalyticsDashboard() {
  const router = useRouter();
  const { resumeId } = router.query;
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!resumeId) return;
    
    setLoading(true);
    fetchAnalytics(resumeId as string)
      .then(setAnalytics)
      .catch(err => {
        console.error(err);
        setError("Failed to load analytics");
      })
      .finally(() => setLoading(false));
  }, [resumeId]);

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent mx-auto mb-4"></div>
            <p className="text-gray-600">Loading analytics...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error || !analytics) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error || "No analytics found"}</p>
            <Button onClick={() => router.back()}>Go Back</Button>
          </div>
        </div>
      </Layout>
    );
  }

  const atsScores = analytics.ats_scores || [];
  const atsData = {
    labels: atsScores.map((s: ATSScore) => new Date(s.date).toLocaleDateString()),
    datasets: [
      {
        label: "ATS Score",
        data: atsScores.map((s: ATSScore) => s.score),
        fill: true,
        backgroundColor: "rgba(99, 102, 241, 0.1)",
        borderColor: "#6366f1",
        borderWidth: 3,
        pointBackgroundColor: "#6366f1",
        pointBorderColor: "#fff",
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7,
        tension: 0.4,
      },
    ],
  };

  const chartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: (value) => `${value}%`,
        },
      },
    },
  };

  const latestATS = atsScores.length > 0 ? atsScores[atsScores.length - 1].score : null;
  const avgATS = atsScores.length > 0 ? Math.round(atsScores.reduce((sum, s) => sum + s.score, 0) / atsScores.length) : null;

  return (
    <Layout>
      <div className="max-w-7xl mx-auto py-8 px-4">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Resume Analytics</h1>
            <p className="text-gray-600">Track your resume performance and insights</p>
          </div>
          <div className="flex gap-3">
            <Button onClick={() => router.back()} variant="secondary">
              ← Back
            </Button>
            <Button onClick={() => exportToCSV(analytics)} variant="primary">
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <div className="flex items-center justify-between mb-2">
              <Eye className="w-8 h-8 text-blue-600" />
              <span className="text-xs font-semibold text-blue-600 uppercase tracking-wide">Views</span>
            </div>
            <div className="text-4xl font-bold text-gray-900">{analytics.views}</div>
            <p className="text-sm text-gray-600 mt-1">
              {analytics.last_viewed ? `Last: ${new Date(analytics.last_viewed).toLocaleDateString()}` : 'No views yet'}
            </p>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <div className="flex items-center justify-between mb-2">
              <Download className="w-8 h-8 text-green-600" />
              <span className="text-xs font-semibold text-green-600 uppercase tracking-wide">Downloads</span>
            </div>
            <div className="text-4xl font-bold text-gray-900">{analytics.downloads}</div>
            <p className="text-sm text-gray-600 mt-1">
              {analytics.last_downloaded ? `Last: ${new Date(analytics.last_downloaded).toLocaleDateString()}` : 'No downloads yet'}
            </p>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <div className="flex items-center justify-between mb-2">
              <Share2 className="w-8 h-8 text-purple-600" />
              <span className="text-xs font-semibold text-purple-600 uppercase tracking-wide">Shares</span>
            </div>
            <div className="text-4xl font-bold text-gray-900">{analytics.shares}</div>
            <p className="text-sm text-gray-600 mt-1">
              {analytics.last_shared ? `Last: ${new Date(analytics.last_shared).toLocaleDateString()}` : 'No shares yet'}
            </p>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <div className="flex items-center justify-between mb-2">
              <FileText className="w-8 h-8 text-orange-600" />
              <span className="text-xs font-semibold text-orange-600 uppercase tracking-wide">Template</span>
            </div>
            <div className="text-2xl font-bold text-gray-900 capitalize">{analytics.template_id || 'Default'}</div>
            <p className="text-sm text-gray-600 mt-1">Current design</p>
          </Card>
        </div>

        {/* ATS Score Section */}
        {atsScores.length > 0 && (
          <Card className="p-8 mb-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <TrendingUp className="w-6 h-6 text-indigo-600" />
                  ATS Score Trend
                </h2>
                <p className="text-gray-600 mt-1">Track your Applicant Tracking System optimization over time</p>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600">Latest Score</div>
                <div className={`text-4xl font-bold ${latestATS && latestATS >= 80 ? 'text-green-600' : latestATS && latestATS >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                  {latestATS}%
                </div>
                <div className="text-sm text-gray-600 mt-1">Avg: {avgATS}%</div>
              </div>
            </div>
            <div style={{ height: '300px' }}>
              <Line data={atsData} options={chartOptions} />
            </div>
          </Card>
        )}

        {atsScores.length === 0 && (
          <Card className="p-8 text-center">
            <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No ATS Score History Yet</h3>
            <p className="text-gray-600">ATS scores will appear here as your resume is analyzed over time.</p>
          </Card>
        )}
      </div>
    </Layout>
  );
}
