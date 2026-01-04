'use client'

import { useState } from 'react'
import { Star, X } from 'lucide-react'
import { Button } from './Button'

interface SessionRatingModalProps {
  sessionId: number
  mentorName: string
  isOpen: boolean
  onClose: () => void
  onSubmit?: (rating: number, comment: string) => Promise<void>
}

export function SessionRatingModal({
  sessionId,
  mentorName,
  isOpen,
  onClose,
  onSubmit
}: SessionRatingModalProps) {
  const [rating, setRating] = useState(5)
  const [comment, setComment] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  if (!isOpen) return null

  const handleSubmit = async () => {
    if (rating < 1 || rating > 5) {
      setError('Please select a rating')
      return
    }

    setLoading(true)
    setError('')

    try {
      if (onSubmit) {
        await onSubmit(rating, comment)
      } else {
        // Default implementation - submit to API
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8002'}/api/v1x/sessions/${sessionId}/rate`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ rating, comment })
          }
        )

        if (!response.ok) {
          throw new Error('Failed to submit rating')
        }
      }

      setSuccess(true)
      setTimeout(() => {
        onClose()
      }, 1500)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-[#0B0A13] to-[#1a1625] border border-white/10 rounded-lg shadow-xl max-w-md w-full p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white">Rate Your Session</h2>
          <button
            onClick={onClose}
            className="text-white/60 hover:text-white transition-colors"
            aria-label="Close"
          >
            <X size={24} />
          </button>
        </div>

        {success ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-3">✨</div>
            <p className="text-white font-semibold mb-1">Thank you for rating!</p>
            <p className="text-white/60 text-sm">Your feedback helps us improve</p>
          </div>
        ) : (
          <>
            {/* Mentor Info */}
            <div className="mb-6">
              <p className="text-white/80 text-sm mb-2">Session with</p>
              <p className="text-white font-semibold">{mentorName}</p>
            </div>

            {/* Star Rating */}
            <div className="mb-6">
              <label className="text-white text-sm font-medium mb-3 block">
                How was your session?
              </label>
              <div className="flex gap-3 justify-center">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setRating(star)}
                    className="transition-transform hover:scale-110"
                  >
                    <Star
                      size={32}
                      className={`${
                        star <= rating
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'text-white/30'
                      } transition-colors`}
                    />
                  </button>
                ))}
              </div>
              <p className="text-center text-white/60 text-xs mt-2">
                {rating === 1 && 'Poor'}
                {rating === 2 && 'Fair'}
                {rating === 3 && 'Good'}
                {rating === 4 && 'Very Good'}
                {rating === 5 && 'Excellent'}
              </p>
            </div>

            {/* Comment */}
            <div className="mb-6">
              <label className="text-white text-sm font-medium mb-2 block">
                Additional feedback (optional)
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Share your thoughts about the session..."
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                rows={4}
              />
              <p className="text-white/40 text-xs mt-1">
                {comment.length}/300 characters
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-6 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3">
              <Button
                variant="secondary"
                size="md"
                onClick={onClose}
                disabled={loading}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                size="md"
                onClick={handleSubmit}
                disabled={loading}
                className="flex-1"
              >
                {loading ? 'Submitting...' : 'Submit Rating'}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
