/**
 * Video Progress Bar Component
 * Displays progress percentage for video courses with visual bar
 */

import { CheckCircle2, Clock } from 'lucide-react'

interface VideoProgressBarProps {
  progress: number // 0-100
  isCompleted: boolean
  showLabel?: boolean
  className?: string
  height?: 'sm' | 'md' | 'lg'
}

export default function VideoProgressBar({
  progress,
  isCompleted,
  showLabel = true,
  className = '',
  height = 'md'
}: VideoProgressBarProps) {
  const heightMap = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4'
  }

  const progressColor = isCompleted
    ? 'bg-green-500'
    : progress >= 75
    ? 'bg-blue-500'
    : progress >= 50
    ? 'bg-amber-500'
    : progress >= 25
    ? 'bg-orange-500'
    : 'bg-red-500'

  const textColor = isCompleted
    ? 'text-green-600'
    : progress >= 75
    ? 'text-blue-600'
    : progress >= 50
    ? 'text-amber-600'
    : progress >= 25
    ? 'text-orange-600'
    : 'text-red-600'

  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      {showLabel && (
        <div className='flex items-center justify-between'>
          <div className='flex items-center gap-2'>
            {isCompleted ? (
              <>
                <CheckCircle2 className='w-5 h-5 text-green-500' />
                <span className='text-sm font-semibold text-green-600'>
                  Completed
                </span>
              </>
            ) : (
              <>
                <Clock className='w-5 h-5 text-gray-500' />
                <span className={`text-sm font-semibold ${textColor}`}>
                  {progress}% Complete
                </span>
              </>
            )}
          </div>
          {!isCompleted && (
            <span className={`text-xs font-medium ${textColor}`}>
              {progress}%
            </span>
          )}
        </div>
      )}

      {/* Progress bar background */}
      <div className={`w-full bg-gray-200 rounded-full overflow-hidden ${heightMap[height]}`}>
        {/* Progress fill */}
        <div
          className={`${progressColor} ${heightMap[height]} rounded-full transition-all duration-300 ease-out`}
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>

      {/* Optional: Show milestones */}
      {showLabel && (
        <div className='flex justify-between text-xs text-gray-500 px-1'>
          <span>0%</span>
          <span>50%</span>
          <span>100%</span>
        </div>
      )}
    </div>
  )
}
