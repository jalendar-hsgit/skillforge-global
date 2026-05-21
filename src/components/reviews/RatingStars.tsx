/**
 * Interactive 5-star rating component
 * Used for viewing and submitting mentor ratings
 */

import React from 'react';

interface RatingStarsProps {
  rating: number;
  onRatingChange?: (rating: number) => void;
  interactive?: boolean;
  size?: 'small' | 'medium' | 'large';
  showLabel?: boolean;
}

export function RatingStars({
  rating,
  onRatingChange,
  interactive = false,
  size = 'medium',
  showLabel = true
}: RatingStarsProps) {
  const [hoverRating, setHoverRating] = React.useState(0);

  const sizeClass = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg'
  }[size];

  const getStarColor = (starNum: number) => {
    const displayRating = interactive && hoverRating ? hoverRating : rating;
    return starNum <= displayRating ? 'text-yellow-400' : 'text-gray-300';
  };

  return (
    <div className="flex items-center gap-2">
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => interactive && onRatingChange?.(star)}
            onMouseEnter={() => interactive && setHoverRating(star)}
            onMouseLeave={() => interactive && setHoverRating(0)}
            disabled={!interactive}
            className={`${sizeClass} ${getStarColor(star)} ${
              interactive ? 'cursor-pointer hover:scale-110' : ''
            } transition-transform`}
          >
            ★
          </button>
        ))}
      </div>
      {showLabel && (
        <span className="text-sm text-gray-600">
          {rating.toFixed(1)} / 5.0
        </span>
      )}
    </div>
  );
}
