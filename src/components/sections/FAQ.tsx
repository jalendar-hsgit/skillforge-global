import { useState } from "react"
import { SectionHeading } from "@/components/SectionHeading"

const faqs = [
  { q: "Who is this for?", a: "Ambitious learners who want job-ready tech skills and AI-powered guidance." },
  { q: "Do I need prior coding experience?", a: "No. Our Python & AI path starts at zero and ramps up with projects." },
  { q: "How does SkillAIBridge work?", a: "It customizes plans, explains concepts, and reviews your code with clear steps." },
  { q: "Can I cancel anytime?", a: "Yes. Plans are flexible and you can export your notes and progress." },
]

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(0)
  return (
    <section id="faq" className="mx-auto max-w-7xl px-6 py-20">
      <SectionHeading title="FAQ" subtitle="Answers to the most common questions." />
      <div className="space-y-3">
        {faqs.map((item, i) => (
          <div key={item.q} className="rounded-xl border border-white/10">
            <button
              onClick={() => setOpen(open === i ? null : i)}
              className="w-full text-left px-5 py-4 flex items-center justify-between"
            >
              <span className="font-medium">{item.q}</span>
              <span className="text-techGray">{open === i ? "−" : "+"}</span>
            </button>
            {open === i && (
              <div className="px-5 pb-5 text-techGray text-sm">{item.a}</div>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
