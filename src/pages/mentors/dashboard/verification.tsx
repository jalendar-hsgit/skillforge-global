// src/pages/mentors/dashboard/verification.tsx
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import VerificationUploadForm from '@/components/VerificationUploadForm'

export default function MentorVerificationPage() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
    } else {
      setIsAuthenticated(true)
      setLoading(false)
    }
  }, [router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <Link href="/mentors/dashboard">
          <button className="flex items-center gap-2 text-blue-600 hover:text-blue-800 font-medium mb-6 transition-colors">
            <ArrowLeft className="w-5 h-5" />
            Back to Dashboard
          </button>
        </Link>

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Mentor Verification</h1>
          <p className="text-gray-600 mt-2">
            Verify your credentials to increase your credibility as a mentor
          </p>
        </div>

        {/* Info Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <h3 className="font-bold text-blue-900 mb-3">About Verification</h3>
          <ul className="space-y-2 text-blue-800 text-sm">
            <li>✓ Upload documents like government ID, degrees, or certifications</li>
            <li>✓ Our admin team reviews all submissions within 24-48 hours</li>
            <li>✓ Verified mentors appear higher in search results</li>
            <li>✓ Increase student trust and booking requests</li>
            <li>✓ Documents are stored securely and never shared publicly</li>
          </ul>
        </div>

        {/* Upload Form */}
        <VerificationUploadForm />

        {/* FAQ Section */}
        <div className="mt-12 space-y-4">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h2>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="font-bold text-gray-900 mb-2">What documents can I upload?</h4>
            <p className="text-gray-700 text-sm">
              You can upload government-issued ID, university degrees, professional certifications,
              or other credentials that verify your expertise.
            </p>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="font-bold text-gray-900 mb-2">How long does verification take?</h4>
            <p className="text-gray-700 text-sm">
              Most verifications are reviewed within 24-48 hours. You'll receive an email notification
              when your documents have been reviewed.
            </p>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="font-bold text-gray-900 mb-2">Are my documents kept private?</h4>
            <p className="text-gray-700 text-sm">
              Yes. Your documents are stored securely and only viewed by our admin team during verification.
              We never share your documents publicly or with students.
            </p>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="font-bold text-gray-900 mb-2">Can I update or replace documents?</h4>
            <p className="text-gray-700 text-sm">
              Yes. You can upload new documents at any time. Expired credentials will be marked as
              such and you'll be notified to update them.
            </p>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="font-bold text-gray-900 mb-2">What if my application is rejected?</h4>
            <p className="text-gray-700 text-sm">
              If your application is rejected, you'll receive an email with the reason and can
              resubmit with different documents or clarification.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
