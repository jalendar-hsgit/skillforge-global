import Head from 'next/head'
import Layout from '@/components/Layout'
import { SectionHeading } from '@/components/SectionHeading'
import { InfoCard } from '@/components/InfoCard'
import { Brain, Code2, CloudCog, ShieldCheck, Smartphone } from "lucide-react"
import Link from 'next/link'

const paths = [
  { slug:'python-ai', title: "Python & AI", icon: <Brain />, subtitle: "Python fundamentals, DS & ML projects, deployment." },
  { slug:'fullstack', title: "Full-Stack Web (React + Node)", icon: <Code2 />, subtitle: "Frontend, backend, APIs, auth, prod deploy." },
  { slug:'aws-devops', title: "AWS / DevOps", icon: <CloudCog />, subtitle: "Cloud basics, IaC, Docker, CI/CD, monitoring." },
  { slug:'cybersec', title: "Cybersecurity", icon: <ShieldCheck />, subtitle: "Threats, OWASP, labs, tools, blue/red basics." },
  { slug:'flutter', title: "Flutter (Mobile)", icon: <Smartphone />, subtitle: "Dart, UI patterns, state mgmt, store & publish." },
]

export default function PathsPage() {
  return (
    <Layout>
      <Head><title>Career Paths – SkillForge Global</title></Head>
      <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
        <SectionHeading
          title="Choose your Career Path"
          subtitle="Each path includes curated video lessons, projects, quizzes, and interview prep."
        />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {paths.map(p => (
            <Link key={p.slug} href={`/paths/${p.slug}`}>
              <div className="rounded-2xl border border-white/10 bg-white/[0.06] hover:bg-white/[0.08] transition p-5">
                <div className="flex items-start gap-4">
                  <div className="shrink-0 h-12 w-12 rounded-xl bg-gradient-to-br from-forgePurple/40 to-neuralBlue/40 grid place-items-center">
                    <div className="text-aiElectric">{p.icon}</div>
                  </div>
                  <div>
                    <h3 className="text-base font-semibold">{p.title}</h3>
                    <p className="text-sm text-techGray mt-1">{p.subtitle}</p>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </Layout>
  )
}
