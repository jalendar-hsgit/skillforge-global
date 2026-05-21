import { Columns, Maximize2 } from 'lucide-react'

interface SplitViewToggleProps {
  isSplitView: boolean
  onToggle: () => void
  className?: string
}

export default function SplitViewToggle({ isSplitView, onToggle, className = '' }: SplitViewToggleProps) {
  return (
    <button
      onClick={onToggle}
      className={`${className} flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all ${
        isSplitView 
          ? 'bg-blue-500/20 border-blue-500/30 text-blue-200 hover:bg-blue-500/30' 
          : 'bg-white/10 border-white/20 text-white/70 hover:bg-white/20 hover:text-white'
      }`}
      title={isSplitView ? 'Exit Split View' : 'Enable Split View'}
    >
      {isSplitView ? (
        <>
          <Maximize2 className="w-4 h-4" />
          <span className="text-xs font-medium">Full Width</span>
        </>
      ) : (
        <>
          <Columns className="w-4 h-4" />
          <span className="text-xs font-medium">Split View</span>
        </>
      )}
    </button>
  )
}
