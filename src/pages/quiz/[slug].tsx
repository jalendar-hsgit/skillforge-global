import Head from 'next/head'
import Layout from '@/components/Layout'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'
import { ROUTES } from '@/lib/routes'
import { addCredits } from '@/lib/credits'

type Q = { id:string; type:'mcq'; text:string; options:string[]; explanation?:string }
type Quiz = { id:string; title:string; questions:Q[] }
type SubmitOut = { score:number; total:number; results:{ id:string; correct:boolean; correctIndex:number; explanation?:string }[] }

function passThreshold(total: number) {
  return Math.ceil(total * 0.5) // >= 50%
}

export default function QuizPage() {
  const { query } = useRouter()
  const slug = String(query.slug || '')
  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [result, setResult] = useState<SubmitOut | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [earned, setEarned] = useState<number>(0)

  useEffect(() => {
    if (!slug) return
    setErr(null); setResult(null)
    fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1/quizzes?path=${slug}`)
      .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
      .then(setQuiz)
      .catch(()=>setErr('Quiz not found'))
  }, [slug])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setErr(null)
    const payload = {
      path: slug,
      answers: Object.entries(answers).map(([id, idx]) => ({ id, answerIndex: idx }))
    }
    const r = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1/quizzes/submit`, {
      method: 'POST',
      headers: { 'Content-Type':'application/json' },
      body: JSON.stringify(payload)
    })
    if (!r.ok) { setErr('Submit failed'); return }
    const d: SubmitOut = await r.json()
    setResult(d)

    // If passed, grant +10 Forge AI Credits
    if (d.score >= passThreshold(d.total)) {
      const newBal = addCredits(10)
      setEarned(10)
      console.log('Forge AI Credits balance:', newBal)
    }
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <Layout>
      <Head><title>{`Quiz – ${slug}`}</title></Head>
      <section className="mx-auto max-w-3xl px-6 pt-36 pb-20">
        <Link href={ROUTES.path(slug)} className="text-techGray hover:text-white text-sm">← Back to path</Link>
        <h1 className="text-3xl font-semibold mt-4">{quiz?.title || 'Quiz'}</h1>

        {err && <div className="mt-6 text-red-400 text-sm">{err}</div>}

        {result && (
          <div className="mt-6 rounded-xl border border-white/10 p-4 bg-white/[0.06]">
            <div className="font-semibold">Score: {result.score} / {result.total}</div>
            <div className="text-xs text-techGray">Pass mark: {passThreshold(result.total)}+</div>
            {earned > 0 && (
              <div className="mt-2 text-sm text-green-400">+{earned} Forge AI Credits earned 🎉</div>
            )}
            <div className="mt-4 flex gap-3">
              <Link href={ROUTES.path(slug)} className="inline-flex h-10 items-center rounded-md bg-white/10 px-4 border border-white/10">Back to path</Link>
              <button onClick={()=>setResult(null)} className="h-10 rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue px-4 font-semibold">Retake</button>
              <Link href={ROUTES.dashboard} className="inline-flex h-10 items-center rounded-md bg-white/10 px-4 border border-white/10">Go to dashboard</Link>
            </div>
          </div>
        )}

        {!result && quiz && (
          <form onSubmit={onSubmit} className="mt-6 space-y-6">
            {quiz.questions.map((q, qi) => (
              <div key={q.id} className="rounded-xl border border-white/10 p-4 bg-white/[0.06]">
                <div className="font-medium">{qi+1}. {q.text}</div>
                <div className="mt-3 grid gap-2">
                  {q.options.map((opt, idx) => (
                    <label key={idx} className="flex items-center gap-2 text-sm">
                      <input
                        type="radio"
                        name={q.id}
                        checked={answers[q.id] === idx}
                        onChange={()=>setAnswers({...answers, [q.id]: idx})}
                      />
                      <span>{opt}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
            <button className="h-12 rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue px-6 font-semibold">Submit</button>
          </form>
        )}

        {result && quiz && (
          <div className="mt-6 space-y-6">
            {quiz.questions.map((q, qi) => {
              const r = result.results.find(x => x.id === q.id)!
              return (
                <div key={q.id} className="rounded-xl border border-white/10 p-4 bg-white/[0.06]">
                  <div className="font-medium">{qi+1}. {q.text}</div>
                  <div className="mt-2 text-sm">
                    {r.correct ? <span className="text-green-400">Correct</span> : <span className="text-red-400">Incorrect</span>}
                  </div>
                  {!r.correct && (
                    <div className="mt-2 text-sm">
                      Correct answer: <span className="text-white/90">{q.options[r.correctIndex]}</span>
                    </div>
                  )}
                  {q.explanation && <div className="mt-2 text-xs text-techGray">{q.explanation}</div>}
                </div>
              )
            })}
          </div>
        )}
      </section>
    </Layout>
  )
}
