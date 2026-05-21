/**
 * Form component for submitting mentor reviews
 * Collects rating, title, comment, and tags
 */

import React from 'react';
import { RatingStars } from './RatingStars';
import { submitMentorReview } from '@/lib/api';

interface ReviewFormProps {
  sessionId: number;
  mentorId: number;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function ReviewForm({ sessionId, mentorId, onSuccess, onCancel }: ReviewFormProps) {
  const [rating, setRating] = React.useState(5);
  const [title, setTitle] = React.useState('');
  const [comment, setComment] = React.useState('');
  const [tags, setTags] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Please enter a review title');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await submitMentorReview({
        session_id: sessionId,
        rating,
        review_text: comment || undefined,
        tags: tags || undefined
      });

      setTitle('');
      setComment('');
      setTags('');
      setRating(5);
      onSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit review');
    } finally {
      setLoading(false);
    }
  };

  const commonTags = ['knowledgeable', 'patient', 'helpful', 'responsive', 'clear-explanations'];

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-gray-50 rounded-lg">
      <h3 className="text-lg font-semibold">Leave a Review</h3>

      {error && (
        <div className="p-3 bg-red-100 text-red-700 rounded text-sm">
          {error}
        </div>
      )}

      {/* Rating */}
      <div>
        <label className="block text-sm font-medium mb-2">Rating</label>
        <RatingStars
          rating={rating}
          onRatingChange={setRating}
          interactive
          size="large"
          showLabel
        />
      </div>

      {/* Title */}
      <div>
        <label className="block text-sm font-medium mb-2">Review Title *</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Brief summary of your experience"
          maxLength={100}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <span className="text-xs text-gray-500">{title.length}/100</span>
      </div>

      {/* Comment */}
      <div>
        <label className="block text-sm font-medium mb-2">Detailed Comment</label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Share your detailed feedback (optional)"
          maxLength={500}
          rows={4}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <span className="text-xs text-gray-500">{comment.length}/500</span>
      </div>

      {/* Tags */}
      <div>
        <label className="block text-sm font-medium mb-2">Tags</label>
        <div className="space-y-2">
          <div className="flex flex-wrap gap-2">
            {commonTags.map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => {
                  const tagsList = tags.split(',').map(t => t.trim()).filter(Boolean);
                  if (tagsList.includes(tag)) {
                    setTags(tagsList.filter(t => t !== tag).join(', '));
                  } else {
                    tagsList.push(tag);
                    setTags(tagsList.join(', '));
                  }
                }}
                className={`px-3 py-1 rounded-full text-sm transition-colors ${
                  tags.split(',').map(t => t.trim()).includes(tag)
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="Custom tags (comma-separated)"
            className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-2">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md font-medium disabled:bg-gray-400"
        >
          {loading ? 'Submitting...' : 'Submit Review'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
