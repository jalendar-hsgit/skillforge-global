import Head from "next/head"
import Layout from "@/components/Layout"
import { useState } from "react"

const QA = [
  {
    q: "Is the content really free?",
    a: "Yes. Starter includes free paths and quizzes. Pro/Elite add projects, AI mentor, certificates, and more."
  },
  {
    q: "How do Forge AI Credits work?",
    a: "Earn credits by completing modules, passing quizzes, and streaks. Soon you can redeem credits for rewards and discounts."
  },
  {
    q: "Can I cancel anytime?",
    a: "Absolutely. Billing is month-to-month. You can cancel in one click and keep your progress."
  },
  {
    q: "Do you provide certificates?",
    a: "Yes, Pro and Elite plans include shareable certificates validated by your progress and quiz results."
  },
  {
    q: "What is SkillAIBridge?",
    a: "Your AI mentor. It gives personalized plans, instant feedback on code, and interview prep suggestions."
  },
  {
    q: "Do you support teams or universities?",
    a: "Yes. We provide admin dashboards, custom tracks, SSO, and reporting."
  }
]

export default function FAQPage() {
  const [open, setOpen] = useState<number | null>(0)
  return (
    <Layout>
      <Head><title>FAQ – SkillForge Global</title></Head>
      <section className="mx-auto max-w-3xl px-6 pt-36 pb-20">
        <h1 className="text-4xl font-semibold">Frequently asked questions</h1>
        <p className="text-techGray mt-2">If you can’t find an answer, email hello@skillforge.global</p>

        <div className="mt-8 divide-y divide-white/10 rounded-2xl border border-white/10 bg-white/[0.04]">
          {QA.map((item, i) => {
            const isOpen = open === i
            return (
              <div key={i}>
                <button
                  className="w-full text-left px-5 py-4 flex items-center justify-between"
                  onClick={()=>setOpen(isOpen ? null : i)}
                >
                  <span className="font-medium">{item.q}</span>
                  <span className={`transition-transform ${isOpen ? 'rotate-45' : ''}`}>+</span>
                </button>
                {isOpen && (
                  <div className="px-5 pb-5 text-sm text-white/90">{item.a}</div>
                )}
              </div>
            )
          })}
        </div>
      </section>
    </Layout>
  )
}
