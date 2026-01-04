/**
 * DashboardSectionHeader - Reusable section header component
 * Replaces repetitive section header HTML across dashboard pages
 * Ensures consistent styling and spacing
 */

interface DashboardSectionHeaderProps {
  title: string
  subtitle?: string
  action?: React.ReactNode
}

export default function DashboardSectionHeader({
  title,
  subtitle,
  action
}: DashboardSectionHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-6">
      <div>
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        {subtitle && <p className="text-sm text-techGray-400 mt-1">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}
