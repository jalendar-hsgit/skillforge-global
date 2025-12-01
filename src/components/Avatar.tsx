import React from 'react';
import clsx from 'clsx';

type Size = 'sm' | 'md' | 'lg' | 'xl';

const sizeMap: Record<Size, string> = {
  sm: 'w-8 h-8 text-sm',
  md: 'w-12 h-12 text-lg',
  lg: 'w-16 h-16 text-2xl',
  xl: 'w-32 h-32 text-5xl',
};

export function Avatar({ name, size = 'md', className }: { name?: string; size?: Size; className?: string }) {
  const letter = (name || 'M').trim().charAt(0).toUpperCase() || 'M';
  return (
    <div
      className={clsx(
        'rounded-full flex items-center justify-center text-white font-bold bg-gradient-to-br from-blue-500 to-purple-600',
        sizeMap[size],
        className
      )}
    >
      {letter}
    </div>
  );
}
