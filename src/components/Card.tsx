import type { ReactNode, HTMLAttributes } from 'react'

type CardProps = HTMLAttributes<HTMLDivElement> & { children: ReactNode; className?: string }

export function Card({ children, className = '', ...props }: CardProps) {
  return (
    <div
      className={`rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm shadow-glow ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardBody({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`p-6 sm:p-8 ${className}`}>{children}</div>
}
