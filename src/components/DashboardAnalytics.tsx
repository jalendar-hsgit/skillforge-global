// Enhanced Dashboard Analytics Component
import React from 'react';

export interface DashboardStats {
  user_id: number;
  totals: {
    videos_completed: number;
    quizzes_taken: number;
    forge_credits: number;
    saved_quizzes: number;
    favorite_quizzes: number;
  };
  performance: {
    quiz_pass_rate: number;
    learning_streak_days: number;
    best_quiz_scores: Array<{
      path: string;
      score: number;
      total: number;
    }>;
  };
  recent_activity: {
    videos_last_7_days: number;
    quizzes_last_7_days: number;
  };
}

interface AnalyticsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: string;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'blue' | 'green' | 'purple' | 'orange';
}

export const AnalyticsCard: React.FC<AnalyticsCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  color = 'blue',
}) => {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    green: 'bg-green-50 border-green-200 text-green-700',
    purple: 'bg-purple-50 border-purple-200 text-purple-700',
    orange: 'bg-orange-50 border-orange-200 text-orange-700',
  };

  const trendIcons = {
    up: '↗',
    down: '↘',
    neutral: '→',
  };

  return (
    <div
      className={`rounded-xl border-2 p-6 transition-all hover:shadow-lg ${colorClasses[color]}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium opacity-70">{title}</p>
          <div className="mt-2 flex items-baseline gap-2">
            <p className="text-3xl font-bold">{value}</p>
            {trend && (
              <span className="text-sm opacity-60">
                {trendIcons[trend]}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="mt-1 text-xs opacity-60">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className="text-3xl opacity-50">{icon}</div>
        )}
      </div>
    </div>
  );
};

interface QuizScoreCardProps {
  path: string;
  score: number;
  total: number;
}

export const QuizScoreCard: React.FC<QuizScoreCardProps> = ({
  path,
  score,
  total,
}) => {
  const percentage = (score / total) * 100;
  const isPerfect = percentage === 100;

  return (
    <div className="flex items-center gap-3 rounded-lg border border-gray-200 bg-white p-3 shadow-sm transition-all hover:shadow-md">
      <div className={`flex h-12 w-12 items-center justify-center rounded-full ${
        isPerfect ? 'bg-yellow-100' : 'bg-blue-100'
      }`}>
        <span className="text-xl">{isPerfect ? '🏆' : '📝'}</span>
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-900">{path}</p>
        <p className="text-xs text-gray-500">
          {score} / {total} ({percentage.toFixed(0)}%)
        </p>
      </div>
    </div>
  );
};

interface LearningPathProgressProps {
  path: string;
  title: string;
  completed_videos: number;
  total_videos: number;
  percentage: number;
  last_watched?: string;
}

export const LearningPathProgress: React.FC<LearningPathProgressProps> = ({
  path,
  title,
  completed_videos,
  total_videos,
  percentage,
  last_watched,
}) => {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-all hover:shadow-md">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <span className="text-sm font-medium text-blue-600">
          {percentage.toFixed(0)}%
        </span>
      </div>
      
      <div className="mb-2 h-2 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className="h-full rounded-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all"
          style={{ width: `${percentage}%` }}
        />
      </div>
      
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>
          {completed_videos} / {total_videos} videos
        </span>
        {last_watched && (
          <span>
            Last watched: {new Date(last_watched).toLocaleDateString()}
          </span>
        )}
      </div>
    </div>
  );
};

interface AchievementBadgeProps {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
}

export const AchievementBadge: React.FC<AchievementBadgeProps> = ({
  name,
  description,
  icon,
  unlocked,
}) => {
  return (
    <div
      className={`rounded-lg border p-4 text-center transition-all ${
        unlocked
          ? 'border-yellow-300 bg-yellow-50 shadow-md'
          : 'border-gray-200 bg-gray-50 opacity-50'
      }`}
    >
      <div className="mb-2 text-4xl">{icon}</div>
      <h4 className="mb-1 text-sm font-semibold text-gray-900">{name}</h4>
      <p className="text-xs text-gray-600">{description}</p>
      {unlocked && (
        <div className="mt-2 text-xs font-medium text-yellow-700">
          ✓ Unlocked
        </div>
      )}
    </div>
  );
};

interface StreakIndicatorProps {
  days: number;
}

export const StreakIndicator: React.FC<StreakIndicatorProps> = ({ days }) => {
  const getStreakEmoji = (days: number) => {
    if (days >= 30) return '🔥🔥🔥';
    if (days >= 7) return '🔥🔥';
    if (days >= 1) return '🔥';
    return '😴';
  };

  const getStreakMessage = (days: number) => {
    if (days >= 30) return 'On fire!';
    if (days >= 7) return 'Great momentum!';
    if (days >= 1) return 'Keep it up!';
    return 'Start your streak today!';
  };

  return (
    <div className="rounded-xl border-2 border-orange-200 bg-gradient-to-br from-orange-50 to-yellow-50 p-6 text-center shadow-md">
      <div className="mb-2 text-5xl">{getStreakEmoji(days)}</div>
      <div className="text-3xl font-bold text-orange-700">{days}</div>
      <div className="text-sm font-medium text-orange-600">
        Day Streak
      </div>
      <div className="mt-2 text-xs text-orange-500">
        {getStreakMessage(days)}
      </div>
    </div>
  );
};
