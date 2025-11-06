/**
 * QuizTimer - Countdown timer for quiz sessions
 * Shows remaining time with color-coded visual feedback
 */
import { useEffect, useState } from 'react'

interface QuizTimerProps {
  totalSeconds: number
  onTimeUp?: () => void
  paused?: boolean
}

export default function QuizTimer({ totalSeconds, onTimeUp, paused = false }: QuizTimerProps) {
  const [remaining, setRemaining] = useState(totalSeconds)
  
  useEffect(() => {
    setRemaining(totalSeconds)
  }, [totalSeconds])
  
  useEffect(() => {
    if (paused || remaining <= 0) return
    
    const timer = setInterval(() => {
      setRemaining(prev => {
        if (prev <= 1) {
          onTimeUp?.()
          return 0
        }
        return prev - 1
      })
    }, 1000)
    
    return () => clearInterval(timer)
  }, [remaining, paused, onTimeUp])
  
  const minutes = Math.floor(remaining / 60)
  const seconds = remaining % 60
  const percentage = (remaining / totalSeconds) * 100
  
  // Color coding: green > 50%, yellow 20-50%, red < 20%
  const color = percentage > 50 
    ? 'text-green-400' 
    : percentage > 20 
      ? 'text-yellow-400' 
      : 'text-red-400'
  
  const barColor = percentage > 50
    ? 'bg-green-500'
    : percentage > 20
      ? 'bg-yellow-500'
      : 'bg-red-500'
  
  return (
    <div className="fixed top-20 right-6 z-50 rounded-lg border border-white/10 bg-black/80 backdrop-blur-sm p-4 min-w-[140px]">
      <div className="text-xs text-techGray mb-1">Time Remaining</div>
      <div className={`text-2xl font-bold ${color}`}>
        {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
      </div>
      <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
        <div 
          className={`h-full ${barColor} transition-all duration-1000`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
