'use client'

import Link from 'next/link'
import { useRouter } from 'next/router'
import { useState } from 'react'

interface NavItem {
  href: string
  label: string
  icon: string
  description: string
}

const navItems: NavItem[] = [
  { 
    href: '/mentors/dashboard', 
    label: 'Overview', 
    icon: '📊',
    description: 'Dashboard overview and quick stats'
  },
  { 
    href: '/mentors/dashboard/earnings', 
    label: 'Earnings', 
    icon: '💰',
    description: 'Revenue analytics and breakdown'
  },
  { 
    href: '/mentors/dashboard/analytics', 
    label: 'Analytics', 
    icon: '📈',
    description: 'Performance metrics and trends'
  },
  { 
    href: '/mentors/dashboard/sessions', 
    label: 'Sessions', 
    icon: '📅',
    description: 'Manage your sessions'
  },
  { 
    href: '/mentors/dashboard/students', 
    label: 'Students', 
    icon: '👥',
    description: 'Your student roster'
  },
  { 
    href: '/mentors/dashboard/payouts', 
    label: 'Payouts', 
    icon: '💳',
    description: 'Payment setup and transfers'
  },
  { 
    href: '/mentors/dashboard/reviews', 
    label: 'Reviews', 
    icon: '⭐',
    description: 'Student feedback'
  },
  { 
    href: '/mentors/dashboard/profile', 
    label: 'Profile', 
    icon: '⚙️',
    description: 'Account settings'
  },
]

export default function MentorDashboardSidebar() {
  const router = useRouter()
  const [hoveredItem, setHoveredItem] = useState<string | null>(null)

  const isActive = (href: string) => {
    if (href === '/mentors/dashboard') {
      return router.pathname === '/mentors/dashboard'
    }
    return router.pathname.includes(href)
  }

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex flex-col w-64 bg-gradient-to-b from-deepNavy to-black border-r border-white/10 h-full overflow-y-auto">
        {/* Logo Section */}
        <div className="p-6 border-b border-white/10">
          <h2 className="text-xl font-bold bg-gradient-to-r from-techBlue to-forgePurple bg-clip-text text-transparent">
            Mentor Portal
          </h2>
          <p className="text-xs text-techGray mt-1">Manage your teaching</p>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const active = isActive(item.href)
            return (
              <Link
                key={item.href}
                href={item.href}
                onMouseEnter={() => setHoveredItem(item.href)}
                onMouseLeave={() => setHoveredItem(null)}
                className={`
                  group relative flex items-center gap-3 px-4 py-3 rounded-lg
                  transition-all duration-200 ease-out
                  ${
                    active
                      ? 'bg-gradient-to-r from-forgePurple to-techBlue text-white shadow-lg shadow-forgePurple/20'
                      : 'text-techGray hover:bg-white/5'
                  }
                `}
                title={item.description}
              >
                <span className="text-xl flex-shrink-0">{item.icon}</span>
                <span className="font-medium flex-1">{item.label}</span>
                
                {/* Indicator dot for active */}
                {active && (
                  <span className="absolute right-3 w-2 h-2 bg-white rounded-full"></span>
                )}

                {/* Hover tooltip */}
                {hoveredItem === item.href && !active && (
                  <div className="absolute left-full ml-2 px-3 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg text-xs text-white whitespace-nowrap pointer-events-none z-50">
                    {item.description}
                  </div>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Footer Section */}
        <div className="p-4 border-t border-white/10 space-y-2">
          <button
            onClick={() => router.push('/mentors/profile')}
            className="w-full px-4 py-2 text-sm text-techGray hover:text-white hover:bg-white/5 rounded-lg transition-colors"
          >
            ⚙️ Settings
          </button>
          <button
            onClick={() => router.push('/help')}
            className="w-full px-4 py-2 text-sm text-techGray hover:text-white hover:bg-white/5 rounded-lg transition-colors"
          >
            ❓ Help & Support
          </button>
        </div>
      </aside>

      {/* Mobile Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 lg:hidden bg-gradient-to-t from-deepNavy to-black border-t border-white/10 z-50">
        <div className="flex items-center justify-around overflow-x-auto">
          {navItems.slice(0, 5).map((item) => {
            const active = isActive(item.href)
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex flex-col items-center justify-center px-3 py-2 min-w-[60px]
                  transition-all duration-200
                  ${
                    active
                      ? 'text-forgePurple border-t-2 border-forgePurple'
                      : 'text-techGray'
                  }
                `}
              >
                <span className="text-2xl">{item.icon}</span>
                <span className="text-xs mt-1 text-center">{item.label}</span>
              </Link>
            )
          })}
          {/* More menu for mobile */}
          <div className="flex flex-col items-center justify-center px-3 py-2 min-w-[60px]">
            <span className="text-2xl">⋯</span>
            <span className="text-xs mt-1">More</span>
          </div>
        </div>
      </div>
    </>
  )
}
