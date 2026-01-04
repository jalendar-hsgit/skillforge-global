'use client'

import { ReactNode } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import DashboardBreadcrumb from './DashboardBreadcrumb'
import MentorDashboardSidebar from './MentorDashboardSidebar'
import { Logo } from './Logo'
import { useMe as useMeHook } from '@/lib/useMe'

interface DashboardLayoutProps {
  children: ReactNode
  title?: string
  subtitle?: string
  breadcrumbs?: Array<{ label: string; href?: string }>
}

export default function DashboardLayout({
  children,
  title,
  subtitle,
  breadcrumbs = [],
}: DashboardLayoutProps) {
  const router = useRouter()
  const { me } = useMeHook()

  const handleLogout = async () => {
    try {
      await fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'include' })
      router.push('/login')
    } catch (err) {
      console.error('Logout failed:', err)
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-deepNavy via-black to-deepNavy">
      {/* Top Navigation Bar - FULL WIDTH */}
      <div className="sticky top-0 z-50 bg-deepNavy/95 backdrop-blur-md border-b border-white/10 w-full">
        <div className="flex items-center justify-between px-6 py-4 w-full">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <Logo />
            <span className="text-lg font-bold text-white hidden sm:inline">SkillForge</span>
          </Link>

          {/* Center - Page Title (on desktop) */}
          <div className="hidden lg:flex items-center gap-2">
            <span className="text-techGray">/</span>
            <span className="text-white font-medium">{title || 'Dashboard'}</span>
          </div>

          {/* Right - User Menu */}
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm text-white font-medium">{me?.email}</p>
              <p className="text-xs text-techGray capitalize">{me?.role}</p>
            </div>
            <div className="relative group">
              <button className="w-10 h-10 rounded-full bg-gradient-to-br from-techBlue to-forgePurple flex items-center justify-center text-white font-bold hover:shadow-lg hover:shadow-techBlue/50 transition-all">
                {me?.email?.[0]?.toUpperCase() || 'U'}
              </button>
              <div className="absolute right-0 mt-2 w-48 bg-deepNavy/95 border border-white/10 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <Link href="/mentors/dashboard" className="block px-4 py-2 text-sm text-white hover:bg-white/10">
                  Dashboard
                </Link>
                <Link href="/mentors/dashboard/earnings" className="block px-4 py-2 text-sm text-white hover:bg-white/10">
                  Earnings
                </Link>
                <Link href="/mentors/dashboard/analytics" className="block px-4 py-2 text-sm text-white hover:bg-white/10">
                  Analytics
                </Link>
                <hr className="border-white/10" />
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-white/10"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content with Sidebar */}
      <div className="flex flex-1 overflow-hidden w-full">
        {/* Sidebar Navigation - INSIDE */}
        <MentorDashboardSidebar />

        {/* Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden w-full">

          {/* Breadcrumb Section */}
          {breadcrumbs.length > 0 && (
            <div className="bg-deepNavy/50 border-b border-white/5 w-full">
              <div className="px-6 py-3">
                <DashboardBreadcrumb items={breadcrumbs} />
              </div>
            </div>
          )}

          {/* Title Section */}
          {title && (
            <div className="w-full px-6 py-8">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-4xl font-bold text-white">{title}</h1>
                  {subtitle && (
                    <p className="mt-2 text-lg text-techGray">{subtitle}</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Main Content */}
          <main className="flex-1 overflow-y-auto w-full">
            <div className="px-6 py-8 w-full">
              {children}
            </div>
          </main>

          {/* Footer */}
          <footer className="border-t border-white/10 py-6 mt-auto w-full">
            <div className="px-6 text-center text-sm text-techGray w-full">
              <p>© 2025 SkillForge. All rights reserved.</p>
            </div>
          </footer>
        </div>
      </div>
    </div>
  )
}
