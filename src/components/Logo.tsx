export function Logo({ className = '' }: { className?: string }) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <svg width="28" height="28" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#6B3BFF" />
            <stop offset="100%" stopColor="#1E9EFF" />
          </linearGradient>
        </defs>
        <circle cx="32" cy="32" r="24" stroke="url(#g)" strokeWidth="3" />
        <circle cx="32" cy="8" r="3" fill="#6B3BFF" />
        <circle cx="56" cy="32" r="3" fill="#1E9EFF" />
        <circle cx="32" cy="56" r="3" fill="#6B3BFF" />
        <circle cx="8" cy="32" r="3" fill="#1E9EFF" />
        <circle cx="48" cy="16" r="3" fill="#6B3BFF" />
        <circle cx="16" cy="48" r="3" fill="#1E9EFF" />
        <path d="M32 8 L48 16 L56 32 L48 48 L32 56 L16 48 L8 32 L16 16 Z" stroke="url(#g)" strokeWidth="2" fill="none" />
      </svg>
      <span className="text-lg font-semibold tracking-wide">SkillForge Global</span>
    </div>
  )
}
