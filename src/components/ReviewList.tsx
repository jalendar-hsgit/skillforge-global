import { useState } from 'react';
import { Star, ThumbsUp, ThumbsDown, Loader2, Trash2 } from 'lucide-react';

interface Review {
  id: number;
  rating: number;
  title: string;
  text: string;
  reviewer_name: string;
  reviewer_avatar: string | null;
  is_verified_purchase: boolean;
  helpful_count: number;
  unhelpful_count: number;
  created_at: string;
  seller_response?: string;
  seller_response_at?: string;
}

interface ReviewListProps {
  productId: number;
  reviews: Review[];
  loading?: boolean;
  totalReviews?: number;
  averageRating?: number;
  ratingDistribution?: Record<string, number>;
  onLoadMore?: () => void;
  hasMore?: boolean;
  onHelpful?: (reviewId: number, isHelpful: boolean) => void;
  onDelete?: (reviewId: number) => void;
  currentUserId?: number;
}

export default function ReviewList({
  productId,
  reviews,
  loading = false,
  totalReviews = 0,
  averageRating = 0,
  ratingDistribution = {},
  onLoadMore,
  hasMore = false,
  onHelpful,
  onDelete,
  currentUserId
}: ReviewListProps) {
  const [votingReview, setVotingReview] = useState<number | null>(null);
  const [userVotes, setUserVotes] = useState<Record<number, boolean | null>>({});
  const [deletingReview, setDeletingReview] = useState<number | null>(null);

  const handleHelpful = async (reviewId: number, isHelpful: boolean) => {
    if (votingReview) return;

    try {
      setVotingReview(reviewId);

      const token = localStorage.getItem('token');
      if (!token) {
        alert('Please login to vote');
        return;
      }

      const response = await fetch(
        `http://localhost:8001/api/v1x/marketplace/products/${productId}/reviews/${reviewId}/helpful?is_helpful=${isHelpful}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to vote');
      }

      const data = await response.json();
      setUserVotes(prev => ({
        ...prev,
        [reviewId]: data.user_vote
      }));

      onHelpful?.(reviewId, isHelpful);
    } catch (error) {
      console.error('Error voting:', error);
      alert('Error voting on review');
    } finally {
      setVotingReview(null);
    }
  };

  const handleDelete = async (reviewId: number) => {
    if (!confirm('Are you sure you want to delete this review?')) {
      return;
    }

    try {
      setDeletingReview(reviewId);

      const token = localStorage.getItem('token');
      if (!token) {
        alert('Please login to delete review');
        return;
      }

      const response = await fetch(
        `http://localhost:8001/api/v1x/marketplace/products/${productId}/reviews/${reviewId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to delete review');
      }

      onDelete?.(reviewId);
    } catch (error) {
      console.error('Error deleting:', error);
      alert('Error deleting review');
    } finally {
      setDeletingReview(null);
    }
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map(star => (
          <Star
            key={star}
            size={16}
            className={star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
          />
        ))}
      </div>
    );
  };

  const ratingPercentage = (rating: number) => {
    if (totalReviews === 0) return 0;
    return Math.round(((ratingDistribution?.[rating] || 0) / totalReviews) * 100);
  };

  return (
    <div className="space-y-6">
      {/* Rating Summary */}
      {totalReviews > 0 && (
        <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Average Rating */}
            <div className="flex items-center">
              <div>
                <p className="text-5xl font-bold text-gray-900">{averageRating.toFixed(1)}</p>
                <div className="flex gap-1 my-2">
                  {[1, 2, 3, 4, 5].map(star => (
                    <Star
                      key={star}
                      size={20}
                      className={star <= Math.round(averageRating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
                    />
                  ))}
                </div>
                <p className="text-gray-600 text-sm">
                  Based on {totalReviews} review{totalReviews !== 1 ? 's' : ''}
                </p>
              </div>
            </div>

            {/* Rating Distribution */}
            <div className="space-y-2">
              {[5, 4, 3, 2, 1].map(rating => (
                <div key={rating} className="flex items-center gap-3">
                  <div className="flex gap-1 w-12">
                    {[1, 2, 3, 4, 5].map(star => (
                      <Star
                        key={star}
                        size={14}
                        className={star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
                      />
                    ))}
                  </div>
                  <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-yellow-400 h-full transition-all"
                      style={{ width: `${ratingPercentage(rating)}%` }}
                    />
                  </div>
                  <p className="text-gray-600 text-sm w-12 text-right">
                    {ratingPercentage(rating)}%
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Reviews List */}
      <div className="space-y-4">
        {loading && reviews.length === 0 ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 size={32} className="animate-spin text-gray-400" />
          </div>
        ) : reviews.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-600">No reviews yet</p>
          </div>
        ) : (
          reviews.map(review => (
            <div
              key={review.id}
              className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3 flex-1">
                  {review.reviewer_avatar && (
                    <img
                      src={review.reviewer_avatar}
                      alt={review.reviewer_name}
                      className="w-10 h-10 rounded-full bg-gray-200"
                    />
                  )}
                  <div>
                    <p className="font-medium text-gray-900">{review.reviewer_name}</p>
                    <div className="flex items-center gap-2">
                      {renderStars(review.rating)}
                      <span className="text-xs text-gray-500">
                        {new Date(review.created_at).toLocaleDateString()}
                      </span>
                      {review.is_verified_purchase && (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                          Verified Purchase
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                {currentUserId && currentUserId === review.id && (
                  <button
                    onClick={() => handleDelete(review.id)}
                    disabled={deletingReview === review.id}
                    className="text-gray-400 hover:text-red-600 transition-colors"
                  >
                    {deletingReview === review.id ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <Trash2 size={16} />
                    )}
                  </button>
                )}
              </div>

              {/* Content */}
              {review.title && (
                <h4 className="font-semibold text-gray-900 mb-2">{review.title}</h4>
              )}
              {review.text && (
                <p className="text-gray-700 mb-4 whitespace-pre-wrap">{review.text}</p>
              )}

              {/* Seller Response */}
              {review.seller_response && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                  <p className="text-sm font-medium text-blue-900 mb-1">Seller Response:</p>
                  <p className="text-sm text-blue-800">{review.seller_response}</p>
                  {review.seller_response_at && (
                    <p className="text-xs text-blue-600 mt-1">
                      {new Date(review.seller_response_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
              )}

              {/* Helpful Votes */}
              <div className="flex items-center gap-4 text-sm">
                <span className="text-gray-600">Was this helpful?</span>
                <button
                  onClick={() => handleHelpful(review.id, true)}
                  disabled={votingReview === review.id}
                  className={`flex items-center gap-1 px-3 py-1 rounded-lg transition-colors ${
                    userVotes[review.id] === true
                      ? 'bg-green-100 text-green-700'
                      : 'hover:bg-gray-100 text-gray-600'
                  } ${votingReview === review.id ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <ThumbsUp size={16} />
                  <span>{review.helpful_count}</span>
                </button>
                <button
                  onClick={() => handleHelpful(review.id, false)}
                  disabled={votingReview === review.id}
                  className={`flex items-center gap-1 px-3 py-1 rounded-lg transition-colors ${
                    userVotes[review.id] === false
                      ? 'bg-red-100 text-red-700'
                      : 'hover:bg-gray-100 text-gray-600'
                  } ${votingReview === review.id ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <ThumbsDown size={16} />
                  <span>{review.unhelpful_count}</span>
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Load More */}
      {hasMore && !loading && (
        <button
          onClick={onLoadMore}
          className="w-full py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
        >
          Load More Reviews
        </button>
      )}

      {loading && reviews.length > 0 && (
        <div className="flex items-center justify-center py-4">
          <Loader2 size={24} className="animate-spin text-blue-600" />
        </div>
      )}
    </div>
  );
}
