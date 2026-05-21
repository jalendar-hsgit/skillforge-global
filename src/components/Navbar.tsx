import Link from 'next/link'
import { Logo } from './Logo'
import { Button } from './Button'
import { useEffect, useState, useCallback } from 'react'
import { useMe as useMeHook } from '@/lib/useMe'
import { ChevronDown, Coins } from 'lucide-react'
import { CoinHistoryModal } from './CoinHistoryModal'

export function Navbar() {
  const { me } = useMeHook()
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [coinBalance, setCoinBalance] = useState<number>(0)
  const [coinModalOpen, setCoinModalOpen] = useState(false)
  const [loadingCoins, setLoadingCoins] = useState(false)
  
  // Fetch coin balance
  const fetchCoinBalance = useCallback(async () => {
    if (!me) return
    try {
      setLoadingCoins(true)
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'
      const token = localStorage.getItem('token')
      const res = await fetch(`${apiBase}/api/v1x/coins_db/balance`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setCoinBalance(data.balance || 0)
      }
    } catch (err) {
      console.error('Failed to fetch coin balance:', err)
    } finally {
      setLoadingCoins(false)
    }
  }, [me])
  
  useEffect(() => { setIsLoggedIn(!!me) }, [me])
  
  useEffect(() => {
    if (me) fetchCoinBalance()
  }, [me, fetchCoinBalance])
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
                {/* Coin Balance Button */}
                <button
                  onClick={() => setCoinModalOpen(true)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 hover:border-yellow-400/50 text-yellow-400 hover:text-yellow-300 transition-all group"
                  title="View coin history"
                >
                  <Coins size={16} className="group-hover:animate-bounce" />
                  <span className="text-sm font-semibold">
                    {loadingCoins ? '...' : coinBalance.toLocaleString()}
                  </span>
                </button>
                
                <Link href="/mentors/dashboard" className="text-sm text-techGray hover:text-white">Mentor Dashboard</Link>
                <Link href="/dashboard" className="text-sm text-techGray hover:text-white">My Dashboard</Link>
                
                {/* User Menu Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-techGray hover:text-white hover:bg-white/5 transition-colors"
                  >
                    Account
                    <ChevronDown size={16} className={`transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
                  </button>
                  
                  {userMenuOpen && (
                    <div className="absolute right-0 mt-1 w-48 bg-black/80 border border-white/10 rounded-lg shadow-lg overflow-hidden z-50">
                      <Link href="/profile" className="block px-4 py-2 text-sm text-techGray hover:text-white hover:bg-white/10 transition-colors">
                        My Profile
                      </Link>
                      <Link href="/profile/edit" className="block px-4 py-2 text-sm text-techGray hover:text-white hover:bg-white/10 transition-colors">
                        Edit Profile
                      </Link>
                      <Link href="/profile/settings" className="block px-4 py-2 text-sm text-techGray hover:text-white hover:bg-white/10 transition-colors">
                        Settings
                      </Link>
                      <Link href="/mentors/dashboard/verification" className="block px-4 py-2 text-sm text-techGray hover:text-white hover:bg-white/10 transition-colors">
                        Verify Credentials
                      </Link>
                      <hr className="border-white/10" />
                      <Link href="/logout" className="block px-4 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-white/10 transition-colors">
                        Log out
                      </Link>
                    </div>
                  )}
                </div>
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
      
      {/* Coin History Modal */}
      <CoinHistoryModal
        isOpen={coinModalOpen}
        onClose={() => {
          setCoinModalOpen(false)
          // Refresh balance when closing modal in case there were changes
          fetchCoinBalance()
        }}
        currentBalance={coinBalance}
      />
    </header>
  )
}
