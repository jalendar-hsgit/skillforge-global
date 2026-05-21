/**
 * DashboardStatCard - Reusable stat card component
 * Replaces repetitive stat card HTML across dashboard pages
 * Ensures consistent styling and color scheme
 */

interface DashboardStatCardProps {
  label: string
  value: string | number
  subtitle?: string
  color: 'purple' | 'blue' | 'electric' | 'green'
  icon?: string
}

export default function DashboardStatCard({
  label,
  value,
  subtitle,
  color,
  icon
}: DashboardStatCardProps) {
  const colorMap = {
    purple: {
      gradient: 'from-forgePurple/20 to-forgePurple/10',
      border: 'border-forgePurple/30',
      text: 'text-forgePurple'
    },
    blue: {
      gradient: 'from-techBlue/20 to-techBlue/10',
      border: 'border-techBlue/30',
      text: 'text-techBlue'
    },
    electric: {
      gradient: 'from-aiElectric/20 to-aiElectric/10',
      border: 'border-aiElectric/30',
      text: 'text-aiElectric'
    },
    green: {
      gradient: 'from-success/20 to-success/10',
      border: 'border-success/30',
      text: 'text-success'
    }
  }

  const colors = colorMap[color]

  return (
    <div
      className={`bg-gradient-to-br ${colors.gradient} border ${colors.border} rounded-xl p-6`}
    >
      {icon && <div className="text-3xl mb-3">{icon}</div>}
      <p className="text-sm text-techGray-400 mb-2">{label}</p>
      <p className={`text-3xl font-bold ${colors.text}`}>{value}</p>
      {subtitle && <p className="text-xs text-success mt-2">{subtitle}</p>}
    </div>
  )
}
