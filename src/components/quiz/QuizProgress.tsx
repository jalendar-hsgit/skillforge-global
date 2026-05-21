/**
 * QuizProgress - Visual progress indicator showing current question
 * Shows completion percentage and question number
 */
interface QuizProgressProps {
  current: number
  total: number
}

export default function QuizProgress({ current, total }: QuizProgressProps) {
  const percentage = (current / total) * 100
  
  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-2 text-sm">
        <span className="text-techGray">Question {current} of {total}</span>
        <span className="text-white/70">{Math.round(percentage)}%</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-forgePurple to-neuralBlue transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
