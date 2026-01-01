import React from 'react';
import Link from 'next/link';

interface SocialFeedItemProps {
  id: number;
  type: 'post' | 'achievement' | 'course-completed' | 'skill-added';
  author: {
    id: number;
    name: string;
    avatar?: string;
  };
  content: string;
  timestamp: string;
  likes: number;
  comments: number;
  isLiked?: boolean;
  image?: string;
  metadata?: {
    courseTitle?: string;
    skillName?: string;
    achievementName?: string;
  };
}

const typeIcons = {
  post: '📝',
  'achievement': '🏆',
  'course-completed': '📚',
  'skill-added': '⭐'
};

const typeColors = {
  post: 'bg-blue-50 dark:bg-blue-900/20',
  'achievement': 'bg-yellow-50 dark:bg-yellow-900/20',
  'course-completed': 'bg-green-50 dark:bg-green-900/20',
  'skill-added': 'bg-purple-50 dark:bg-purple-900/20'
};

export default function SocialFeedItem({
  id,
  type,
  author,
  content,
  timestamp,
  likes,
  comments,
  isLiked = false,
  image,
  metadata
}: SocialFeedItemProps) {
  return (
    <div className={`rounded-lg border border-gray-200 dark:border-gray-700 ${typeColors[type]} p-5 mb-4`}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <img
          src={author.avatar || `https://ui-avatars.com/api/?name=${author.name}&background=random`}
          alt={author.name}
          className="w-10 h-10 rounded-full"
        />
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <Link href={`/profile/${author.id}`}>
              <span className="font-semibold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400">
                {author.name}
              </span>
            </Link>
            <span className="text-lg">{typeIcons[type]}</span>
          </div>
          <span className="text-xs text-gray-500 dark:text-gray-500">{timestamp}</span>
        </div>
      </div>

      {/* Metadata */}
      {metadata && (
        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
          {metadata.courseTitle && (
            <p className="text-sm text-gray-700 dark:text-gray-300">
              Completed: <span className="font-semibold">{metadata.courseTitle}</span>
            </p>
          )}
          {metadata.skillName && (
            <p className="text-sm text-gray-700 dark:text-gray-300">
              Added skill: <span className="font-semibold">{metadata.skillName}</span>
            </p>
          )}
          {metadata.achievementName && (
            <p className="text-sm text-gray-700 dark:text-gray-300">
              Unlocked: <span className="font-semibold">{metadata.achievementName}</span>
            </p>
          )}
        </div>
      )}

      {/* Content */}
      <p className="text-gray-800 dark:text-gray-200 mb-4 leading-relaxed">
        {content}
      </p>

      {/* Image */}
      {image && (
        <img
          src={image}
          alt="Feed item"
          className="w-full rounded-lg mb-4 max-h-64 object-cover"
        />
      )}

      {/* Actions */}
      <div className="flex items-center gap-6 text-sm text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 pt-4">
        <button className={`flex items-center gap-1 hover:text-red-600 dark:hover:text-red-400 transition-colors ${isLiked ? 'text-red-600 dark:text-red-400' : ''}`}>
          <span className="text-lg">{isLiked ? '❤️' : '🤍'}</span>
          <span>{likes}</span>
        </button>
        <button className="flex items-center gap-1 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
          <span className="text-lg">💬</span>
          <span>{comments}</span>
        </button>
        <button className="ml-auto flex items-center gap-1 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
          <span className="text-lg">📤</span>
          <span>Share</span>
        </button>
      </div>
    </div>
  );
}
