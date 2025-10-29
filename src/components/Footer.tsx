import Link from "next/link"
import Image from "next/image"
import { ROUTES } from "@/lib/routes"
import { useState } from "react"

export default function Footer() {
  const [email, setEmail] = useState("")
  const [msg, setMsg] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onSubscribe(e: React.FormEvent) {
    e.preventDefault()
    setMsg(null); setBusy(true)
    const r = await fetch("/api/subscribe", {
      method: "POST",
      headers: { "Content-Type":"application/json" },
      body: JSON.stringify({ email }),
    })
    setBusy(false)
    if (r.ok) { setMsg("Subscribed!"); setEmail("") }
    else { setMsg("Failed. Try again.") }
  }

  return (
    <footer className="mt-24 border-t border-white/10 bg-white/[0.03]">
      <div className="border-b border-white/10">
        <div className="mx-auto max-w-7xl px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-gradient-to-r from-forgePurple to-neuralBlue animate-ping" />
            <span className="text-sm text-white/90">
              Earn <b>Forge AI Credits</b> by completing modules and passing quizzes.
            </span>
          </div>
          <Link
            href={ROUTES.dashboard}
            className="text-sm inline-flex items-center rounded-md px-3 py-1.5 bg-gradient-to-r from-forgePurple to-neuralBlue font-medium"
          >
            View rewards →
          </Link>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-6 py-12 grid grid-cols-1 md:grid-cols-4 gap-10">
        <div className="space-y-3">
          <Link href={ROUTES.home} className="flex items-center gap-3">
            <Image src="/logo.svg" alt="SkillForge Global" width={28} height={28} />
            <span className="font-semibold">SkillForge Global</span>
          </Link>
          <p className="text-sm text-techGray">
            Project-first learning. Quizzes, progress, AI mentor, and real-world challenges.
          </p>
        </div>

        <div>
          <h4 className="font-semibold mb-3">Product</h4>
          <ul className="space-y-2 text-sm text-white/90">
            <li><Link className="hover:underline" href={ROUTES.paths}>Career Paths</Link></li>
            <li><Link className="hover:underline" href={ROUTES.ai}>SkillAIBridge</Link></li>
            <li><Link className="hover:underline" href={ROUTES.pricing}>Pricing</Link></li>
            <li><Link className="hover:underline" href="/quiz/python-ai">Sample Quiz</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="font-semibold mb-3">Company</h4>
          <ul className="space-y-2 text-sm text-white/90">
            <li><Link className="hover:underline" href="/company">About</Link></li>
            <li><Link className="hover:underline" href="/careers">Careers</Link></li>
            <li><Link className="hover:underline" href="/mentors">Mentors</Link></li>
            <li><Link className="hover:underline" href="/contact">Contact</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="font-semibold mb-3">Stay in the loop</h4>
          <form onSubmit={onSubscribe} className="flex gap-2">
            <input
              className="w-full h-10 rounded-md bg-white/5 border border-white/10 px-3 text-sm"
              type="email" placeholder="your@email.com" aria-label="email"
              value={email} onChange={e=>setEmail(e.target.value)}
              required
            />
            <button disabled={busy} className="h-10 px-4 rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue text-sm font-semibold">
              {busy ? "…" : "Subscribe"}
            </button>
          </form>
          <p className="text-xs text-techGray mt-2">{msg || "No spam. Unsubscribe anytime."}</p>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-6 py-6 border-t border-white/10 flex flex-col md:flex-row items-center justify-between text-xs text-techGray">
        <div>© {new Date().getFullYear()} SkillForge Global. All rights reserved.</div>
        <div className="flex items-center gap-4 mt-3 md:mt-0">
          <Link href="/privacy" className="hover:underline">Privacy</Link>
          <Link href="/terms" className="hover:underline">Terms</Link>
          <Link href="/security" className="hover:underline">Security</Link>
        </div>
      </div>
    </footer>
  )
}
