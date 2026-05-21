'use client'

export function DashboardStatSkeleton() {
  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-6 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="h-4 bg-white/10 rounded w-24 mb-3"></div>
          <div className="h-8 bg-white/10 rounded w-32"></div>
        </div>
        <div className="w-12 h-12 bg-white/10 rounded-lg"></div>
      </div>
    </div>
  )
}

export function DashboardCardSkeleton() {
  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-6 animate-pulse">
      <div className="h-6 bg-white/10 rounded w-40 mb-4"></div>
      <div className="space-y-3">
        <div className="h-4 bg-white/10 rounded w-full"></div>
        <div className="h-4 bg-white/10 rounded w-5/6"></div>
        <div className="h-4 bg-white/10 rounded w-4/6"></div>
      </div>
    </div>
  )
}

export function DashboardListSkeleton({ count = 3 }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-lg overflow-hidden">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`px-6 py-4 ${
            i !== count - 1 ? 'border-b border-white/10' : ''
          } animate-pulse`}
        >
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="h-4 bg-white/10 rounded w-40 mb-2"></div>
              <div className="h-3 bg-white/10 rounded w-56"></div>
            </div>
            <div className="h-8 bg-white/10 rounded w-20"></div>
          </div>
        </div>
      ))}
    </div>
  )
}

export function DashboardChartSkeleton() {
  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-6 animate-pulse">
      <div className="h-6 bg-white/10 rounded w-40 mb-6"></div>
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="h-8 bg-white/10 rounded flex-1" style={{width: `${(i+1) * 20}%`}}></div>
            <div className="h-4 bg-white/10 rounded w-12"></div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function DashboardGridSkeleton({ count = 4 }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <DashboardStatSkeleton key={i} />
      ))}
    </div>
  )
}

// Pulse animation component for more dynamic loading
export function PulseAnimation() {
  return (
    <style jsx>{`
      @keyframes pulse {
        0%, 100% {
          opacity: 1;
        }
        50% {
          opacity: 0.5;
        }
      }
      .animate-pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
      }
    `}</style>
  )
}
