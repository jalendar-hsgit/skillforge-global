import { useState } from 'react';
import { Star, Loader2 } from 'lucide-react';

interface ReviewFormProps {
  productId: number;
  onSubmit: (rating: number, title: string, text: string) => void;
  loading?: boolean;
  error?: string;
  onClose?: () => void;
}

export default function ReviewForm({
  productId,
  onSubmit,
  loading = false,
  error,
  onClose
}: ReviewFormProps) {
  const [rating, setRating] = useState(5);
  const [hoverRating, setHoverRating] = useState(0);
  const [title, setTitle] = useState('');
  const [text, setText] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim() || !text.trim()) {
      alert('Please fill in all fields');
      return;
    }

    onSubmit(rating, title, text);
    setSubmitted(true);
  };

  if (submitted && !error) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <h3 className="text-lg font-semibold text-green-900 mb-2">
          Thank you for your review!
        </h3>
        <p className="text-green-700 mb-4">
          Your review has been submitted and will be displayed after moderation.
        </p>
        {onClose && (
          <button
            onClick={onClose}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
          >
            Close
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
      <h3 className="text-xl font-semibold text-gray-900 mb-4">Write a Review</h3>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Rating */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Rating
          </label>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map(num => (
              <button
                key={num}
                type="button"
                onClick={() => setRating(num)}
                onMouseEnter={() => setHoverRating(num)}
                onMouseLeave={() => setHoverRating(0)}
                className="transition-transform hover:scale-110"
              >
                <Star
                  size={32}
                  className={`${
                    (hoverRating || rating) >= num
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-300'
                  } transition-colors`}
                />
              </button>
            ))}
          </div>
          <p className="mt-2 text-sm text-gray-600">
            {rating === 1 && 'Poor'}
            {rating === 2 && 'Fair'}
            {rating === 3 && 'Good'}
            {rating === 4 && 'Very Good'}
            {rating === 5 && 'Excellent'}
          </p>
        </div>

        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
            Review Title
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={e => setTitle(e.target.value)}
            maxLength={200}
            placeholder="Summarize your experience"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <p className="mt-1 text-sm text-gray-500">
            {title.length}/200 characters
          </p>
        </div>

        {/* Review Text */}
        <div>
          <label htmlFor="text" className="block text-sm font-medium text-gray-700 mb-2">
            Your Review
          </label>
          <textarea
            id="text"
            value={text}
            onChange={e => setText(e.target.value)}
            maxLength={2000}
            rows={6}
            placeholder="Share your honest thoughts about this product..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            disabled={loading}
          />
          <p className="mt-1 text-sm text-gray-500">
            {text.length}/2000 characters
          </p>
        </div>

        {/* Buttons */}
        <div className="flex gap-3 justify-end">
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading && <Loader2 size={16} className="animate-spin" />}
            Submit Review
          </button>
        </div>
      </form>
    </div>
  );
}
