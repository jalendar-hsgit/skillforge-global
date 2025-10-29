import React from 'react'

type Props = React.InputHTMLAttributes<HTMLInputElement> & { label?: string }

export function Input({ label, className = '', ...props }: Props) {
  return (
    <label className="block">
      {label && <div className="mb-2 text-sm text-techGray">{label}</div>}
      <input
        className={
          'w-full h-12 rounded-xl bg-white/5 border border-white/10 px-4 ' +
          'placeholder:text-techGray/70 outline-none focus:ring-2 focus:ring-aiElectric/40 ' +
          className
        }
        {...props}
      />
    </label>
  )
}
