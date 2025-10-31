import React from 'react'

interface PageHeaderProps {
  title: string
  subtitle?: string
  icon?: string
  actions?: React.ReactNode
  breadcrumbs?: { label: string; href?: string }[]
}

export function PageHeader({ title, subtitle, icon, actions, breadcrumbs }: PageHeaderProps) {
  return (
    <div className="mb-8">
      {/* Breadcrumbs */}
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav className="flex items-center gap-2 text-sm text-white/50 mb-4">
          {breadcrumbs.map((crumb, index) => (
            <React.Fragment key={index}>
              {index > 0 && <span>/</span>}
              {crumb.href ? (
                <a href={crumb.href} className="hover:text-white transition-colors">
                  {crumb.label}
                </a>
              ) : (
                <span className="text-white/70">{crumb.label}</span>
              )}
            </React.Fragment>
          ))}
        </nav>
      )}

      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="flex items-start gap-4">
          {icon && (
            <div className="text-5xl sm:text-6xl leading-none mt-1">
              {icon}
            </div>
          )}
          <div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-2 bg-gradient-to-r from-white via-white to-white/80 bg-clip-text text-transparent">
              {title}
            </h1>
            {subtitle && (
              <p className="text-base sm:text-lg text-white/60 max-w-3xl">
                {subtitle}
              </p>
            )}
          </div>
        </div>
        {actions && (
          <div className="flex items-center gap-3">
            {actions}
          </div>
        )}
      </div>
    </div>
  )
}

interface PageContainerProps {
  children: React.ReactNode
  variant?: 'default' | 'card' | 'glass'
  className?: string
}

export function PageContainer({ children, variant = 'default', className = '' }: PageContainerProps) {
  const variants = {
    default: '',
    card: 'bg-white/5 backdrop-blur-xl rounded-2xl p-6 sm:p-8 border border-white/10 shadow-xl',
    glass: 'bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-2xl rounded-2xl p-6 sm:p-8 border border-white/20 shadow-2xl'
  }

  return (
    <div className={`${variants[variant]} ${className}`}>
      {children}
    </div>
  )
}

interface PageSectionProps {
  children: React.ReactNode
  title?: string
  subtitle?: string
  icon?: string
  className?: string
  headerActions?: React.ReactNode
}

export function PageSection({ children, title, subtitle, icon, className = '', headerActions }: PageSectionProps) {
  return (
    <section className={`mb-12 ${className}`}>
      {(title || subtitle) && (
        <div className="mb-6 flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            {icon && <span className="text-3xl">{icon}</span>}
            <div>
              {title && (
                <h2 className="text-2xl sm:text-3xl font-bold mb-2 bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
                  {title}
                </h2>
              )}
              {subtitle && (
                <p className="text-sm sm:text-base text-white/60">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
          {headerActions && (
            <div className="flex items-center gap-2">
              {headerActions}
            </div>
          )}
        </div>
      )}
      {children}
    </section>
  )
}

interface PageGridProps {
  children: React.ReactNode
  cols?: 1 | 2 | 3 | 4
  gap?: 'sm' | 'md' | 'lg'
  className?: string
}

export function PageGrid({ children, cols = 3, gap = 'md', className = '' }: PageGridProps) {
  const colsClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
  }

  const gapClasses = {
    sm: 'gap-4',
    md: 'gap-6',
    lg: 'gap-8'
  }

  return (
    <div className={`grid ${colsClasses[cols]} ${gapClasses[gap]} ${className}`}>
      {children}
    </div>
  )
}

interface EmptyStateProps {
  icon?: string
  title: string
  description: string
  action?: React.ReactNode
}

export function EmptyState({ icon = '📭', title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="text-7xl mb-6 opacity-50">
        {icon}
      </div>
      <h3 className="text-2xl font-bold mb-3 text-white/90">
        {title}
      </h3>
      <p className="text-white/60 mb-6 max-w-md">
        {description}
      </p>
      {action && (
        <div>
          {action}
        </div>
      )}
    </div>
  )
}

interface LoadingStateProps {
  message?: string
}

export function LoadingState({ message = 'Loading...' }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="relative w-16 h-16 mb-4">
        <div className="absolute inset-0 border-4 border-white/10 rounded-full"></div>
        <div className="absolute inset-0 border-4 border-transparent border-t-forgePurple border-r-neuralBlue rounded-full animate-spin"></div>
      </div>
      <p className="text-white/60">{message}</p>
    </div>
  )
}

interface ErrorStateProps {
  title?: string
  message: string
  action?: React.ReactNode
}

export function ErrorState({ title = 'Something went wrong', message, action }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="text-6xl mb-4">⚠️</div>
      <h3 className="text-2xl font-bold mb-2 text-white/90">
        {title}
      </h3>
      <p className="text-white/60 mb-6 max-w-md">
        {message}
      </p>
      {action && (
        <div>
          {action}
        </div>
      )}
    </div>
  )
}
