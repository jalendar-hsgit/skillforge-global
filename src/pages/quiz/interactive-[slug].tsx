import Head from 'next/head'
import Layout from '@/components/Layout'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'
import { ROUTES } from '@/lib/routes'
import { addCredits } from '@/lib/credits'
import QuizTimer from '@/components/quiz/QuizTimer'
import QuizProgress from '@/components/quiz/QuizProgress'
import QuestionFeedback from '@/components/quiz/QuestionFeedback'
import AchievementToast from '@/components/quiz/AchievementToast'

type Q = { id:string; type:'mcq'; text:string; options:string[]; explanation?:string }
type Quiz = { id:string; title:string; questions:Q[]; timeLimit?: number }
type SubmitOut = { score:number; total:number; results:{ id:string; correct:boolean; correctIndex:number; explanation?:string }[] }
type Achievement = { id:string; name:string; description:string; icon:string; points:number; category?:string }

function passThreshold(total: number) {
  return Math.ceil(total * 0.5) // >= 50%
}

export default function InteractiveQuizPage() {
  const { query } = useRouter()
  const slug = String(query.slug || '')
  
  // Quiz state
  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [result, setResult] = useState<SubmitOut | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [earned, setEarned] = useState<number>(0)
  
  // Interactive features
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [showFeedback, setShowFeedback] = useState(false)
  const [currentFeedback, setCurrentFeedback] = useState<any>(null)
  const [startTime, setStartTime] = useState<number>(0)
  const [timeUp, setTimeUp] = useState(false)
  const [unlockedAchievements, setUnlockedAchievements] = useState<Achievement[]>([])

  useEffect(() => {
    if (!slug) return
    setErr(null); setResult(null)
    fetch(`/api/quizzes/list?slug=${slug}`)
      .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
      .then((q: Quiz) => {
        setQuiz(q)
        setStartTime(Date.now())
      })
      .catch(()=>setErr('Quiz not found'))
  }, [slug])

  const currentQuestion = quiz?.questions[currentQuestionIndex]
  const isLastQuestion = currentQuestionIndex === (quiz?.questions.length || 0) - 1
  
  async function handleAnswerSubmit() {
    if (!currentQuestion || answers[currentQuestion.id] === undefined) return
    
    // Move to next question
    if (isLastQuestion) {
      // Submit entire quiz
      await submitQuiz()
    } else {
      setCurrentQuestionIndex(prev => prev + 1)
    }
  }
  
  async function submitQuiz() {
    setErr(null)
    const completionTime = Math.floor((Date.now() - startTime) / 1000)
    
    const payload = {
      path: slug,
      answers: Object.entries(answers).map(([id, idx]) => ({ id, answerIndex: idx }))
    }
    
    const r = await fetch('/api/v1/quizzes/submit', {
      method: 'POST',
      headers: { 'Content-Type':'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload)
    })
    
    if (!r.ok) { 
      const errData = await r.json().catch(() => ({}))
      setErr(typeof errData.detail === 'string' ? errData.detail : 'Submit failed')
      return 
    }
    
    const d: SubmitOut = await r.json()
    setResult(d)

    // Check for achievements
    const newAchievements: Achievement[] = []
    
    // First quiz achievement
    if (await checkFirstQuiz()) {
      newAchievements.push({
        id: 'first_quiz',
        name: 'Quiz Novice',
        description: 'Complete your first quiz',
        icon: '🎯',
        points: 10
      })
    }
    
    // Perfect score achievement
    if (d.score === d.total) {
      newAchievements.push({
        id: 'perfect_score',
        name: 'Perfectionist',
        description: 'Get 100% on any quiz',
        icon: '💯',
        points: 50
      })
      
      await unlockAchievement('perfect_score')
    }
    
    // Speed demon (under 5 minutes)
    if (completionTime < 300 && d.score >= passThreshold(d.total)) {
      newAchievements.push({
        id: 'speed_demon',
        name: 'Speed Demon',
        description: 'Complete a quiz in under 5 minutes',
        icon: '⚡',
        points: 30
      })
      
      await unlockAchievement('speed_demon')
    }
    
    setUnlockedAchievements(newAchievements)

    // If passed, grant +10 Forge AI Credits
    if (d.score >= passThreshold(d.total)) {
      const newBal = addCredits(10)
      setEarned(10)
      console.log('Forge AI Credits balance:', newBal)
      
      // Refresh coin badge in navbar
      if (typeof window !== 'undefined' && (window as any).refreshCoins) {
        setTimeout(() => (window as any).refreshCoins(), 500)
      }
    }
    
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
  
  async function checkFirstQuiz(): Promise<boolean> {
    try {
      const r = await fetch('/api/v1/achievements/me', { credentials: 'include' })
      if (!r.ok) return true // Assume first if can't check
      const data = await r.json()
      const hasFirstQuiz = data.unlocked?.some((a: any) => a.achievement_id === 'first_quiz')
      
      if (!hasFirstQuiz) {
        await unlockAchievement('first_quiz')
        return true
      }
      return false
    } catch {
      return true
    }
  }
  
  async function unlockAchievement(achievementId: string) {
    try {
      await fetch('/api/v1/achievements/unlock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ achievement_id: achievementId })
      })
    } catch (err) {
      console.error('Failed to unlock achievement:', err)
    }
  }
  
  function handleTimeUp() {
    setTimeUp(true)
    submitQuiz()
  }

  return (
    <Layout>
      <Head><title>{`Quiz – ${slug}`}</title></Head>
      
      {/* Achievement toasts */}
      {unlockedAchievements.map((achievement, idx) => (
        <AchievementToast
          key={achievement.id}
          achievement={achievement}
          onClose={() => {
            setUnlockedAchievements(prev => prev.filter(a => a.id !== achievement.id))
          }}
          duration={5000 + idx * 1000} // Stagger multiple achievements
        />
      ))}
      
      {/* Quiz timer */}
      {quiz && !result && quiz.timeLimit && (
        <QuizTimer
          totalSeconds={quiz.timeLimit * 60}
          onTimeUp={handleTimeUp}
          paused={showFeedback}
        />
      )}
      
      <section className="mx-auto max-w-3xl px-6 pt-36 pb-20">
        <Link href={ROUTES.path(slug)} className="text-techGray hover:text-white text-sm">← Back to path</Link>
        <h1 className="text-3xl font-semibold mt-4">{quiz?.title || 'Quiz'}</h1>

        {err && <div className="mt-6 text-red-400 text-sm">{err}</div>}
        
        {timeUp && !result && (
          <div className="mt-6 rounded-xl border border-red-500/50 bg-red-500/10 p-4">
            <div className="text-red-400 font-semibold">⏰ Time's up! Submitting quiz...</div>
          </div>
        )}

        {result && (
          <div className="mt-6 rounded-xl border border-white/10 p-4 bg-white/[0.06]">
            <div className="font-semibold">Score: {result.score} / {result.total}</div>
            <div className="text-xs text-techGray">Pass mark: {passThreshold(result.total)}+</div>
            {earned > 0 && (
              <div className="mt-2 text-sm text-green-400">+{earned} Forge AI Credits earned 🎉</div>
            )}
            <div className="mt-4 flex gap-3 flex-wrap">
              <Link href={ROUTES.path(slug)} className="inline-flex h-10 items-center rounded-md bg-white/10 px-4 border border-white/10 hover:bg-white/20 transition-colors">Back to path</Link>
              <button 
                onClick={()=>{
                  setResult(null)
                  setCurrentQuestionIndex(0)
                  setAnswers({})
                  setStartTime(Date.now())
                  setTimeUp(false)
                }} 
                className="h-10 rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue px-4 font-semibold hover:opacity-90 transition-opacity"
              >
                Retake
              </button>
              <Link href={ROUTES.dashboard} className="inline-flex h-10 items-center rounded-md bg-white/10 px-4 border border-white/10 hover:bg-white/20 transition-colors">Dashboard</Link>
            </div>
          </div>
        )}

        {!result && quiz && (
          <div className="mt-6">
            <QuizProgress 
              current={currentQuestionIndex + 1} 
              total={quiz.questions.length} 
            />
            
            {currentQuestion && (
              <div className="rounded-xl border border-white/10 p-6 bg-white/[0.06]">
                <div className="font-medium text-lg mb-4">
                  {currentQuestionIndex + 1}. {currentQuestion.text}
                </div>
                
                <div className="grid gap-3">
                  {currentQuestion.options.map((opt, idx) => (
                    <label 
                      key={idx} 
                      className={`flex items-center gap-3 p-3 rounded-lg border transition-all cursor-pointer ${
                        answers[currentQuestion.id] === idx
                          ? 'border-forgePurple bg-forgePurple/10'
                          : 'border-white/10 hover:border-white/30 hover:bg-white/5'
                      }`}
                    >
                      <input
                        type="radio"
                        name={currentQuestion.id}
                        checked={answers[currentQuestion.id] === idx}
                        onChange={()=>setAnswers({...answers, [currentQuestion.id]: idx})}
                        className="w-4 h-4"
                        disabled={showFeedback}
                      />
                      <span className="flex-1">{opt}</span>
                    </label>
                  ))}
                </div>
                
                {answers[currentQuestion.id] !== undefined && (
                  <button
                    onClick={handleAnswerSubmit}
                    className="mt-6 h-12 rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue px-6 font-semibold hover:opacity-90 transition-opacity"
                  >
                    {isLastQuestion ? 'Submit Quiz' : 'Next Question →'}
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {result && quiz && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4">Review Answers</h2>
            <div className="space-y-6">
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
                        <div className="text-techGray">Your answer: <span className="text-white/70">{q.options[answers[q.id]]}</span></div>
                        <div className="text-techGray mt-1">Correct answer: <span className="text-white">{q.options[r.correctIndex]}</span></div>
                      </div>
                    )}
                    {q.explanation && <div className="mt-2 text-xs text-techGray italic">{q.explanation}</div>}
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </section>
    </Layout>
  )
}
