import { SectionHeading } from "@/components/SectionHeading"

const tiers = [
  {
    name: "Starter",
    price: "Free",
    bullets: [
      "Access to Career Paths overview",
      "AI chat demo (rate-limited)",
      "Community & weekly tips"
    ],
    cta: "Get Started",
  },
  {
    name: "Pro",
    price: "$19/mo",
    bullets: [
      "Full AI mentor access",
      "Projects & assessments",
      "Certificates & job prep"
    ],
    cta: "Upgrade",
    highlight: true,
  },
]

export default function Pricing() {
  return (
    <section id="pricing" className="mx-auto max-w-7xl px-6 py-20">
      <SectionHeading
        title="Pricing"
        subtitle="Start free. Upgrade when you want more depth, speed, and support."
      />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {tiers.map((t) => (
          <div
            key={t.name}
            className={`rounded-2xl border p-6 ${
              t.highlight
                ? "border-aiElectric bg-gradient-to-br from-forgePurple/15 to-neuralBlue/15 shadow-glowBlue"
                : "border-white/10 bg-white/[0.06]"
            }`}
          >
            <div className="flex items-baseline justify-between">
              <h3 className="text-lg font-semibold">{t.name}</h3>
              <div className="text-2xl font-bold">{t.price}</div>
            </div>
            <ul className="mt-4 space-y-2 text-sm text-techGray">
              {t.bullets.map((b) => <li key={b}>• {b}</li>)}
            </ul>
            <button className="mt-6 h-12 w-full rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue font-semibold">
              {t.cta}
            </button>
          </div>
        ))}
      </div>
    </section>
  )
}
