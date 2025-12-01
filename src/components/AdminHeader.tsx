import { useRouter } from 'next/router'
import Link from 'next/link'

type AdminHeaderProps = {
  title: string
  showBackButton?: boolean
  backUrl?: string
  actions?: React.ReactNode
}

export default function AdminHeader({ title, showBackButton = true, backUrl, actions }: AdminHeaderProps) {
  const router = useRouter()

  const handleBack = () => {
    if (backUrl) {
      router.push(backUrl)
    } else {
      router.back()
    }
  }

  return (
    <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-4">
          <div className="flex items-center gap-4">
            {showBackButton && (
              <button
                onClick={handleBack}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
                title="Go back"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                <span className="font-medium">Back</span>
              </button>
            )}
            
            <div className="flex items-center gap-3">
              <Link href="/admin" className="text-techBlue hover:text-techBlue/80 font-medium">
                Admin
              </Link>
              <span className="text-gray-400">/</span>
              <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
            </div>
          </div>

          {actions && (
            <div className="flex items-center gap-3">
              {actions}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
