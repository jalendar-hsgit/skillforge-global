// Enhanced Dashboard with Real-time Analytics
import Head from 'next/head';
import Layout from '@/components/Layout';
import {
  PageHeader,
  PageContainer,
  PageSection,
  PageGrid,
  LoadingState,
} from '@/components/PageLayout';
import {
  AnalyticsCard,
  QuizScoreCard,
  LearningPathProgress,
  AchievementBadge,
  StreakIndicator,
} from '@/components/DashboardAnalytics';
import {
  useDashboardStats,
  useLearningPaths,
  useQuizAnalytics,
  useAchievements,
} from '@/hooks/useDashboard';
import { Button } from '@/components/Button';
import { ROUTES } from '@/lib/routes';
import Link from 'next/link';

export default function EnhancedDashboard() {
  const { stats, loading: statsLoading } = useDashboardStats();
  const { paths, loading: pathsLoading } = useLearningPaths();
  const { analytics, loading: analyticsLoading } = useQuizAnalytics(30);
  const { achievements, loading: achievementsLoading } = useAchievements();

  if (statsLoading) {
    return (
      <Layout>
        <LoadingState message="Loading your dashboard..." />
      </Layout>
    );
  }

  return (
    <Layout>
      <Head>
        <title>Dashboard - SkillForge Global</title>
        <meta
          name="description"
          content="Your personalized learning dashboard"
        />
      </Head>

      <PageContainer>
        <PageHeader
          title="Your Learning Dashboard"
          subtitle="Track your progress, achievements, and AI-powered insights"
        />

        {/* Top Stats Grid */}
        <PageSection>
          <h2 className="mb-4 text-xl font-bold text-gray-900">
            Overview
          </h2>
          <PageGrid cols={4}>
            <AnalyticsCard
              title="Videos Completed"
              value={stats?.totals.videos_completed || 0}
              icon="📺"
              color="blue"
              subtitle="Keep watching to learn more"
            />
            <AnalyticsCard
              title="Quizzes Taken"
              value={stats?.totals.quizzes_taken || 0}
              icon="📝"
              color="green"
              subtitle="Test your knowledge"
            />
            <AnalyticsCard
              title="Forge Credits"
              value={stats?.totals.forge_credits || 0}
              icon="⚡"
              color="purple"
              subtitle="Use for AI quiz generation"
            />
            <AnalyticsCard
              title="Pass Rate"
              value={`${stats?.performance.quiz_pass_rate || 0}%`}
              icon="🎯"
              color="orange"
              subtitle="Your quiz success rate"
            />
          </PageGrid>
        </PageSection>

        {/* Streak and Recent Activity */}
        <PageSection>
          <h2 className="mb-4 text-xl font-bold text-gray-900">
            Your Momentum
          </h2>
          <PageGrid cols={3}>
            <StreakIndicator
              days={stats?.performance.learning_streak_days || 0}
            />
            <AnalyticsCard
              title="Recent Videos"
              value={stats?.recent_activity.videos_last_7_days || 0}
              subtitle="Last 7 days"
              icon="📹"
              color="blue"
              trend={
                (stats?.recent_activity.videos_last_7_days || 0) > 0
                  ? 'up'
                  : 'neutral'
              }
            />
            <AnalyticsCard
              title="Recent Quizzes"
              value={stats?.recent_activity.quizzes_last_7_days || 0}
              subtitle="Last 7 days"
              icon="✏️"
              color="green"
              trend={
                (stats?.recent_activity.quizzes_last_7_days || 0) > 0
                  ? 'up'
                  : 'neutral'
              }
            />
          </PageGrid>
        </PageSection>

        {/* Best Quiz Scores */}
        {stats?.performance.best_quiz_scores &&
          stats.performance.best_quiz_scores.length > 0 && (
            <PageSection>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900">
                  Your Best Scores
                </h2>
                <Link href={ROUTES.paths}>
                  <Button size="sm" variant="secondary">
                    View All Paths
                  </Button>
                </Link>
              </div>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
                {stats.performance.best_quiz_scores.map((score, idx) => (
                  <QuizScoreCard
                    key={idx}
                    path={score.path}
                    score={score.score}
                    total={score.total}
                  />
                ))}
              </div>
            </PageSection>
          )}

        {/* Learning Paths Progress */}
        {!pathsLoading && paths && paths.length > 0 && (
          <PageSection>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">
                Your Learning Paths
              </h2>
              <Link href={ROUTES.paths}>
                <Button size="sm" variant="outline">
                  Browse All Paths
                </Button>
              </Link>
            </div>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {paths.slice(0, 6).map((path, idx) => (
                <LearningPathProgress
                  key={idx}
                  path={path.path}
                  title={path.title}
                  completed_videos={path.completed_videos}
                  total_videos={path.total_videos}
                  percentage={path.percentage}
                  last_watched={path.last_watched}
                />
              ))}
            </div>
          </PageSection>
        )}

        {/* Quiz Analytics */}
        {!analyticsLoading && analytics && analytics.total_quizzes > 0 && (
          <PageSection>
            <h2 className="mb-4 text-xl font-bold text-gray-900">
              Quiz Analytics (Last 30 Days)
            </h2>
            <PageGrid cols={3}>
              <AnalyticsCard
                title="Total Quizzes"
                value={analytics.total_quizzes}
                icon="📊"
                color="blue"
              />
              <AnalyticsCard
                title="Average Score"
                value={`${analytics.avg_score_percentage.toFixed(1)}%`}
                icon="📈"
                color="green"
              />
              <AnalyticsCard
                title="Saved Quizzes"
                value={stats?.totals.saved_quizzes || 0}
                subtitle={`${stats?.totals.favorite_quizzes || 0} favorites`}
                icon="⭐"
                color="purple"
              />
            </PageGrid>

            {/* Topic Breakdown */}
            {analytics.topic_breakdown.length > 0 && (
              <div className="mt-6">
                <h3 className="mb-3 text-lg font-semibold text-gray-800">
                  Popular Topics
                </h3>
                <div className="flex flex-wrap gap-2">
                  {analytics.topic_breakdown.slice(0, 8).map((topic, idx) => (
                    <div
                      key={idx}
                      className="rounded-full border border-blue-200 bg-blue-50 px-4 py-2"
                    >
                      <span className="text-sm font-medium text-blue-700">
                        {topic.topic}
                      </span>
                      <span className="ml-2 text-xs text-blue-500">
                        ×{topic.count}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Difficulty Distribution */}
            <div className="mt-6">
              <h3 className="mb-3 text-lg font-semibold text-gray-800">
                Difficulty Distribution
              </h3>
              <div className="flex gap-4">
                <div className="flex-1 rounded-lg border border-green-200 bg-green-50 p-4 text-center">
                  <div className="text-2xl font-bold text-green-700">
                    {analytics.difficulty_distribution.easy}
                  </div>
                  <div className="text-sm text-green-600">Easy</div>
                </div>
                <div className="flex-1 rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-center">
                  <div className="text-2xl font-bold text-yellow-700">
                    {analytics.difficulty_distribution.medium}
                  </div>
                  <div className="text-sm text-yellow-600">Medium</div>
                </div>
                <div className="flex-1 rounded-lg border border-red-200 bg-red-50 p-4 text-center">
                  <div className="text-2xl font-bold text-red-700">
                    {analytics.difficulty_distribution.hard}
                  </div>
                  <div className="text-sm text-red-600">Hard</div>
                </div>
              </div>
            </div>
          </PageSection>
        )}

        {/* Achievements */}
        {!achievementsLoading && achievements && achievements.length > 0 && (
          <PageSection>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">
                Your Achievements
              </h2>
              <span className="text-sm text-gray-500">
                {achievements.filter((a) => a.unlocked).length} /{' '}
                {achievements.length} unlocked
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              {achievements.map((achievement) => (
                <AchievementBadge
                  key={achievement.id}
                  id={achievement.id}
                  name={achievement.name}
                  description={achievement.description}
                  icon={achievement.icon}
                  unlocked={achievement.unlocked}
                />
              ))}
            </div>
          </PageSection>
        )}

        {/* Quick Actions */}
        <PageSection>
          <h2 className="mb-4 text-xl font-bold text-gray-900">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <Link href={ROUTES.paths}>
              <div className="cursor-pointer rounded-xl border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100 p-6 transition-all hover:shadow-lg">
                <div className="mb-2 text-3xl">🎓</div>
                <h3 className="mb-1 font-semibold text-blue-900">
                  Browse Learning Paths
                </h3>
                <p className="text-sm text-blue-700">
                  Explore new courses and career paths
                </p>
              </div>
            </Link>

            <Link href="/quiz/stream">
              <div className="cursor-pointer rounded-xl border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100 p-6 transition-all hover:shadow-lg">
                <div className="mb-2 text-3xl">🤖</div>
                <h3 className="mb-1 font-semibold text-purple-900">
                  Generate AI Quiz
                </h3>
                <p className="text-sm text-purple-700">
                  Create personalized quizzes with AI
                </p>
              </div>
            </Link>

            <Link href="/dashboard">
              <div className="cursor-pointer rounded-xl border-2 border-green-200 bg-gradient-to-br from-green-50 to-green-100 p-6 transition-all hover:shadow-lg">
                <div className="mb-2 text-3xl">📊</div>
                <h3 className="mb-1 font-semibold text-green-900">
                  View Analytics
                </h3>
                <p className="text-sm text-green-700">
                  Deep dive into your progress
                </p>
              </div>
            </Link>
          </div>
        </PageSection>
      </PageContainer>
    </Layout>
  );
}
