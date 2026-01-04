// src/pages/profile/edit.tsx
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import ProfileForm from '@/components/ProfileForm'
import { useProtectedPage } from '@/lib/useProtectedPage'

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
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Security: Don't render if not authenticated
  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <Link href="/profile">
          <button className="flex items-center gap-2 text-blue-600 hover:text-blue-800 font-medium mb-6 transition-colors">
            <ArrowLeft className="w-5 h-5" />
            Back to Profile
          </button>
        </Link>

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Edit Your Profile</h1>
          <p className="text-gray-600 mt-2">Update your information and profile settings</p>
        </div>

        {/* Form */}
        <ProfileForm />

        {/* Help Section */}
        <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6 max-w-2xl">
          <h3 className="font-bold text-blue-900 mb-3">Tips for Your Profile</h3>
          <ul className="space-y-2 text-blue-800 text-sm">
            <li>✓ Add a clear, professional name for mentors to recognize you</li>
            <li>✓ Write a compelling bio - it helps mentees understand your expertise</li>
            <li>✓ Keep your contact information up to date</li>
            <li>✓ Add relevant skills to help with course recommendations</li>
            <li>✓ Use a professional photo as your avatar</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
