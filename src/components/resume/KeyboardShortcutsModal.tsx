import { X, Keyboard } from 'lucide-react'

interface KeyboardShortcutsModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function KeyboardShortcutsModal({ isOpen, onClose }: KeyboardShortcutsModalProps) {
  if (!isOpen) return null

  const shortcuts = [
    { keys: ['Ctrl', 'S'], description: 'Save resume' },
    { keys: ['Ctrl', 'Z'], description: 'Undo last change' },
    { keys: ['Ctrl', 'Y'], description: 'Redo change' },
    { keys: ['Ctrl', 'P'], description: 'Open preview in new tab' },
    { keys: ['Ctrl', 'B'], description: 'Toggle split view' },
    { keys: ['Ctrl', 'Shift', 'A'], description: 'Toggle AI assistant' },
    { keys: ['Ctrl', '+'], description: 'Zoom in (preview)' },
    { keys: ['Ctrl', '-'], description: 'Zoom out (preview)' },
    { keys: ['Ctrl', '0'], description: 'Reset zoom (preview)' },
    { keys: ['Esc'], description: 'Exit fullscreen preview' },
    { keys: ['?'], description: 'Show this help' },
  ]

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-gradient-to-br from-deepTech to-deepTech/90 rounded-2xl shadow-2xl border border-white/20 max-w-2xl w-full mx-4 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-forgePurple to-neuralBlue rounded-lg">
              <Keyboard className="w-5 h-5 text-white" />
            </div>
            <h3 className="text-xl font-black text-white">Keyboard Shortcuts</h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-all text-white/70 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Shortcuts List */}
        <div className="p-6 max-h-[70vh] overflow-y-auto">
          <div className="space-y-3">
            {shortcuts.map((shortcut, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-all"
              >
                <span className="text-sm text-white/80">{shortcut.description}</span>
                <div className="flex items-center gap-1">
                  {shortcut.keys.map((key, i) => (
                    <span key={i} className="flex items-center gap-1">
                      <kbd className="px-3 py-1.5 bg-white/10 border border-white/20 rounded text-xs font-mono text-white shadow-sm min-w-[2.5rem] text-center">
                        {key}
                      </kbd>
                      {i < shortcut.keys.length - 1 && (
                        <span className="text-white/40 text-xs">+</span>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Platform Note */}
          <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <p className="text-xs text-blue-200/80">
              💡 <strong>Tip:</strong> On macOS, use <kbd className="px-2 py-0.5 bg-white/10 rounded font-mono">Cmd</kbd> instead of <kbd className="px-2 py-0.5 bg-white/10 rounded font-mono">Ctrl</kbd>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-white/10 bg-white/5 text-center">
          <p className="text-xs text-white/50">
            Press <kbd className="px-2 py-0.5 bg-white/10 rounded font-mono text-white/70">?</kbd> anytime to toggle this dialog
          </p>
        </div>
      </div>
    </div>
  )
}
