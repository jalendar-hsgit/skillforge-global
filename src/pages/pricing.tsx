import Head from "next/head"
import Layout from "@/components/Layout"
import Link from "next/link"

type Tier = {
  name: string
  price: string
  blurb: string
  cta: string
  highlight?: boolean
  features: string[]
}

const tiers: Tier[] = [
  {
    name: "Starter",
    price: "$0",
    blurb: "Explore paths, watch modules, take basic quizzes.",
    cta: "Get started",
    features: [
      "Access to free paths",
      "Basic quizzes",
      "Progress tracking",
      "Community access"
    ],
  },
  {
    name: "Pro",
    price: "$19/mo",
    blurb: "Serious learning with projects and AI guidance.",
    cta: "Upgrade to Pro",
    highlight: true,
    features: [
      "All Starter features",
      "Projects with templates",
      "SkillAIBridge guidance",
      "Certificates",
      "Email support"
    ],
  },
  {
    name: "Elite",
    price: "$49/mo",
    blurb: "Fast-track results with mentors and interview prep.",
    cta: "Go Elite",
    features: [
      "All Pro features",
      "Mentor office hours",
      "Mock interviews",
      "Job match signals",
      "Priority support"
    ],
  },
]

export default function PricingPage() {
  return (
    <Layout>
      <Head><title>Pricing – SkillForge Global</title></Head>
      <section className="mx-auto max-w-6xl px-6 pt-36 pb-20">
        <h1 className="text-4xl font-semibold">Simple, transparent pricing</h1>
        <p className="text-techGray mt-2">Start free. Upgrade anytime. Cancel anytime.</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10">
          {tiers.map(t => (
            <div key={t.name} className={`rounded-2xl border ${t.highlight ? 'border-neuralBlue/40 shadow-glowBlue' : 'border-white/10'} bg-white/[0.05] p-6 flex flex-col`}>
              <div className="flex items-baseline justify-between">
                <h3 className="text-xl font-semibold">{t.name}</h3>
                <div className="text-2xl font-bold">{t.price}</div>
              </div>
              <p className="text-sm text-techGray mt-2">{t.blurb}</p>
              <ul className="mt-4 space-y-2 text-sm">
                {t.features.map(f => (
                  <li key={f} className="flex items-start gap-2">
                    <span className="mt-1 h-1.5 w-1.5 rounded-full bg-gradient-to-r from-forgePurple to-neuralBlue" />
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
              <Link href="/signup" className={`mt-6 inline-flex h-11 items-center justify-center rounded-md ${t.highlight ? 'bg-gradient-to-r from-forgePurple to-neuralBlue' : 'bg-white/10 border border-white/10'} px-6 font-semibold`}>
                {t.cta}
              </Link>
            </div>
          ))}
        </div>

        <div className="mt-14 rounded-2xl border border-white/10 bg-white/[0.04] p-6">
          <h4 className="font-semibold">Teams & Universities</h4>
          <p className="text-sm text-techGray mt-1">Need 20+ seats, custom tracks, or SSO? Contact us for a tailored plan.</p>
          <Link href="mailto:sales@skillforge.global" className="inline-flex mt-3 h-10 items-center rounded-md bg-white/10 px-4 border border-white/10 text-sm">Contact sales</Link>
        </div>
      </section>
    </Layout>
  )
}
