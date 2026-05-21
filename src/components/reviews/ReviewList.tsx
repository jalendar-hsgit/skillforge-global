/**
 * Component to display a list of mentor reviews
 */

import React from 'react';
import { ReviewDisplay } from './ReviewDisplay';
import { RatingStars } from './RatingStars';
import { getMentorReviews } from '@/lib/api';

interface ReviewListProps {
  mentorId: number;
  maxReviews?: number;
}

interface Review {
  id: number;
  mentor_id: number;
  session_id: number;
  student_id: number;
  rating: number;
  review_text?: string;
  tags?: string;
  created_at: string;
}

interface ReviewStats {
  total: number;
  average_rating: number;
  reviews: Review[];
}

export function ReviewList({ mentorId, maxReviews = 5 }: ReviewListProps) {
  const [reviews, setReviews] = React.useState<ReviewStats | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState('');

  React.useEffect(() => {
    const fetchReviews = async () => {
      try {
        setLoading(true);
        const data = await getMentorReviews(mentorId, maxReviews);
        setReviews(data);
        setError('');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load reviews');
      } finally {
        setLoading(false);
      }
    };

    fetchReviews();
  }, [mentorId, maxReviews]);

  if (loading) {
    return <div className="p-4 text-center text-gray-500">Loading reviews...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-600">{error}</div>;
  }

  if (!reviews || reviews.total === 0) {
    return <div className="p-4 text-center text-gray-500">No reviews yet</div>;
  }

  // Calculate rating distribution
  const ratingCounts = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
  reviews.reviews.forEach(r => {
    ratingCounts[r.rating as keyof typeof ratingCounts]++;
  });

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center gap-4 mb-4">
          <div>
            <div className="text-3xl font-bold text-gray-900">
              {reviews.average_rating.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600">out of 5</div>
          </div>
          <div className="flex-1">
            <RatingStars
              rating={reviews.average_rating}
              interactive={false}
              size="large"
              showLabel={false}
            />
            <p className="text-sm text-gray-600 mt-2">
              Based on {reviews.total} review{reviews.total !== 1 ? 's' : ''}
            </p>
          </div>
        </div>

        {/* Rating distribution */}
        <div className="space-y-2">
          {[5, 4, 3, 2, 1].map((rating) => (
            <div key={rating} className="flex items-center gap-2">
              <span className="text-sm font-medium w-8">{rating}★</span>
              <div className="flex-1 bg-gray-300 rounded-full h-2">
                <div
                  className="bg-yellow-400 h-full rounded-full transition-all"
                  style={{
                    width: `${(ratingCounts[rating as keyof typeof ratingCounts] / reviews.total) * 100}%`
                  }}
                />
              </div>
              <span className="text-sm text-gray-600 w-8">
                {ratingCounts[rating as keyof typeof ratingCounts]}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Reviews list */}
      <div className="space-y-3">
        <h3 className="font-semibold text-lg">Recent Reviews</h3>
        <div className="space-y-3">
          {reviews.reviews.map((review) => (
            <ReviewDisplay
              key={review.id}
              id={review.id}
              rating={review.rating}
              reviewText={review.review_text}
              tags={review.tags}
              createdAt={review.created_at}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
