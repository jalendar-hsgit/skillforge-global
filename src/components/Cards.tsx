import React from 'react'
import Link from 'next/link'

interface StatCardProps {
  icon: React.ReactNode | string
  label: string
  value: string | number
  trend?: {
    value: number
    direction: 'up' | 'down'
  }
  href?: string
  color?: 'purple' | 'blue' | 'green' | 'orange' | 'pink'
}

export function StatCard({ icon, label, value, trend, href, color = 'purple' }: StatCardProps) {
  const colorClasses = {
    purple: 'from-purple-500/20 to-purple-600/20 border-purple-500/30',
    blue: 'from-blue-500/20 to-blue-600/20 border-blue-500/30',
    green: 'from-green-500/20 to-green-600/20 border-green-500/30',
    orange: 'from-orange-500/20 to-orange-600/20 border-orange-500/30',
    pink: 'from-pink-500/20 to-pink-600/20 border-pink-500/30'
  }

  const content = (
    <>
      <div className="flex items-start justify-between mb-4">
        <div className="text-3xl">
          {typeof icon === 'string' ? icon : icon}
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full ${
            trend.direction === 'up' 
              ? 'bg-green-500/20 text-green-400' 
              : 'bg-red-500/20 text-red-400'
          }`}>
            <span>{trend.direction === 'up' ? '↑' : '↓'}</span>
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
      <div>
        <div className="text-3xl font-bold mb-1">{value}</div>
        <div className="text-sm text-white/60">{label}</div>
      </div>
    </>
  )

  const className = `bg-gradient-to-br ${colorClasses[color]} backdrop-blur-xl rounded-xl p-6 border hover:border-white/30 transition-all hover:shadow-lg hover:shadow-${color}-500/20 hover:scale-105 transform duration-200`

  return href ? (
    <Link href={href} className={className}>
      {content}
    </Link>
  ) : (
    <div className={className}>
      {content}
    </div>
  )
}

interface FeatureCardProps {
  icon: string
  title: string
  description: string
  href?: string
  badge?: string
  onClick?: () => void
}

export function FeatureCard({ icon, title, description, href, badge, onClick }: FeatureCardProps) {
  const content = (
    <div className="h-full flex flex-col">
      <div className="flex items-start justify-between mb-4">
        <div className="text-4xl">{icon}</div>
        {badge && (
          <span className="text-xs font-semibold px-2 py-1 rounded-full bg-gradient-to-r from-forgePurple to-neuralBlue">
            {badge}
          </span>
        )}
      </div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-white/60 text-sm flex-1">{description}</p>
      <div className="mt-4 text-sm text-forgePurple font-medium flex items-center gap-2">
        Learn more <span>→</span>
      </div>
    </div>
  )

  const className = "bg-white/5 backdrop-blur-xl rounded-xl p-6 border border-white/10 hover:border-white/30 hover:bg-white/10 transition-all hover:shadow-xl hover:shadow-purple-500/20 cursor-pointer transform hover:scale-105 duration-200"

  if (href) {
    return (
      <Link href={href} className={className}>
        {content}
      </Link>
    )
  }

  return (
    <div className={className} onClick={onClick}>
      {content}
    </div>
  )
}

interface ProgressCardProps {
  title: string
  subtitle?: string
  progress: number
  icon?: string
  href?: string
  stats?: { label: string; value: string | number }[]
}

export function ProgressCard({ title, subtitle, progress, icon, href, stats }: ProgressCardProps) {
  const content = (
    <>
      <div className="flex items-start gap-4 mb-4">
        {icon && <div className="text-3xl flex-shrink-0">{icon}</div>}
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold mb-1 truncate">{title}</h3>
          {subtitle && <p className="text-sm text-white/60">{subtitle}</p>}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-white/60">Progress</span>
          <span className="font-semibold">{progress}%</span>
        </div>
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-forgePurple to-neuralBlue rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Stats */}
      {stats && stats.length > 0 && (
        <div className="flex items-center gap-4 pt-4 border-t border-white/10">
          {stats.map((stat, index) => (
            <div key={index} className="flex-1">
              <div className="text-lg font-bold">{stat.value}</div>
              <div className="text-xs text-white/60">{stat.label}</div>
            </div>
          ))}
        </div>
      )}
    </>
  )

  const className = "bg-gradient-to-br from-white/5 to-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/10 hover:border-white/30 transition-all hover:shadow-lg hover:shadow-purple-500/10"

  return href ? (
    <Link href={href} className={className}>
      {content}
    </Link>
  ) : (
    <div className={className}>
      {content}
    </div>
  )
}

interface AlertCardProps {
  variant: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  action?: React.ReactNode
  onDismiss?: () => void
}

export function AlertCard({ variant, title, message, action, onDismiss }: AlertCardProps) {
  const variants = {
    info: {
      bg: 'from-blue-500/20 to-blue-600/10',
      border: 'border-blue-500/30',
      icon: 'ℹ️'
    },
    success: {
      bg: 'from-green-500/20 to-green-600/10',
      border: 'border-green-500/30',
      icon: '✅'
    },
    warning: {
      bg: 'from-orange-500/20 to-orange-600/10',
      border: 'border-orange-500/30',
      icon: '⚠️'
    },
    error: {
      bg: 'from-red-500/20 to-red-600/10',
      border: 'border-red-500/30',
      icon: '❌'
    }
  }

  const config = variants[variant]

  return (
    <div className={`bg-gradient-to-br ${config.bg} backdrop-blur-xl rounded-xl p-6 border ${config.border}`}>
      <div className="flex items-start gap-4">
        <div className="text-3xl flex-shrink-0">{config.icon}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4 mb-2">
            <h3 className="text-lg font-semibold">{title}</h3>
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="text-white/60 hover:text-white transition-colors"
              >
                ✕
              </button>
            )}
          </div>
          <p className="text-sm text-white/70 mb-4">{message}</p>
          {action && <div>{action}</div>}
        </div>
      </div>
    </div>
  )
}

interface ActionCardProps {
  icon: string
  title: string
  description: string
  buttonText: string
  buttonHref?: string
  buttonOnClick?: () => void
  variant?: 'default' | 'gradient'
}

export function ActionCard({ 
  icon, 
  title, 
  description, 
  buttonText, 
  buttonHref, 
  buttonOnClick,
  variant = 'default' 
}: ActionCardProps) {
  const button = (
    <button
      onClick={buttonOnClick}
      className={`w-full mt-4 px-6 py-3 rounded-lg font-semibold transition-all transform hover:scale-105 ${
        variant === 'gradient'
          ? 'bg-gradient-to-r from-forgePurple to-neuralBlue hover:shadow-lg hover:shadow-purple-500/50'
          : 'bg-white/10 hover:bg-white/20 border border-white/20'
      }`}
    >
      {buttonText} →
    </button>
  )

  return (
    <div className="bg-gradient-to-br from-white/5 to-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/10">
      <div className="text-5xl mb-4">{icon}</div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-white/60 text-sm mb-4">{description}</p>
      {buttonHref ? (
        <Link href={buttonHref}>
          {button}
        </Link>
      ) : (
        button
      )}
    </div>
  )
}
