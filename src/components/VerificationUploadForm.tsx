// src/components/VerificationUploadForm.tsx
import { useState, useEffect } from 'react'
import { Upload, CheckCircle, AlertCircle, Clock } from 'lucide-react'

interface VerificationDocument {
  id: number
  document_type: string
  status: 'pending' | 'approved' | 'rejected'
  submitted_at: string
  reviewer_notes?: string
}

export default function VerificationUploadForm() {
  const [file, setFile] = useState<File | null>(null)
  const [docType, setDocType] = useState('government_id')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [verifications, setVerifications] = useState<VerificationDocument[]>([])
  const [loadingStatus, setLoadingStatus] = useState(false)

  // Fetch verification status on mount
  useEffect(() => {
    fetchStatus()
  }, [])

  const fetchStatus = async () => {
    setLoadingStatus(true)
    try {
      const token = localStorage.getItem('token')
      const res = await fetch('/api/v1x/mentor-verification/status', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setVerifications(data.verifications)
      }
    } catch (err) {
      console.error('Failed to fetch verification status:', err)
    } finally {
      setLoadingStatus(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a file')
      return
    }

    setLoading(true)
    setError('')
    setSuccess(false)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('doc_type', docType)

    try {
      const token = localStorage.getItem('token')
      const res = await fetch('/api/v1x/mentor-verification/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      })

      if (res.ok) {
        setSuccess(true)
        setFile(null)
        // Reset form
        document.getElementById('file-input')?.setAttribute('value', '')
        // Refresh status
        await fetchStatus()
      } else {
        const data = await res.json()
        setError(data.detail || 'Upload failed')
      }
    } catch (err) {
      setError('Error uploading file. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-50 border-green-200'
      case 'rejected':
        return 'bg-red-50 border-red-200'
      case 'pending':
        return 'bg-yellow-50 border-yellow-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'rejected':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-600" />
      default:
        return null
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-2xl font-bold mb-6">Mentor Verification</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Document Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Document Type
            </label>
            <select
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="government_id">Government ID (Passport, Driver's License)</option>
              <option value="degree">Degree/Diploma</option>
              <option value="certification">Professional Certification</option>
              <option value="credential">Other Credential</option>
            </select>
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Document
            </label>
            <div className="relative border-2 border-dashed border-gray-300 rounded-lg px-6 py-8 text-center hover:border-blue-400 transition-colors cursor-pointer">
              <input
                id="file-input"
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                accept=".pdf,.jpg,.jpeg,.png,.webp,.doc,.docx"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <Upload className="w-10 h-10 mx-auto text-gray-400 mb-2" />
              <p className="text-gray-600 font-medium">
                {file ? file.name : 'Click or drag to upload'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                PDF, JPEG, PNG, WebP, DOC, DOCX • Max 10MB
              </p>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
              Document uploaded successfully! It's now pending admin review.
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            {loading ? 'Uploading...' : 'Upload Document'}
          </button>
        </form>
      </div>

      {/* Verification Status */}
      {!loadingStatus && verifications.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-bold mb-4">Your Documents</h3>
          <div className="space-y-3">
            {verifications.map((doc) => (
              <div
                key={doc.id}
                className={`border rounded-lg p-4 flex items-start justify-between ${getStatusColor(doc.status)}`}
              >
                <div className="flex items-start gap-3 flex-1">
                  {getStatusIcon(doc.status)}
                  <div>
                    <p className="font-medium capitalize">
                      {doc.document_type.replace('_', ' ')}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      Submitted: {new Date(doc.submitted_at).toLocaleDateString()}
                    </p>
                    {doc.reviewer_notes && (
                      <p className="text-sm text-gray-600 mt-1 italic">
                        {doc.reviewer_notes}
                      </p>
                    )}
                  </div>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${
                    doc.status === 'approved'
                      ? 'bg-green-200 text-green-800'
                      : doc.status === 'rejected'
                      ? 'bg-red-200 text-red-800'
                      : 'bg-yellow-200 text-yellow-800'
                  }`}
                >
                  {doc.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
