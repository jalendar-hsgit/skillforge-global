import { Brain, Code2, CloudCog, ShieldCheck, Smartphone } from "lucide-react"
import { InfoCard } from "@/components/InfoCard"
import { SectionHeading } from "@/components/SectionHeading"

const paths = [
  { title: "Python & AI", icon: <Brain />, subtitle: "From Python basics to ML projects and certification." },
  { title: "Full-Stack Web (React + Node)", icon: <Code2 />, subtitle: "Frontend, backend, APIs, deployment." },
  { title: "AWS / DevOps", icon: <CloudCog />, subtitle: "Cloud fundamentals, CI/CD, Docker, monitoring." },
  { title: "Cybersecurity", icon: <ShieldCheck />, subtitle: "Security basics, OWASP, labs, tooling." },
  { title: "Flutter (Mobile)", icon: <Smartphone />, subtitle: "Cross-platform apps with solid UX patterns." },
]

export default function CareerPathsGrid() {
  return (
    <section id="paths" className="mx-auto max-w-7xl px-6 py-20">
      <SectionHeading
        title="Career Paths"
        subtitle="Structured, project-first learning with checklists, assessments, and certificates."
      />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {paths.map((p) => (
          <InfoCard
            key={p.title}
            title={p.title}
            subtitle={p.subtitle}
            icon={<div className="text-aiElectric">{p.icon}</div>}
            href="/paths"
          />
        ))}
      </div>
    </section>
  )
}
