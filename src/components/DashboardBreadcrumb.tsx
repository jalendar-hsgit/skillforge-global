'use client'

import Link from 'next/link'
import { useRouter } from 'next/router'

interface BreadcrumbItem {
  label: string
  href?: string
}

interface DashboardBreadcrumbProps {
  items: BreadcrumbItem[]
}

export default function DashboardBreadcrumb({ items }: DashboardBreadcrumbProps) {
  const router = useRouter()

  return (
    <nav className="flex items-center space-x-2 text-sm">
      {/* Home Link */}
      <Link
        href="/mentors/dashboard"
        className="text-techGray hover:text-forgePurple transition-colors flex items-center gap-1"
      >
        <span>🏠</span>
        <span>Dashboard</span>
      </Link>

      {/* Breadcrumb Items */}
      {items.map((item, index) => (
        <div key={index} className="flex items-center space-x-2">
          {/* Separator */}
          <span className="text-white/30">/</span>

          {/* Item */}
          {item.href ? (
            <Link
              href={item.href}
              className="text-techGray hover:text-forgePurple transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-white font-medium">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  )
}
