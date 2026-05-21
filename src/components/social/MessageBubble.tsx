import React from 'react';
import Link from 'next/link';

interface MessageBubbleProps {
  id: number;
  sender: {
    id: number;
    name: string;
    avatar?: string;
  };
  content: string;
  timestamp: string;
  isOwn: boolean;
  hasAttachment?: boolean;
}

export default function MessageBubble({
  id,
  sender,
  content,
  timestamp,
  isOwn,
  hasAttachment = false
}: MessageBubbleProps) {
  return (
    <div className={`flex gap-3 mb-4 ${isOwn ? 'flex-row-reverse' : ''}`}>
      {!isOwn && (
        <img
          src={sender.avatar || `https://ui-avatars.com/api/?name=${sender.name}&background=random`}
          alt={sender.name}
          className="w-8 h-8 rounded-full flex-shrink-0"
        />
      )}

      <div className={`flex flex-col gap-1 max-w-xs ${isOwn ? 'items-end' : 'items-start'}`}>
        {!isOwn && (
          <span className="text-xs font-semibold text-gray-600 dark:text-gray-400">
            {sender.name}
          </span>
        )}

        <div
          className={`px-4 py-2 rounded-lg max-w-full ${
            isOwn
              ? 'bg-blue-600 text-white rounded-br-none'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-none'
          }`}
        >
          <p className="text-sm break-words">{content}</p>
          {hasAttachment && (
            <div className="mt-2 text-xs opacity-75">
              📎 Attachment
            </div>
          )}
        </div>

        <span className="text-xs text-gray-500 dark:text-gray-500">
          {timestamp}
        </span>
      </div>
    </div>
  );
}
