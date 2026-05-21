/**
 * DashboardListItem - Reusable list item component
 * Replaces repetitive list item HTML across dashboard pages
 * Ensures consistent styling and hover effects
 */

interface DashboardListItemProps {
  children: React.ReactNode
  hoverColor?: 'purple' | 'blue' | 'electric'
  onClick?: () => void
  className?: string
}

export default function DashboardListItem({
  children,
  hoverColor = 'purple',
  onClick,
  className = ''
}: DashboardListItemProps) {
  const hoverMap = {
    purple: 'hover:border-forgePurple/50',
    blue: 'hover:border-techBlue/50',
    electric: 'hover:border-aiElectric/50'
  }

  return (
    <div
      className={`bg-white/5 border border-white/10 rounded-lg p-6 ${hoverMap[hoverColor]} transition ${
        onClick ? 'cursor-pointer' : ''
      } ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  )
}
