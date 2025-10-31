import Link from 'next/link'
import Image from 'next/image'
import { useMe } from '@/hooks/useMe'
import { ROUTES } from '@/lib/routes'
import Footer from '@/components/Footer'
import CoinBadge from '@/components/CoinBadge'

export default function Layout({ children }: {children: React.ReactNode}) {
  const { me } = useMe()
  return (
    <div className="min-h-screen bg-[#0B0A13] text-white flex flex-col">
      <header className="fixed inset-x-0 top-0 z-40 backdrop-blur border-b border-white/10">
        <nav className="mx-auto max-w-7xl px-6 h-16 flex items-center justify-between">
          <Link href={ROUTES.home} className="flex items-center gap-3">
            <Image src="/logo.svg" alt="SkillForge Global" width={28} height={28} priority />
            <span className="font-semibold">SkillForge Global</span>
          </Link>
          <div className="flex items-center gap-6 text-sm">
            <Link href={ROUTES.paths}>Career Paths</Link>
            <Link href={ROUTES.ai}>SkillAIBridge</Link>
            <Link href={ROUTES.pricing}>Pricing</Link>
            <Link href={ROUTES.faq}>FAQ</Link>
            {me && <CoinBadge />}
            {!me && <Link href={ROUTES.login} className="text-white/80 hover:text-white">Log in</Link>}
            {me ? (
              <>
                <Link href={ROUTES.dashboard} className="text-white/90">Dashboard</Link>
                <Link href={ROUTES.logout} className="inline-flex h-9 items-center rounded-md bg-white/10 px-3 border border-white/10">Log out</Link>
              </>
            ) : (
              <Link href={ROUTES.signup} className="inline-flex h-9 items-center rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue px-3">Get Started</Link>
            )}
          </div>
        </nav>
      </header>

      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  )
}
