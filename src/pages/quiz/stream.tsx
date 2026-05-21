import Head from 'next/head'
import Layout from '@/components/Layout'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'
import { ROUTES } from '@/lib/routes'
import { useQuizStream, QuizQuestion, QuizMetadata } from '@/lib/quizStream'

export default function StreamingQuizPage() {
  const { query } = useRouter()
  const topic = String(query.topic || '')
  const difficulty = String(query.difficulty || 'medium') as 'easy' | 'medium' | 'hard'
  
  const [metadata, setMetadata] = useState<QuizMetadata | null>(null)
  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isComplete, setIsComplete] = useState(false)
  const [generationStartTime, setGenerationStartTime] = useState<number>(0)
  
  const { startStream, stopStream } = useQuizStream()
  
  useEffect(() => {
    if (!topic) return
    
    setIsGenerating(true)
    setError(null)
    setQuestions([])
    setMetadata(null)
    setIsComplete(false)
    setGenerationStartTime(Date.now())
    
    startStream(
      {
        topic,
        difficulty,
        num_questions: 5,
        options_per_question: 4
      },
      {
        onMetadata: (meta) => {
          console.log('Quiz metadata:', meta)
          setMetadata(meta)
        },
        onQuestion: (question, index) => {
          console.log(`Question ${index + 1} arrived:`, question)
          setQuestions(prev => [...prev, question])
        },
        onComplete: (total) => {
          console.log(`Generation complete: ${total} questions`)
          setIsGenerating(false)
          setIsComplete(true)
        },
        onError: (err) => {
          console.error('Stream error:', err)
          setError(err)
          setIsGenerating(false)
        }
      }
    ).catch(err => {
      console.error('Failed to start stream:', err)
      setError(err.message || 'Failed to start generation')
      setIsGenerating(false)
    })
    
    return () => {
      stopStream()
    }
  }, [topic, difficulty])
  
  const elapsedSeconds = isGenerating && generationStartTime 
    ? Math.floor((Date.now() - generationStartTime) / 1000)
    : 0
  
  return (
    <Layout>
      <Head><title>Streaming Quiz Generation – {topic}</title></Head>
      
      <section className="mx-auto max-w-4xl px-6 pt-36 pb-20">
        <Link href={ROUTES.paths} className="text-techGray hover:text-white text-sm">← Back to paths</Link>
        
        <div className="mt-6">
          <h1 className="text-3xl font-semibold">
            {metadata?.title || `Generating ${topic} Quiz...`}
          </h1>
          
          {isGenerating && (
            <div className="mt-4 rounded-xl border border-forgePurple/50 bg-forgePurple/10 p-4">
              <div className="flex items-center gap-3">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <div>
                  <div className="font-semibold text-white">AI is crafting your quiz...</div>
                  <div className="text-xs text-techGray mt-1">
                    Generated {questions.length} questions • {elapsedSeconds}s elapsed
                  </div>
                </div>
              </div>
              
              {/* Progress bar */}
              <div className="mt-3 h-1 bg-white/10 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-forgePurple to-neuralBlue transition-all duration-500"
                  style={{ width: `${(questions.length / 5) * 100}%` }}
                />
              </div>
            </div>
          )}
          
          {isComplete && (
            <div className="mt-4 rounded-xl border border-green-500/50 bg-green-500/10 p-4">
              <div className="flex items-center gap-2">
                <span className="text-2xl">✓</span>
                <div>
                  <div className="font-semibold text-green-400">Quiz ready!</div>
                  <div className="text-xs text-techGray mt-1">
                    {questions.length} questions generated in {Math.floor((Date.now() - generationStartTime) / 1000)}s
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {error && (
            <div className="mt-4 rounded-xl border border-red-500/50 bg-red-500/10 p-4">
              <div className="flex items-center gap-2">
                <span className="text-2xl">✗</span>
                <div>
                  <div className="font-semibold text-red-400">Generation failed</div>
                  <div className="text-sm text-red-300 mt-1">{error}</div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Questions appear as they're generated */}
        <div className="mt-8 space-y-6">
          {questions.map((q, index) => (
            <div
              key={q.id}
              className="rounded-xl border border-white/10 p-6 bg-white/[0.06] animate-fadeIn"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-forgePurple to-neuralBlue flex items-center justify-center font-bold">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="font-medium text-lg mb-3">{q.text}</div>
                  
                  <div className="grid gap-2">
                    {q.options.map((opt, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-3 p-3 rounded-lg border border-white/10 hover:border-white/30 transition-colors"
                      >
                        <div className="w-6 h-6 rounded-full border-2 border-white/30" />
                        <span className="text-sm">{opt}</span>
                      </div>
                    ))}
                  </div>
                  
                  {q.explanation && (
                    <details className="mt-3 text-sm">
                      <summary className="cursor-pointer text-techGray hover:text-white">
                        Show explanation
                      </summary>
                      <div className="mt-2 text-white/80 italic">{q.explanation}</div>
                    </details>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {isComplete && questions.length > 0 && (
          <div className="mt-8 flex gap-4">
            <Link
              href={`/quiz/${topic}?generated=true`}
              className="h-12 rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue px-6 font-semibold inline-flex items-center hover:opacity-90 transition-opacity"
            >
              Start Quiz →
            </Link>
            <button
              onClick={() => {
                setQuestions([])
                setMetadata(null)
                setIsComplete(false)
                setIsGenerating(true)
                setGenerationStartTime(Date.now())
                startStream(
                  { topic, difficulty, num_questions: 5, options_per_question: 4 },
                  {
                    onMetadata: setMetadata,
                    onQuestion: (q, i) => setQuestions(prev => [...prev, q]),
                    onComplete: () => { setIsGenerating(false); setIsComplete(true) },
                    onError: (err) => { setError(err); setIsGenerating(false) }
                  }
                )
              }}
              className="h-12 rounded-md bg-white/10 px-6 font-semibold border border-white/10 hover:bg-white/20 transition-colors"
            >
              Generate New Quiz
            </button>
          </div>
        )}
      </section>
      
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out forwards;
          opacity: 0;
        }
      `}</style>
    </Layout>
  )
}
