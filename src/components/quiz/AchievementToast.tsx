/**
 * AchievementToast - Animated notification when user unlocks an achievement
 * Shows achievement icon, name, and points earned
 */
import { useEffect, useState } from 'react'

interface Achievement {
  id: string
  name: string
  description: string
  icon: string
  points: number
  category?: string
}

interface AchievementToastProps {
  achievement: Achievement
  onClose?: () => void
  duration?: number
}

export default function AchievementToast({ 
  achievement, 
  onClose, 
  duration = 5000 
}: AchievementToastProps) {
  const [show, setShow] = useState(false)
  const [sparkles, setSparkles] = useState<Array<{ id: number; x: number; y: number }>>([])
  
  useEffect(() => {
    // Animate in
    setTimeout(() => setShow(true), 100)
    
    // Generate sparkle positions
    const newSparkles = Array.from({ length: 8 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100
    }))
    setSparkles(newSparkles)
    
    // Auto close
    const timer = setTimeout(() => {
      setShow(false)
      if (onClose) setTimeout(onClose, 300)
    }, duration)
    
    return () => clearTimeout(timer)
  }, [duration, onClose])
  
  return (
    <div 
      className={`fixed top-24 right-6 z-50 transition-all duration-300 ${
        show ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-full'
      }`}
    >
      <div className="relative rounded-xl border border-yellow-500/50 bg-gradient-to-br from-yellow-900/20 to-orange-900/20 backdrop-blur-sm p-4 min-w-[280px] shadow-2xl">
        {/* Sparkle effects */}
        {sparkles.map(sparkle => (
          <div
            key={sparkle.id}
            className="absolute w-1 h-1 bg-yellow-400 rounded-full animate-ping"
            style={{
              left: `${sparkle.x}%`,
              top: `${sparkle.y}%`,
              animationDelay: `${sparkle.id * 0.1}s`,
              animationDuration: '1s'
            }}
          />
        ))}
        
        <div className="relative z-10">
          <div className="flex items-start gap-3">
            <div className="text-4xl">{achievement.icon}</div>
            <div className="flex-1">
              <div className="text-xs text-yellow-400 font-semibold mb-1">🎉 ACHIEVEMENT UNLOCKED!</div>
              <div className="font-bold text-white">{achievement.name}</div>
              <div className="text-xs text-techGray mt-1">{achievement.description}</div>
              <div className="mt-2 inline-flex items-center gap-1 text-yellow-400 text-sm font-semibold">
                <span>+{achievement.points}</span>
                <span className="text-xs">points</span>
              </div>
            </div>
            <button
              onClick={() => {
                setShow(false)
                if (onClose) setTimeout(onClose, 300)
              }}
              className="text-white/50 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
