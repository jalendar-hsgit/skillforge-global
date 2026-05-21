// src/pages/profile/edit.tsx
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { ArrowLeft, Lightbulb } from 'lucide-react'
import Layout from '@/components/Layout'
import ProfileForm from '@/components/ProfileForm'
import { useProtectedPage } from '@/lib/useProtectedPage'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ROUTES } from '@/lib/routes'

export default function EditProfilePage() {
  const router = useRouter()
  const { user, loading: authLoading } = useProtectedPage()
  const [loading, setLoading] = useState(true)

  // Security: Redirect if not authenticated
  useEffect(() => {
    if (!authLoading) {
      if (!user) {
        router.push('/login?redirect=' + encodeURIComponent(router.asPath))
      } else {
        setLoading(false)
      }
    }
  }, [user, authLoading, router])

  // Security: Show loading while checking auth
  if (authLoading || loading) {
    return <LoadingSpinner message="Loading your profile..." />
  }

  // Security: Don't render if not authenticated
  if (!user) {
    return null
  }

  return (
    <Layout maxWidth="4xl">
      <div className="py-12 flex flex-col items-center w-full">
        {/* Back Button */}
        <div className="w-full max-w-2xl flex justify-start mb-8">
          <Link href={ROUTES.profile}>
            <button className="flex items-center gap-2 text-white/70 hover:text-white font-medium transition-colors">
              <ArrowLeft className="w-5 h-5" />
              Back to Profile
            </button>
          </Link>
        </div>

        {/* Page Header */}
        <div className="mb-12 text-center">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent mb-2">Edit Your Profile</h1>
          <p className="text-white/60">Update your information and profile settings</p>
        </div>

        {/* Form - Centered */}
        <div className="w-full max-w-2xl">
          <ProfileForm />
        </div>

        {/* Help Section - Centered */}
        <div className="mt-12 w-full max-w-2xl bg-gradient-to-br from-white/10 to-white/5 border border-white/10 rounded-lg p-6 backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-4">
            <Lightbulb className="w-5 h-5 text-yellow-400" />
            <h3 className="font-bold text-white">Tips for Your Profile</h3>
          </div>
          <ul className="space-y-2 text-white/70 text-sm">
            <li>✓ Add a clear, professional name for mentors to recognize you</li>
            <li>✓ Write a compelling bio - it helps mentees understand your expertise</li>
            <li>✓ Keep your contact information up to date</li>
            <li>✓ Add relevant skills to help with course recommendations</li>
            <li>✓ Use a professional photo as your avatar</li>
          </ul>
        </div>
      </div>
    </Layout>
  )
}
