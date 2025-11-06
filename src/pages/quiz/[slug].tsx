import Head from 'next/head'
import Layout from '@/components/Layout'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { useEffect, useMemo, useRef, useState } from 'react'
import { ROUTES } from '@/lib/routes'
import { addCredits } from '@/lib/credits'

type Q = { id:string; type:'mcq'; text:string; options:string[]; answerIndex:number; explanation?:string }
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
  const [passedBefore, setPassedBefore] = useState<boolean | null>(null)
  const [secondsLeft, setSecondsLeft] = useState<number>(0)
  const timerRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!slug) return
    setErr(null); setResult(null); setEarned(0); setPassedBefore(null)
    // load quiz data
    fetch(`/api/quizzes/list?slug=${slug}`)
      .then(async r => {
        if (r.ok) return r.json()
        // fallback to AI-generated quiz
        const gen = await fetch('/api/quizzes/generate', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ topic: slug, difficulty: 'medium', num_questions: 6, options_per_question: 4 })
        })
        if (gen.ok) return gen.json()
        throw new Error(await r.text().catch(()=> 'load failed'))
      })
      .then((q: Quiz) => {
        setQuiz(q)
        // initialize a simple time limit: 30s per question, min 60s, max 15min
        const perQ = 30
        const total = Math.min(Math.max((q?.questions?.length || 0) * perQ, 60), 15 * 60)
        setSecondsLeft(total)
      })
      .catch(()=>setErr('Quiz not found'))
    // check previous status (optional, best-effort)
    fetch(`/api/quizzes/status?path=${slug}`, { credentials: 'include' as any })
      .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
      .then(d => setPassedBefore(!!d?.passed))
      .catch(() => {})
  }, [slug])

  // Start countdown when quiz is loaded and not yet submitted
  useEffect(() => {
    if (!quiz || result) return
    if (timerRef.current) clearInterval(timerRef.current)
    if (secondsLeft <= 0) return
    timerRef.current = setInterval(() => {
      setSecondsLeft(prev => {
        if (prev <= 1) {
          // auto-submit when time is up
          if (!result) {
            setTimeout(() => {
              const fakeEvt = { preventDefault: () => {} } as unknown as React.FormEvent
              onSubmit(fakeEvt)
            }, 0)
          }
          if (timerRef.current) clearInterval(timerRef.current)
          return 0
        }
        return prev - 1
      })
    }, 1000)
    return () => { if (timerRef.current) clearInterval(timerRef.current) }
  }, [quiz, result])

  const answeredCount = useMemo(() => Object.keys(answers).length, [answers])
  const totalQuestions = quiz?.questions?.length || 0
  const progressPct = totalQuestions ? Math.round((answeredCount / totalQuestions) * 100) : 0
  const minutes = Math.floor(Math.max(secondsLeft, 0) / 60)
  const seconds = Math.max(secondsLeft, 0) % 60

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setErr(null)
    const payload = {
      path: slug,
      answers: Object.entries(answers).map(([id, idx]) => ({ id, answerIndex: idx }))
    }
    // If this quiz was AI-generated (no static entry), submit via AI endpoint
    const isAi = quiz && quiz.id && String(quiz.id).startsWith('ai-')
    const r = await fetch(isAi ? '/api/quizzes/submit-ai' : '/api/v1/quizzes/submit', {
      method: 'POST',
      headers: { 'Content-Type':'application/json' },
      credentials: 'include',
      body: JSON.stringify(isAi ? { path: slug, questions: quiz?.questions, answers: payload.answers } : payload)
    })
    if (!r.ok) { 
      const errData = await r.json().catch(() => ({}))
      setErr(typeof errData.detail === 'string' ? errData.detail : 'Submit failed')
      return 
    }
    const d: SubmitOut = await r.json()
    setResult(d)

    // If passed, grant +10 Forge AI Credits
    if (d.score >= passThreshold(d.total)) {
      const newBal = addCredits(10)
      setEarned(10)
      console.log('Forge AI Credits balance:', newBal)
      
      // Refresh coin badge in navbar
      if (typeof window !== 'undefined' && (window as any).refreshCoins) {
        setTimeout(() => (window as any).refreshCoins(), 500)
      }

      // Unlock achievements: generic pass + perfect score
      try {
        await fetch('/api/achievements/unlock', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            key: `quiz:${slug}:passed`,
            title: `Passed ${quiz?.title || slug} Quiz`,
            description: `You passed the ${quiz?.title || slug} quiz!`,
            points: 5,
          }),
        })
        if (d.score === d.total) {
          await fetch('/api/achievements/unlock', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
              key: `quiz:${slug}:perfect`,
              title: `Perfect Score – ${quiz?.title || slug}`,
              description: `You aced the ${quiz?.title || slug} quiz with a perfect score.`,
              points: 10,
            }),
          })
        }
      } catch {}
    }
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <Layout>
      <Head><title>{`Quiz – ${slug}`}</title></Head>
      <section className="mx-auto max-w-3xl px-6 pt-36 pb-20">
        <Link href={ROUTES.path(slug)} className="text-techGray hover:text-white text-sm">← Back to path</Link>
        <h1 className="text-3xl font-semibold mt-4">{quiz?.title || 'Quiz'}</h1>

        {passedBefore && (
          <div className="mt-3 rounded-lg border border-green-500/20 bg-green-500/10 px-3 py-2 text-sm text-green-300">
            You have already passed this quiz. Retakes won’t change your status, but you can try for a perfect score.
          </div>
        )}

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
            {/* Timer + progress bar */}
            <div className="rounded-xl border border-white/10 p-4 bg-white/[0.06]">
              <div className="flex items-center justify-between text-sm">
                <div className="text-techGray">Progress</div>
                <div className="font-mono tabular-nums">{String(minutes).padStart(2,'0')}:{String(seconds).padStart(2,'0')}</div>
              </div>
              <div className="mt-2 h-2 w-full rounded bg-white/10">
                <div className="h-2 rounded bg-gradient-to-r from-forgePurple to-neuralBlue" style={{ width: `${progressPct}%` }} />
              </div>
              <div className="mt-1 text-xs text-techGray">Answered {answeredCount} / {totalQuestions}</div>
            </div>

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
                {answers[q.id] !== undefined && (
                  <div className="mt-2 text-sm">
                    {answers[q.id] === q.answerIndex ? (
                      <span className="text-green-400">✓ Correct</span>
                    ) : (
                      <span className="text-red-400">✗ Incorrect</span>
                    )}
                  </div>
                )}
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
                    {r.correct ? <span className="text-green-400">✓ Correct</span> : <span className="text-red-400">✗ Incorrect</span>}
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
