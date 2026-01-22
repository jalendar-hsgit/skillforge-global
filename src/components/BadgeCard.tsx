/**
 * Badge Card Component
 * Displays a single badge with rarity level and details
 */

import { Trophy } from 'lucide-react'

interface BadgeCardProps {
  id: number
  name: string
  description: string
  icon_url?: string
  icon_emoji?: string
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary'
  points_value?: number
  is_earned?: boolean
  earned_at?: string
  onClick?: () => void
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

const rarityStyles = {
  common: {
    bg: 'from-gray-600/20 to-gray-700/20',
    border: 'border-gray-500/30',
    text: 'text-gray-300',
    badge: 'bg-gray-600/30 text-gray-200',
    glow: 'shadow-gray-500/10'
  },
  uncommon: {
    bg: 'from-green-600/20 to-green-700/20',
    border: 'border-green-500/30',
    text: 'text-green-300',
    badge: 'bg-green-600/30 text-green-200',
    glow: 'shadow-green-500/10'
  },
  rare: {
    bg: 'from-blue-600/20 to-blue-700/20',
    border: 'border-blue-500/30',
    text: 'text-blue-300',
    badge: 'bg-blue-600/30 text-blue-200',
    glow: 'shadow-blue-500/10'
  },
  epic: {
    bg: 'from-purple-600/20 to-purple-700/20',
    border: 'border-purple-500/30',
    text: 'text-purple-300',
    badge: 'bg-purple-600/30 text-purple-200',
    glow: 'shadow-purple-500/10'
  },
  legendary: {
    bg: 'from-yellow-600/20 to-yellow-700/20',
    border: 'border-yellow-500/30',
    text: 'text-yellow-300',
    badge: 'bg-yellow-600/30 text-yellow-200',
    glow: 'shadow-yellow-500/10'
  }
}

const sizeStyles = {
  sm: 'w-16 h-16 text-lg',
  md: 'w-24 h-24 text-3xl',
  lg: 'w-32 h-32 text-5xl'
}

const sizeTextStyles = {
  sm: {
    title: 'text-sm font-semibold',
    description: 'text-xs',
    points: 'text-xs'
  },
  md: {
    title: 'text-base font-semibold',
    description: 'text-sm',
    points: 'text-sm'
  },
  lg: {
    title: 'text-lg font-bold',
    description: 'text-base',
    points: 'text-base'
  }
}

export default function BadgeCard({
  id,
  name,
  description,
  icon_url,
  icon_emoji,
  rarity,
  points_value = 0,
  is_earned = false,
  earned_at,
  onClick,
  className = '',
  size = 'md'
}: BadgeCardProps) {
  const styles = rarityStyles[rarity]
  const textSizes = sizeTextStyles[size]
  const iconSize = sizeStyles[size]

  return (
    <div
      onClick={onClick}
      className={`rounded-lg border-2 p-4 transition backdrop-blur-sm ${
        is_earned
          ? `bg-gradient-to-br ${styles.bg} ${styles.border} cursor-pointer hover:shadow-lg ${styles.glow}`
          : 'bg-white/5 border-white/10 opacity-60'
      } ${onClick ? 'cursor-pointer hover:shadow-md' : ''} ${className}`}
    >
      {/* Badge Icon */}
      <div className='flex justify-center mb-3'>
        {icon_url ? (
          <img
            src={icon_url}
            alt={name}
            className={`${iconSize} rounded-full object-cover border border-white/20`}
          />
        ) : (
          <div className={`${iconSize} bg-gradient-to-br ${styles.bg} rounded-full flex items-center justify-center ${styles.text}`}>
            {icon_emoji || <Trophy className='w-1/2 h-1/2' />}
          </div>
        )}
      </div>

      {/* Rarity Badge */}
      <div className='flex justify-center mb-2'>
        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${styles.badge} capitalize backdrop-blur-sm border border-white/10`}>
          {rarity}
        </span>
      </div>

      {/* Badge Name */}
      <h3 className={`${textSizes.title} text-center ${styles.text} mb-1`}>
        {name}
      </h3>

      {/* Badge Description */}
      <p className={`${textSizes.description} text-white/60 text-center mb-2 line-clamp-2`}>
        {description}
      </p>

      {/* Points */}
      {points_value > 0 && (
        <div className={`${textSizes.points} text-center ${styles.text} font-semibold`}>
          +{points_value} points
        </div>
      )}

      {/* Earned Date */}
      {is_earned && earned_at && (
        <div className={`${textSizes.description} text-white/50 text-center mt-2 text-xs`}>
          Earned {new Date(earned_at).toLocaleDateString()}
        </div>
      )}

      {/* Locked Badge Indicator */}
      {!is_earned && (
        <div className='text-center text-xs text-white/50 font-medium mt-2'>
          Locked
        </div>
      )}
    </div>
  )
}
