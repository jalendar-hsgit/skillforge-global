import React from 'react';
import Link from 'next/link';

interface NotificationItemProps {
  id: number;
  type: 'mention' | 'reply' | 'follow' | 'like' | 'message';
  actor: {
    id: number;
    name: string;
    avatar?: string;
  };
  action: string;
  target?: string;
  timestamp: string;
  isRead: boolean;
  actionUrl?: string;
}

const iconMap = {
  mention: '👤',
  reply: '💬',
  follow: '➕',
  like: '❤️',
  message: '📧'
};

const colorMap = {
  mention: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
  reply: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
  follow: 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800',
  like: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
  message: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
};

export default function NotificationItem({
  id,
  type,
  actor,
  action,
  target,
  timestamp,
  isRead,
  actionUrl = '#'
}: NotificationItemProps) {
  return (
    <Link href={actionUrl}>
      <div
        className={`block p-4 rounded-lg border ${colorMap[type]} ${
          !isRead ? 'bg-opacity-100' : 'bg-opacity-50'
        } transition-all hover:shadow-md cursor-pointer`}
      >
        <div className="flex gap-3">
          <img
            src={actor.avatar || `https://ui-avatars.com/api/?name=${actor.name}&background=random`}
            alt={actor.name}
            className="w-10 h-10 rounded-full flex-shrink-0"
          />

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg">{iconMap[type]}</span>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">
                {actor.name}
              </p>
              {!isRead && (
                <span className="w-2 h-2 rounded-full bg-blue-600 ml-auto"></span>
              )}
            </div>

            <p className="text-sm text-gray-700 dark:text-gray-300">
              {action}
              {target && (
                <span className="font-semibold ml-1 text-gray-900 dark:text-white">
                  "{target}"
                </span>
              )}
            </p>

            <span className="text-xs text-gray-500 dark:text-gray-500 mt-1 block">
              {timestamp}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}
