import { cn } from './utils'
import { motion } from 'framer-motion'
import React from 'react'
import type { MotionProps } from 'framer-motion'

interface ButtonProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'className'> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  className?: string
  children?: React.ReactNode
}

export function Button({
  className, variant = 'primary', size = 'md', children, loading, ...props
}: ButtonProps) {
  const sizes =
    size === 'sm' ? 'h-10 px-4 text-sm'
    : size === 'lg' ? 'h-14 px-7 text-base'
    : 'h-12 px-6 text-sm'

  const styles =
    variant === 'primary'
      ? 'text-white bg-gradient-to-r from-forgePurple to-neuralBlue shadow-glow hover:opacity-95'
      : variant === 'secondary'
      ? 'text-aiElectric border border-aiElectric/60 hover:bg-aiElectric/10'
      : variant === 'outline'
      ? 'text-white border border-white/30 hover:bg-white/10'
      : 'text-techGray hover:text-white hover:bg-white/5'

  const base =
    'inline-flex items-center justify-center rounded-2xl font-display font-semibold tracking-wide transition-all duration-200 ' +
    'focus:outline-none focus:ring-2 focus:ring-forgePurple/40 focus:ring-offset-2 focus:ring-offset-deepTech ' +
    'disabled:opacity-60 disabled:cursor-not-allowed shadow-glow hover:scale-105 active:scale-95'

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={cn(base, sizes, styles, className)}
      {...(props as MotionProps & React.ButtonHTMLAttributes<HTMLButtonElement>)}
    >
      {children}
    </motion.button>
  )
}
// Default export for backwards compatibility
export default Button