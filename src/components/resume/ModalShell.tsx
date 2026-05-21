import { X } from 'lucide-react'
import React from 'react'

type Accent = 'purple' | 'blue' | 'green' | 'amber' | 'red' | 'gray'
type Size = 'md' | 'lg' | 'xl'

const accentHeaderBg: Record<Accent, string> = {
  purple: 'from-forgePurple/10 via-neuralBlue/10 to-forgePurple/10',
  blue: 'from-blue-500/10 via-blue-600/10 to-blue-500/10',
  green: 'from-green-500/10 via-emerald-600/10 to-green-500/10',
  amber: 'from-amber-500/10 via-yellow-600/10 to-amber-500/10',
  red: 'from-rose-500/10 via-red-600/10 to-rose-500/10',
  gray: 'from-white/5 via-white/10 to-white/5',
}

const containerMaxWidth: Record<Size, string> = {
  md: 'max-w-2xl',
  lg: 'max-w-4xl',
  xl: 'max-w-6xl',
}

interface ModalShellProps {
  isOpen: boolean
  onClose: () => void
  title: string
  icon?: React.ReactNode
  accent?: Accent
  size?: Size
  footer?: React.ReactNode
  children: React.ReactNode
}

export default function ModalShell({
  isOpen,
  onClose,
  title,
  icon,
  accent = 'purple',
  size = 'lg',
  footer,
  children,
}: ModalShellProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-md"
        onClick={onClose}
      />

      {/* Container */}
      <div
        className={`relative bg-gradient-to-br from-deepTech via-deepTech/95 to-deepTech/90 border-2 border-white/20 rounded-3xl shadow-2xl w-full ${containerMaxWidth[size]} mx-6 max-h-[90vh] overflow-hidden`}
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className={`relative px-8 py-6 border-b border-white/10 bg-gradient-to-r ${accentHeaderBg[accent]}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 min-w-0">
              {icon && <div className="p-3 bg-white/5 rounded-xl text-white/90">{icon}</div>}
              <h2 className="text-2xl md:text-3xl font-black truncate" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
                <span className="bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
                  {title}
                </span>
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-3 hover:bg-white/10 rounded-xl transition-all duration-200 group"
              aria-label="Close"
            >
              <X className="w-6 h-6 text-techGray group-hover:text-white transition-colors" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 md:p-8 overflow-y-auto max-h-[calc(90vh-140px)]">
          {children}
        </div>

        {footer && (
          <div className="flex items-center justify-between gap-3 px-6 md:px-8 py-5 border-t border-white/10">
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}
