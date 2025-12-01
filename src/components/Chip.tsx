import React from 'react';
import clsx from 'clsx';

export function Chip({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={clsx('px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium', className)}>
      {children}
    </span>
  );
}
