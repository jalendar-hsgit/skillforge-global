import { useState, useCallback, useRef } from 'react'
import { Undo2, Redo2, History } from 'lucide-react'

interface HistoryState<T> {
  past: T[]
  present: T
  future: T[]
}

interface UseUndoRedoReturn<T> {
  state: T
  setState: (newState: T | ((prev: T) => T)) => void
  undo: () => void
  redo: () => void
  canUndo: boolean
  canRedo: boolean
  history: T[]
  clearHistory: () => void
}

export function useUndoRedo<T>(initialState: T, maxHistory: number = 50): UseUndoRedoReturn<T> {
  const [history, setHistory] = useState<HistoryState<T>>({
    past: [],
    present: initialState,
    future: [],
  })

  const setState = useCallback((newState: T | ((prev: T) => T)) => {
    setHistory((currentHistory) => {
      const resolvedState = typeof newState === 'function' 
        ? (newState as (prev: T) => T)(currentHistory.present)
        : newState

      // Don't add to history if state hasn't changed
      if (JSON.stringify(resolvedState) === JSON.stringify(currentHistory.present)) {
        return currentHistory
      }

      const newPast = [...currentHistory.past, currentHistory.present].slice(-maxHistory)

      return {
        past: newPast,
        present: resolvedState,
        future: [], // Clear future when new state is set
      }
    })
  }, [maxHistory])

  const undo = useCallback(() => {
    setHistory((currentHistory) => {
      if (currentHistory.past.length === 0) return currentHistory

      const previous = currentHistory.past[currentHistory.past.length - 1]
      const newPast = currentHistory.past.slice(0, -1)

      return {
        past: newPast,
        present: previous,
        future: [currentHistory.present, ...currentHistory.future],
      }
    })
  }, [])

  const redo = useCallback(() => {
    setHistory((currentHistory) => {
      if (currentHistory.future.length === 0) return currentHistory

      const next = currentHistory.future[0]
      const newFuture = currentHistory.future.slice(1)

      return {
        past: [...currentHistory.past, currentHistory.present],
        present: next,
        future: newFuture,
      }
    })
  }, [])

  const clearHistory = useCallback(() => {
    setHistory({
      past: [],
      present: history.present,
      future: [],
    })
  }, [history.present])

  return {
    state: history.present,
    setState,
    undo,
    redo,
    canUndo: history.past.length > 0,
    canRedo: history.future.length > 0,
    history: [... history.past, history.present, ...history.future],
    clearHistory,
  }
}

interface UndoRedoControlsProps {
  canUndo: boolean
  canRedo: boolean
  onUndo: () => void
  onRedo: () => void
  historyCount?: number
  className?: string
}

export function UndoRedoControls({
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  historyCount = 0,
  className = ''
}: UndoRedoControlsProps) {
  return (
    <div className={`${className} flex items-center gap-2`}>
      <button
        onClick={onUndo}
        disabled={!canUndo}
        className={`p-2 rounded-lg border transition-all ${
          canUndo
            ? 'bg-white/10 border-white/20 text-white hover:bg-white/20 hover:scale-105'
            : 'bg-white/5 border-white/10 text-white/30 cursor-not-allowed'
        }`}
        title="Undo (Ctrl+Z)"
      >
        <Undo2 className="w-4 h-4" />
      </button>
      
      <button
        onClick={onRedo}
        disabled={!canRedo}
        className={`p-2 rounded-lg border transition-all ${
          canRedo
            ? 'bg-white/10 border-white/20 text-white hover:bg-white/20 hover:scale-105'
            : 'bg-white/5 border-white/10 text-white/30 cursor-not-allowed'
        }`}
        title="Redo (Ctrl+Y)"
      >
        <Redo2 className="w-4 h-4" />
      </button>

      {historyCount > 0 && (
        <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg">
          <History className="w-3.5 h-3.5 text-white/60" />
          <span className="text-xs text-white/70 font-medium">{historyCount}</span>
        </div>
      )}
    </div>
  )
}

interface AutoSaveIndicatorProps {
  status: 'saving' | 'saved' | 'error' | 'idle'
  lastSaved?: Date | null
  error?: string
  className?: string
}

export function AutoSaveIndicator({
  status,
  lastSaved,
  error,
  className = ''
}: AutoSaveIndicatorProps) {
  const getStatusConfig = () => {
    switch (status) {
      case 'saving':
        return {
          icon: '⏳',
          text: 'Saving...',
          color: 'text-yellow-400',
          bg: 'bg-yellow-500/10',
          border: 'border-yellow-500/30',
        }
      case 'saved':
        return {
          icon: '✓',
          text: lastSaved ? `Saved ${lastSaved.toLocaleTimeString()}` : 'Saved',
          color: 'text-green-400',
          bg: 'bg-green-500/10',
          border: 'border-green-500/30',
        }
      case 'error':
        return {
          icon: '⚠',
          text: error || 'Save failed',
          color: 'text-red-400',
          bg: 'bg-red-500/10',
          border: 'border-red-500/30',
        }
      default:
        return {
          icon: '—',
          text: 'Not saved',
          color: 'text-white/50',
          bg: 'bg-white/5',
          border: 'border-white/10',
        }
    }
  }

  const config = getStatusConfig()

  return (
    <div className={`${className} flex items-center gap-2 px-3 py-1.5 rounded-lg border ${config.bg} ${config.border}`}>
      <span className={`${config.color} ${status === 'saving' ? 'animate-spin' : ''}`}>
        {config.icon}
      </span>
      <span className={`text-xs font-medium ${config.color}`}>
        {config.text}
      </span>
    </div>
  )
}
