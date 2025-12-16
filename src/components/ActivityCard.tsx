import React, { useState } from 'react';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';

interface Activity {
  id: number;
  user_id: number;
  user: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  activity_type: string;
  title: string;
  description?: string;
  points_earned: number;
  like_count: number;
  comment_count: number;
  view_count: number;
  created_at: string;
}

interface ActivityCardProps {
  activity: Activity;
  onLike?: () => void;
  onUnlike?: () => void;
  isLiked?: boolean;
}

const ActivityCard: React.FC<ActivityCardProps> = ({
  activity,
  onLike,
  onUnlike,
  isLiked = false,
}) => {
  const [expanded, setExpanded] = useState(false);

  const getActivityIcon = (type: string) => {
    const icons: { [key: string]: string } = {
      challenge_solved: '✅',
      badge_earned: '🏆',
      contest_participated: '🎯',
      contest_won: '🥇',
      solution_shared: '💡',
      course_completed: '📚',
      path_started: '🛤️',
      path_completed: '🎓',
      user_followed: '👥',
      streak_achieved: '🔥',
      comment_posted: '💬',
      solution_upvoted: '👍',
      mentor_session: '👨‍🏫',
      ai_hint_used: '🤖',
      points_earned: '⭐',
      leaderboard_rank: '📊',
      achievement_unlocked: '🎁',
      system_announcement: '📢',
    };
    return icons[type] || '📌';
  };

  const getActivityColor = (type: string) => {
    const colors: { [key: string]: string } = {
      challenge_solved: 'border-green-500',
      badge_earned: 'border-yellow-500',
      contest_participated: 'border-purple-500',
      contest_won: 'border-gold-500',
      solution_shared: 'border-blue-500',
      course_completed: 'border-indigo-500',
    };
    return colors[type] || 'border-gray-500';
  };

  return (
    <div
      className={`bg-gray-800 rounded-lg overflow-hidden border-l-4 ${getActivityColor(
        activity.activity_type
      )} hover:shadow-lg transition transform hover:scale-102`}
    >
      {/* Card Header */}
      <div className="p-6">
        {/* User and Meta */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
              {activity.user.avatar_url ? (
                <img
                  src={activity.user.avatar_url}
                  alt={activity.user.username}
                  className="w-10 h-10 rounded-full"
                />
              ) : (
                <span className="text-white font-bold text-sm">
                  {activity.user.username.charAt(0).toUpperCase()}
                </span>
              )}
            </div>
            <div>
              <Link href={`/profile/${activity.user.username}`}>
                <a className="font-semibold text-white hover:text-blue-400 transition">
                  {activity.user.username}
                </a>
              </Link>
              <p className="text-xs text-gray-400">
                {formatDistanceToNow(new Date(activity.created_at), { addSuffix: true })}
              </p>
            </div>
          </div>
          <span className="text-2xl">{getActivityIcon(activity.activity_type)}</span>
        </div>

        {/* Activity Title */}
        <div className="mb-3">
          <h3 className="text-lg font-bold text-white mb-1">{activity.title}</h3>
          {activity.description && (
            <p
              className={`text-gray-400 text-sm transition-all ${
                expanded ? 'line-clamp-none' : 'line-clamp-2'
              }`}
            >
              {activity.description}
            </p>
          )}
          {activity.description && activity.description.length > 150 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-blue-400 text-sm hover:text-blue-300 transition mt-1"
            >
              {expanded ? 'Read less' : 'Read more'}
            </button>
          )}
        </div>

        {/* Points Badge */}
        {activity.points_earned > 0 && (
          <div className="mb-4 inline-block bg-yellow-900 bg-opacity-50 text-yellow-200 px-3 py-1 rounded-full text-sm font-semibold">
            +{activity.points_earned} points
          </div>
        )}

        {/* Engagement Metrics and Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-700">
          {/* Metrics */}
          <div className="flex gap-6 text-sm">
            <button className="flex items-center gap-2 text-gray-400 hover:text-blue-400 transition">
              <span className="text-lg">{isLiked ? '❤️' : '🤍'}</span>
              <span>{activity.like_count}</span>
            </button>
            <div className="flex items-center gap-2 text-gray-400">
              <span className="text-lg">💬</span>
              <span>{activity.comment_count}</span>
            </div>
            <div className="flex items-center gap-2 text-gray-400">
              <span className="text-lg">👁️</span>
              <span>{activity.view_count}</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            {isLiked ? (
              <button
                onClick={onUnlike}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition text-sm"
              >
                Unlike
              </button>
            ) : (
              <button
                onClick={onLike}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-semibold transition text-sm"
              >
                Like
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActivityCard;
