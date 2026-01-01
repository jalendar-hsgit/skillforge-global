import React from 'react';
import Link from 'next/link';

interface ForumTopicCardProps {
  id: number;
  title: string;
  description: string;
  threadCount: number;
  replyCount: number;
  latestActivity: string;
  category: string;
  icon?: string;
}

export default function ForumTopicCard({
  id,
  title,
  description,
  threadCount,
  replyCount,
  latestActivity,
  category,
  icon = '💬'
}: ForumTopicCardProps) {
  return (
    <Link href={`/community/forums/topic/${id}`}>
      <div className="block p-6 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:shadow-lg hover:border-blue-500 dark:hover:border-blue-400 transition-all cursor-pointer">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-3 flex-1">
            <span className="text-3xl">{icon}</span>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400">
                {title}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                {description}
              </p>
            </div>
          </div>
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
            {category}
          </span>
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 pt-4">
          <div className="flex items-center gap-1">
            <span>📌</span>
            <span>{threadCount} threads</span>
          </div>
          <div className="flex items-center gap-1">
            <span>💬</span>
            <span>{replyCount} replies</span>
          </div>
          <div className="flex items-center gap-1 ml-auto">
            <span>🕐</span>
            <span>{latestActivity}</span>
          </div>
        </div>
      </div>
    </Link>
  );
}
