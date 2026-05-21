import { useEffect, useState } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import ResumeImportModal from '@/components/resume/ResumeImportModal'

export default function ImportResumePage() {
  const router = useRouter()
  const [open, setOpen] = useState(true)
  const [checking, setChecking] = useState(true)

  // Ensure user is authenticated; if not, redirect to login
  useEffect(() => {
    const check = async () => {
      try {
        const r = await fetch('/api/session/me', { credentials: 'include' })
        if (r.status === 401) {
          router.replace(`/login?redirect=/resumes/import`)
          return
        }
      } catch {}
      setChecking(false)
    }
    check()
  }, [router])

  const handleSuccess = (resumeId: number) => {
    router.replace(`/resumes/${resumeId}/edit`)
  }

  if (checking) {
    return (
      <div className="min-h-screen grid place-items-center bg-gradient-to-br from-deepTech via-deepTech/95 to-deepTech/90">
        <div className="text-white/80">Checking authentication…</div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>Import Resume</title>
      </Head>
      <div className="min-h-screen grid place-items-center bg-gradient-to-br from-deepTech via-deepTech/95 to-deepTech/90">
        <div className="text-center text-white/80 mb-6">
          <h1 className="text-3xl font-bold">Import your resume</h1>
          <p className="text-white/60 mt-2">Upload a PDF or DOCX, well parse and create a new editable resume.</p>
        </div>
        <ResumeImportModal
          isOpen={open}
          onClose={() => setOpen(false)}
          onImportSuccess={handleSuccess}
        />
      </div>
    </>
  )
}
