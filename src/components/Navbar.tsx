import Link from 'next/link'
import { Logo } from './Logo'
import { Button } from './Button'
import { useEffect, useState } from 'react'
import { useMe as useMeHook } from '@/lib/useMe'

export function Navbar() {
  const { me } = useMeHook()
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  useEffect(() => { setIsLoggedIn(!!me) }, [me])
  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-black/25 backdrop-blur">
      <div className="container">
        <div className="h-16 flex items-center justify-between">
          <Link href="/" aria-label="SkillForge Global home" className="flex items-center">
            <Logo />
          </Link>

          <nav className="hidden md:flex items-center gap-8 text-sm text-techGray">
            <Link href="/paths" className="hover:text-white">Career Paths</Link>
            <Link href="/practice" className="hover:text-white">Coding Practice</Link>
            <Link href="/marketplace" className="hover:text-white">Marketplace</Link>
            <Link href="/ai" className="hover:text-white">SkillAIBridge</Link>
            <Link href="/resumes/new" className="hover:text-white">Create Resume</Link>
            <a href="#pricing" className="hover:text-white">Pricing</a>
            <a href="#faq" className="hover:text-white">FAQ</a>
          </nav>

          <div className="flex items-center gap-3">
            {isLoggedIn ? (
              <>
                <Link href="/mentors/dashboard" className="text-sm text-techGray hover:text-white">Mentor Dashboard</Link>
                <Link href="/dashboard" className="text-sm text-techGray hover:text-white">My Dashboard</Link>
                <Link href="/logout" className="hidden sm:block">
                  <Button size="sm" variant="secondary">Log out</Button>
                </Link>
              </>
            ) : (
              <>
                <Link href="/login" className="text-sm text-techGray hover:text-white">Log in</Link>
                <Link href="/signup" className="hidden sm:block">
                  <Button size="sm">Get Started</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
