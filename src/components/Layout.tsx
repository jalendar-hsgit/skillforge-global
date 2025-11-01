import Link from 'next/link'
import Image from 'next/image'
import { useRouter } from 'next/router'
import { useState } from 'react'
import { useMe } from '@/hooks/useMe'
import { ROUTES } from '@/lib/routes'
import Footer from '@/components/Footer'
import CoinBadge from '@/components/CoinBadge'

interface LayoutProps {
  children: React.ReactNode
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '7xl' | 'full'
  showFooter?: boolean
}

export default function Layout({ children, maxWidth = '7xl', showFooter = true }: LayoutProps) {
  const { me, loading } = useMe()
  const router = useRouter()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const isActive = (path: string) => router.pathname === path || router.pathname.startsWith(path + '/')

  const maxWidthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    '7xl': 'max-w-7xl',
    full: 'max-w-full'
  }

  const navLinks = [
    { href: ROUTES.paths, label: 'Courses', icon: '📚' },
    { href: ROUTES.mentors, label: 'Mentors', icon: '👥' },
    { href: ROUTES.ai, label: 'AI Assistant', icon: '🤖' },
    { href: ROUTES.resumeNew, label: 'Create Resume', icon: '📄' },
    { href: ROUTES.pricing, label: 'Pricing', icon: '💳' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0B0A13] via-[#1a1625] to-[#0B0A13] text-white flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-[#0B0A13]/80 border-b border-white/10 shadow-lg shadow-purple-500/5">
        <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href={ROUTES.home} className="flex items-center gap-3 group">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-forgePurple to-neuralBlue rounded-lg blur opacity-20 group-hover:opacity-40 transition-opacity" />
                <Image 
                  src="/logo.svg" 
                  alt="SkillForge Global" 
                  width={32} 
                  height={32} 
                  priority 
                  className="relative"
                />
              </div>
              <span className="font-bold text-lg bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
                SkillForge Global
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive(link.href)
                      ? 'bg-white/10 text-white shadow-lg shadow-purple-500/20'
                      : 'text-white/70 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <span className="text-base">{link.icon}</span>
                  <span>{link.label}</span>
                </Link>
              ))}
            </div>

            {/* Right Side Actions */}
            <div className="flex items-center gap-3">
              {/* Coin Badge */}
              {me && !loading && <CoinBadge />}

              {/* Auth Buttons */}
              {loading ? (
                <div className="h-9 w-24 bg-white/5 rounded-lg animate-pulse" />
              ) : me ? (
                <div className="flex items-center gap-3">
                  {/* User Menu */}
                  <Link
                    href={ROUTES.dashboard}
                    className={`hidden sm:flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      isActive(ROUTES.dashboard)
                        ? 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white shadow-lg'
                        : 'bg-white/5 text-white/90 hover:bg-white/10'
                    }`}
                  >
                    <span>📊</span>
                    <span>Dashboard</span>
                  </Link>
                  <Link
                    href={ROUTES.logout}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-white/5 text-white/70 hover:bg-white/10 hover:text-white transition-all border border-white/10"
                  >
                    <span>🚪</span>
                    <span className="hidden sm:inline">Logout</span>
                  </Link>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <Link
                    href={ROUTES.login}
                    className="px-4 py-2 rounded-lg text-sm font-medium text-white/80 hover:text-white hover:bg-white/5 transition-all"
                  >
                    Log in
                  </Link>
                  <Link
                    href={ROUTES.signup}
                    className="px-5 py-2 rounded-lg text-sm font-semibold bg-gradient-to-r from-forgePurple to-neuralBlue hover:shadow-lg hover:shadow-purple-500/50 transition-all transform hover:scale-105"
                  >
                    Get Started →
                  </Link>
                </div>
              )}

              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-lg hover:bg-white/5 transition-colors"
                aria-label="Toggle menu"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  {mobileMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-white/10 animate-in slide-in-from-top">
              <div className="flex flex-col gap-2">
                {navLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                      isActive(link.href)
                        ? 'bg-white/10 text-white'
                        : 'text-white/70 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <span className="text-xl">{link.icon}</span>
                    <span>{link.label}</span>
                  </Link>
                ))}
                {me && (
                  <Link
                    href={ROUTES.dashboard}
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium bg-gradient-to-r from-forgePurple to-neuralBlue text-white"
                  >
                    <span className="text-xl">📊</span>
                    <span>Dashboard</span>
                  </Link>
                )}
              </div>
            </div>
          )}
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <div className={`mx-auto ${maxWidthClasses[maxWidth]} px-4 sm:px-6 lg:px-8 py-8`}>
          {children}
        </div>
      </main>

      {/* Footer */}
      {showFooter && <Footer />}
    </div>
  )
}
