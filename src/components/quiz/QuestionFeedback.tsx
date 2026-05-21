/**
 * QuestionFeedback - Immediate visual feedback after answering
 * Shows if answer is correct/incorrect with explanation
 */
import { useEffect, useState } from 'react'

interface QuestionFeedbackProps {
  isCorrect: boolean
  correctAnswer: string
  explanation?: string
  userAnswer: string
  onNext?: () => void
  isLastQuestion?: boolean
}

export default function QuestionFeedback({
  isCorrect,
  correctAnswer,
  explanation,
  userAnswer,
  onNext,
  isLastQuestion = false
}: QuestionFeedbackProps) {
  const [show, setShow] = useState(false)
  
  useEffect(() => {
    // Animate in
    setTimeout(() => setShow(true), 50)
  }, [])
  
  return (
    <div 
      className={`mt-4 rounded-xl border p-4 transition-all duration-300 ${
        show ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      } ${
        isCorrect 
          ? 'border-green-500/50 bg-green-500/10' 
          : 'border-red-500/50 bg-red-500/10'
      }`}
    >
      <div className="flex items-center gap-2 mb-2">
        {isCorrect ? (
          <>
            <span className="text-2xl">✓</span>
            <span className="text-green-400 font-semibold">Correct!</span>
          </>
        ) : (
          <>
            <span className="text-2xl">✗</span>
            <span className="text-red-400 font-semibold">Incorrect</span>
          </>
        )}
      </div>
      
      {!isCorrect && (
        <div className="mb-2 text-sm">
          <div className="text-techGray">Your answer: <span className="text-white/70">{userAnswer}</span></div>
          <div className="text-techGray mt-1">Correct answer: <span className="text-white">{correctAnswer}</span></div>
        </div>
      )}
      
      {explanation && (
        <div className="mt-3 pt-3 border-t border-white/10">
          <div className="text-xs text-techGray mb-1">Explanation</div>
          <div className="text-sm text-white/90">{explanation}</div>
        </div>
      )}
      
      {onNext && (
        <button
          onClick={onNext}
          className="mt-4 h-10 rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue px-6 font-semibold hover:opacity-90 transition-opacity"
        >
          {isLastQuestion ? 'View Results' : 'Next Question'}
        </button>
      )}
    </div>
  )
}
