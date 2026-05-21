import React, { useState, useEffect } from "react";
import Layout from "@/components/Layout";
import { Card } from "@/components/Card";
import Button from "@/components/Button";
import SectionHeading from "@/components/SectionHeading";
import { TrendingUp, Activity, Award, Zap, Users, Code } from "lucide-react";

interface Analytics {
  total_submissions: number;
  total_challenges_completed: number;
  total_learning_minutes: number;
  average_code_quality_score: number;
  current_streak_days: number;
  longest_streak_days: number;
  total_coins_earned: number;
  coins_earned_this_month: number;
  total_achievements: number;
  total_followers: number;
  global_rank: number | null;
  weekly_growth_percent: number;
  monthly_growth_percent: number;
  primary_language: string;
  languages: Record<string, number>;
  skills: string[];
}

export default function AdvancedDashboard() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState<any[]>([]);

  useEffect(() => {
    fetchAnalytics();
    fetchInsights();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/dashboard/analytics`,
        { credentials: "include" }
      );
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data.analytics);
      }
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
      setLoading(false);
    }
  };

  const fetchInsights = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/dashboard/insights?limit=5`,
        { credentials: "include" }
      );
      if (response.ok) {
        const data = await response.json();
        setInsights(data.insights || []);
      }
    } catch (error) {
      console.error("Failed to fetch insights:", error);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
          <div className="text-center text-white">
            <p>Loading analytics...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Header */}
          <div className="mb-12">
            <SectionHeading className="text-white mb-4">Your Advanced Dashboard</SectionHeading>
            <p className="text-slate-300 text-lg">
              Track your progress, view detailed analytics, and get personalized insights to accelerate your learning.
            </p>
          </div>

          {analytics && (
            <>
              {/* Key Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {/* Submissions */}
                <Card className="bg-gradient-to-br from-blue-900/30 to-slate-800 border-slate-700">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-slate-400 text-sm mb-2">Submissions</p>
                      <h3 className="text-3xl font-bold text-white mb-2">
                        {analytics.total_submissions}
                      </h3>
                      <p className="text-xs text-blue-400">
                        📈 {analytics.weekly_growth_percent}% this week
                      </p>
                    </div>
                    <Code className="w-8 h-8 text-blue-400 opacity-50" />
                  </div>
                </Card>

                {/* Challenges Completed */}
                <Card className="bg-gradient-to-br from-green-900/30 to-slate-800 border-slate-700">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-slate-400 text-sm mb-2">Challenges</p>
                      <h3 className="text-3xl font-bold text-white mb-2">
                        {analytics.total_challenges_completed}
                      </h3>
                      <p className="text-xs text-green-400">
                        ✓ Completed
                      </p>
                    </div>
                    <Award className="w-8 h-8 text-green-400 opacity-50" />
                  </div>
                </Card>

                {/* Current Streak */}
                <Card className="bg-gradient-to-br from-orange-900/30 to-slate-800 border-slate-700">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-slate-400 text-sm mb-2">Streak</p>
                      <h3 className="text-3xl font-bold text-white mb-2">
                        {analytics.current_streak_days}
                      </h3>
                      <p className="text-xs text-orange-400">
                        🔥 {analytics.longest_streak_days} days best
                      </p>
                    </div>
                    <Zap className="w-8 h-8 text-orange-400 opacity-50" />
                  </div>
                </Card>

                {/* Coins Earned */}
                <Card className="bg-gradient-to-br from-yellow-900/30 to-slate-800 border-slate-700">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-slate-400 text-sm mb-2">Coins</p>
                      <h3 className="text-3xl font-bold text-white mb-2">
                        {analytics.total_coins_earned}
                      </h3>
                      <p className="text-xs text-yellow-400">
                        💰 {analytics.coins_earned_this_month} this month
                      </p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-yellow-400 opacity-50" />
                  </div>
                </Card>
              </div>

              {/* Secondary Metrics */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                {/* Code Quality */}
                <Card className="bg-slate-800 border-slate-700">
                  <h3 className="text-lg font-semibold text-white mb-4">Code Quality</h3>
                  <div className="mb-4">
                    <div className="text-4xl font-bold text-blue-400">
                      {analytics.average_code_quality_score.toFixed(1)}
                    </div>
                    <p className="text-slate-400 text-sm">Average Score</p>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full"
                      style={{ width: `${(analytics.average_code_quality_score / 100) * 100}%` }}
                    />
                  </div>
                </Card>

                {/* Languages */}
                <Card className="bg-slate-800 border-slate-700">
                  <h3 className="text-lg font-semibold text-white mb-4">Languages</h3>
                  <div className="space-y-2">
                    {analytics.primary_language && (
                      <div className="flex justify-between items-center">
                        <span className="text-slate-300">{analytics.primary_language}</span>
                        <span className="text-blue-400 font-semibold">Primary</span>
                      </div>
                    )}
                    {Object.entries(analytics.languages).slice(0, 2).map(([lang, count]) => (
                      <div key={lang} className="text-xs text-slate-400">
                        {lang}: {count} challenges
                      </div>
                    ))}
                  </div>
                </Card>

                {/* Social Stats */}
                <Card className="bg-slate-800 border-slate-700">
                  <h3 className="text-lg font-semibold text-white mb-4">Community</h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4 text-slate-400" />
                      <span className="text-slate-300">{analytics.total_followers} followers</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Award className="w-4 h-4 text-slate-400" />
                      <span className="text-slate-300">{analytics.total_achievements} achievements</span>
                    </div>
                    {analytics.global_rank && (
                      <div className="flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-slate-400" />
                        <span className="text-slate-300">Rank #{analytics.global_rank}</span>
                      </div>
                    )}
                  </div>
                </Card>
              </div>

              {/* Learning Time */}
              <Card className="bg-slate-800 border-slate-700 mb-8">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  Learning Activity
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                  <div>
                    <p className="text-slate-400 text-sm mb-2">Total Learning Time</p>
                    <p className="text-3xl font-bold text-white">
                      {Math.floor(analytics.total_learning_minutes / 60)}h{analytics.total_learning_minutes % 60}m
                    </p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm mb-2">Weekly Growth</p>
                    <p className="text-3xl font-bold text-green-400">
                      +{analytics.weekly_growth_percent}%
                    </p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm mb-2">Monthly Growth</p>
                    <p className="text-3xl font-bold text-blue-400">
                      +{analytics.monthly_growth_percent}%
                    </p>
                  </div>
                </div>
              </Card>

              {/* Insights Section */}
              {insights.length > 0 && (
                <Card className="bg-slate-800 border-slate-700">
                  <h3 className="text-lg font-semibold text-white mb-4">Personalized Insights</h3>
                  <div className="space-y-4">
                    {insights.map(insight => (
                      <div
                        key={insight.id}
                        className={`p-4 rounded-lg border-l-4 ${
                          insight.priority === "high"
                            ? "bg-red-900/20 border-l-red-500"
                            : insight.priority === "normal"
                            ? "bg-blue-900/20 border-l-blue-500"
                            : "bg-slate-700/20 border-l-slate-500"
                        }`}
                      >
                        <h4 className="font-semibold text-white mb-1">{insight.title}</h4>
                        <p className="text-slate-300 text-sm mb-3">{insight.description}</p>
                        {insight.action_url && (
                          <a href={insight.action_url} className="text-blue-400 text-sm hover:underline">
                            {insight.action_label || "Take action"} →
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              {/* Skills Section */}
              {analytics.skills.length > 0 && (
                <Card className="bg-slate-800 border-slate-700 mt-8">
                  <h3 className="text-lg font-semibold text-white mb-4">Your Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {analytics.skills.map(skill => (
                      <span
                        key={skill}
                        className="px-3 py-1 bg-blue-600/30 text-blue-300 rounded-full text-sm border border-blue-500/50"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}
