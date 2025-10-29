import { Bot, MessageSquare, BookOpenCheck } from "lucide-react"
import { InfoCard } from "@/components/InfoCard"
import { SectionHeading } from "@/components/SectionHeading"
import Link from "next/link"

export default function SkillAIBridgeBand() {
  return (
    <section id="ai" className="mx-auto max-w-7xl px-6 py-20">
      <SectionHeading
        title="SkillAIBridge"
        subtitle="Your AI mentor for roadmaps, instant feedback, and interview prep."
      />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <InfoCard
          title="Personalized Roadmaps"
          subtitle="Tell the AI your goal. It builds a path, projects, and checkpoints."
          icon={<Bot />}
        />
        <InfoCard
          title="Explain & Debug"
          subtitle="Paste code or errors. Get concise fixes and why they work."
          icon={<MessageSquare />}
        />
        <InfoCard
          title="Assessments"
          subtitle="Auto-graded quizzes and tasks to lock in knowledge."
          icon={<BookOpenCheck />}
        />
        <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-forgePurple/15 to-neuralBlue/15 p-6">
          <h3 className="text-base font-semibold mb-2">Try it now</h3>
          <p className="text-sm text-techGray mb-4">Open the chat and ask for a roadmap. Free demo available.</p>
          <Link
            href="/ai"
            className="inline-flex h-12 items-center justify-center rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue px-6 font-semibold"
          >
            Open SkillAIBridge
          </Link>
        </div>
      </div>
    </section>
  )
}
