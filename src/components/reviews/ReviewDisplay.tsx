/**
 * Component to display a single review
 */

import React from 'react';
import { RatingStars } from './RatingStars';

interface ReviewDisplayProps {
  id: number;
  rating: number;
  reviewText?: string;
  tags?: string;
  createdAt: string;
  studentName?: string;
  onDelete?: () => void;
  canDelete?: boolean;
}

export function ReviewDisplay({
  id,
  rating,
  reviewText,
  tags,
  createdAt,
  studentName,
  onDelete,
  canDelete
}: ReviewDisplayProps) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const tagList = tags ? tags.split(',').map(t => t.trim()) : [];

  return (
    <div className="border rounded-lg p-4 bg-white hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <div>
          {studentName && (
            <p className="font-medium text-gray-900">{studentName}</p>
          )}
          <p className="text-xs text-gray-500">{formatDate(createdAt)}</p>
        </div>
        {canDelete && (
          <button
            onClick={onDelete}
            className="text-red-500 hover:text-red-700 text-sm font-medium"
          >
            Delete
          </button>
        )}
      </div>

      <RatingStars rating={rating} interactive={false} size="small" showLabel={false} />

      {reviewText && (
        <p className="text-sm text-gray-700 mt-3 leading-relaxed">{reviewText}</p>
      )}

      {tagList.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {tagList.map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
