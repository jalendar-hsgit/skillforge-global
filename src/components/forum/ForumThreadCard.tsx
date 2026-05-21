import React from 'react';
import Link from 'next/link';

interface ForumThreadCardProps {
  id: number;
  title: string;
  author: {
    id: number;
    name: string;
    avatar?: string;
  };
  preview: string;
  views: number;
  replyCount: number;
  createdAt: string;
  isPinned?: boolean;
  isSolved?: boolean;
}

export default function ForumThreadCard({
  id,
  title,
  author,
  preview,
  views,
  replyCount,
  createdAt,
  isPinned = false,
  isSolved = false
}: ForumThreadCardProps) {
  return (
    <Link href={`/community/forums/thread/${id}`}>
      <div className="block p-5 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:shadow-md hover:border-blue-500 dark:hover:border-blue-400 transition-all cursor-pointer">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <img
            src={author.avatar || `https://ui-avatars.com/api/?name=${author.name}&background=random`}
            alt={author.name}
            className="w-10 h-10 rounded-full flex-shrink-0"
          />

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 truncate">
                {title}
              </h3>
              {isPinned && <span className="text-lg">📌</span>}
              {isSolved && <span className="text-lg">✅</span>}
            </div>

            <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-3">
              {preview}
            </p>

            <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-500">
              <Link href={`/profile/${author.id}`} className="hover:text-blue-600 dark:hover:text-blue-400">
                {author.name}
              </Link>
              <span>•</span>
              <span>{createdAt}</span>
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center gap-4 text-xs text-gray-600 dark:text-gray-400 flex-shrink-0">
            <div className="text-center">
              <div className="font-semibold text-gray-900 dark:text-white">{views}</div>
              <div className="text-gray-500">views</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-gray-900 dark:text-white">{replyCount}</div>
              <div className="text-gray-500">replies</div>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
