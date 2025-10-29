import Head from 'next/head'
import Layout from '@/components/Layout'
import Link from 'next/link'
import type { GetServerSideProps } from 'next'

type Me = { id:number; email:string; created_at:string } | null

export const getServerSideProps: GetServerSideProps = async (ctx) => {
  const base = `http://${ctx.req.headers.host}`
  const r = await fetch(`${base}/api/session/me`, {
    headers: { cookie: ctx.req.headers.cookie || '' }
  })
  if (!r.ok) {
    return { redirect: { destination: '/login', permanent: false } }
  }
  const me = await r.json()
  return { props: { me } }
}

export default function Dashboard({ me }: { me: Me }) {
  return (
    <Layout>
      <Head><title>{`Dashboard – SkillForge Global`}</title></Head>
      <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
        <h1 className="text-3xl md:text-4xl font-semibold">Welcome{me ? `, ${me.email}` : ''}</h1>
        <p className="text-techGray mt-2">Track your learning, projects, and career assets in one place.</p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-10">
          <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-6">
            <h3 className="font-semibold">Progress</h3>
            <p className="text-sm text-techGray mt-1">See completion across paths and modules.</p>
            <div className="mt-4 h-3 rounded bg-white/10">
              <div className="h-3 rounded bg-gradient-to-r from-forgePurple to-neuralBlue" style={{width:'28%'}} />
            </div>
            <Link href="/paths/python-ai" className="inline-block mt-4 underline text-sm">Continue Python & AI →</Link>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-6">
            <h3 className="font-semibold">Quizzes & Checkpoints</h3>
            <p className="text-sm text-techGray mt-1">Short assessments to lock in skills.</p>
            <button className="mt-4 h-10 px-4 rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue">Take a quiz</button>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-6">
            <h3 className="font-semibold">Projects & Challenges</h3>
            <p className="text-sm text-techGray mt-1">Ship portfolio-ready apps with real specs.</p>
            <ul className="text-sm mt-3 list-disc pl-5">
              <li>API-driven app with auth</li>
              <li>DevOps pipeline to AWS</li>
              <li>Security hardening checklist</li>
            </ul>
            <button className="mt-4 h-10 px-4 rounded-md bg-white/10 border border-white/10">View challenge library</button>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-6">
            <h3 className="font-semibold">AI Resume & Job Match</h3>
            <p className="text-sm text-techGray mt-1">Generate a tailored resume and match roles to your skills.</p>
            <div className="text-xs text-techGray mt-2">Resume will auto-include verified projects completed here.</div>
            <button className="mt-4 h-10 px-4 rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue">Create resume</button>
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-6 mt-6">
          <h3 className="font-semibold">Dev Simulator (MVP)</h3>
          <p className="text-sm text-techGray mt-1">Practice real-time tasks: receive tickets, write code, run tests.</p>
          <button className="mt-4 h-10 px-4 rounded-md bg-white/10 border border-white/10">Open simulator</button>
        </div>
      </section>
    </Layout>
  )
}
