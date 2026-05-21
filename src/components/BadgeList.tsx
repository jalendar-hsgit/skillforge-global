/**
 * Badge List Component
 * Displays a collection of badges for user achievements
 */

import { useState, useEffect } from 'react'
import BadgeCard from './BadgeCard'
import { LoadingSpinner } from './LoadingSpinner'

interface Badge {
  id: number
  name: string
  description: string
  icon_url?: string
  icon_emoji?: string
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary'
  points_value?: number
  is_earned?: boolean
  earned_at?: string
}

interface BadgeListProps {
  userId?: number // If not provided, uses current user
  className?: string
  showEarned?: boolean
  showLocked?: boolean
  columns?: 2 | 3 | 4 | 5 | 6
  onBadgeClick?: (badge: Badge) => void
}

const columnStyles = {
  2: 'grid-cols-2',
  3: 'grid-cols-3',
  4: 'grid-cols-4',
  5: 'grid-cols-5',
  6: 'grid-cols-6'
}

export default function BadgeList({
  userId,
  className = '',
  showEarned = true,
  showLocked = true,
  columns = 4,
  onBadgeClick
}: BadgeListProps) {
  const [badges, setBadges] = useState<Badge[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchBadges = async () => {
      try {
        setLoading(true)
        const url = userId
          ? `/api/v1x/badges/user/earned?user_id=${userId}`
          : '/api/v1x/badges/user/earned'

        const response = await fetch(url, {
          credentials: 'include'
        })

        if (!response.ok) {
          throw new Error(`Failed to fetch badges: ${response.statusText}`)
        }

        const data = await response.json()
        
        // Mark earned badges and filter based on settings
        let filteredBadges = Array.isArray(data) ? data : data.badges || []
        
        if (!showEarned) {
          filteredBadges = filteredBadges.filter((b: Badge) => !b.is_earned)
        }
        
        if (!showLocked) {
          filteredBadges = filteredBadges.filter((b: Badge) => b.is_earned)
        }

        setBadges(filteredBadges)
        setError(null)
      } catch (err) {
        console.error('Error fetching badges:', err)
        setError(err instanceof Error ? err.message : 'Failed to load badges')
        setBadges([])
      } finally {
        setLoading(false)
      }
    }

    fetchBadges()
  }, [userId, showEarned, showLocked])

  if (loading) {
    return (
      <div className='flex justify-center items-center py-12'>
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className='p-6 rounded-lg border border-red-500/20 bg-red-500/10 backdrop-blur-sm'>
        <p className='text-red-300 text-sm'>Error loading badges: {error}</p>
      </div>
    )
  }

  if (badges.length === 0) {
    return (
      <div className='text-center py-12'>
        <p className='text-white/60'>
          {showEarned && !showLocked
            ? 'No badges earned yet. Keep working to unlock achievements!'
            : 'No badges available.'}
        </p>
      </div>
    )
  }

  // Separate earned and locked badges
  const earnedBadges = badges.filter(b => b.is_earned)
  const lockedBadges = badges.filter(b => !b.is_earned)

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Earned Badges Section */}
      {showEarned && earnedBadges.length > 0 && (
        <div>
          <h3 className='text-lg font-semibold mb-4 text-white'>
            Earned Badges ({earnedBadges.length})
          </h3>
          <div className={`grid ${columnStyles[columns]} gap-4`}>
            {earnedBadges.map(badge => (
              <BadgeCard
                key={badge.id}
                {...badge}
                is_earned={true}
                onClick={() => onBadgeClick?.(badge)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Locked Badges Section */}
      {showLocked && lockedBadges.length > 0 && (
        <div>
          <h3 className='text-lg font-semibold mb-4 text-white'>
            Locked Badges ({lockedBadges.length})
          </h3>
          <div className={`grid ${columnStyles[columns]} gap-4`}>
            {lockedBadges.map(badge => (
              <BadgeCard
                key={badge.id}
                {...badge}
                is_earned={false}
                onClick={() => onBadgeClick?.(badge)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
