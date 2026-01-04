import Head from 'next/head'
import DashboardLayout from '@/components/DashboardLayout'
import DashboardStatCard from '@/components/DashboardStatCard'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { DashboardGridSkeleton, DashboardListSkeleton } from '@/components/DashboardSkeletons'

type Review = {
  id: number
  student_id: number
  session_id: number
  rating: number
  comment: string
  created_at: string
}

export default function MentorReviews() {
  const router = useRouter()
  const [reviews, setReviews] = useState<Review[]>([])
  const [total, setTotal] = useState(0)
  const [avgRating, setAvgRating] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadReviews()
  }, [])

  async function loadReviews() {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/mentor-portal/dashboard/reviews`,
        { credentials: 'include' }
      )

      if (res.status === 401) {
        router.push('/login?redirect=/mentors/dashboard/reviews')
        return
      }

      if (res.ok) {
        const data = await res.json()
        setReviews(data.reviews || [])
        setTotal(data.total || 0)
        setAvgRating(data.average_rating || 0)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const renderStars = (rating: number) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <span key={star} className={star <= rating ? 'text-yellow-400' : 'text-gray-600'}>
            ⭐
          </span>
        ))}
      </div>
    )
  }

  const getRatingColor = (rating: number) => {
    if (rating >= 4.5) return 'text-green-400'
    if (rating >= 3.5) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <DashboardLayout
      title="Student Reviews"
      subtitle={`Average Rating: ${avgRating.toFixed(1)} ⭐ (${total} reviews)`}
      breadcrumbs={[
        { label: 'Dashboard', href: '/mentors/dashboard' },
        { label: 'Reviews' }
      ]}
    >
      <Head>
        <title>Reviews – Mentor Dashboard</title>
      </Head>

      <div className="space-y-8">
        {/* Stats Header */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <DashboardStatCard
            label="Average Rating"
            value={`${avgRating.toFixed(1)} ⭐`}
            color="purple"
          />
          <DashboardStatCard
            label="Total Reviews"
            value={total.toString()}
            color="blue"
          />
          <DashboardStatCard
            label="5-Star Reviews"
            value={reviews.filter(r => r.rating === 5).length.toString()}
            color="green"
          />
        </div>

        {/* Reviews List */}
        {loading ? (
          <div>
            <DashboardGridSkeleton count={3} />
            <DashboardListSkeleton count={5} />
          </div>
        ) : reviews.length === 0 ? (
          <div className="bg-white/5 border border-white/10 rounded-xl p-12 text-center">
            <div className="text-6xl mb-4">⭐</div>
            <h3 className="text-xl font-semibold text-white mb-2">No reviews yet</h3>
            <p className="text-techGray">
              Complete sessions to receive student reviews
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {reviews.map((review) => (
              <div
                key={review.id}
                className="bg-white/5 border border-white/10 rounded-xl p-6 hover:border-techBlue/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-techBlue to-forgePurple flex items-center justify-center text-white font-bold">
                      S{review.student_id}
                    </div>
                    <div>
                      <div className="text-white font-medium mb-1">Student #{review.student_id}</div>
                      <div className="text-xs text-techGray">
                        {new Date(review.created_at).toLocaleDateString()} • Session #{review.session_id}
                      </div>
                    </div>
                  </div>
                  {renderStars(review.rating)}
                </div>

                {review.comment && (
                  <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                    <p className="text-white leading-relaxed">{review.comment}</p>
                  </div>
                )}

                {!review.comment && (
                  <div className="text-techGray italic text-sm">No written comment</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
