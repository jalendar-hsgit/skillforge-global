import { useEffect, useState, useRef } from 'react'
import useResizeObserver from '@/hooks/useResizeObserver'
import useAutoScale from '@/hooks/useAutoScale'

interface MultiPagePreviewProps {
  resume: any
  scale?: number
  className?: string
}

export default function MultiPagePreview({ resume, scale = 1, className = '' }: MultiPagePreviewProps) {
  const [pages, setPages] = useState<HTMLElement[]>([])
  const containerRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)
  const containerWidth = useResizeObserver(containerRef)
  const autoScale = useAutoScale(containerWidth, { targetWidth: 794, min: 0.45, max: 1 })

  useEffect(() => {
    if (!contentRef.current) return

    // Calculate page breaks based on A4 dimensions (210mm x 297mm at 96dpi)
    const A4_HEIGHT_PX = 1122 // 297mm at 96dpi
    const MARGIN_PX = 60
    const MAX_CONTENT_HEIGHT = A4_HEIGHT_PX - (MARGIN_PX * 2)

    const splitIntoPages = () => {
      const content = contentRef.current
      if (!content) return []

      const sections = Array.from(content.children) as HTMLElement[]
      const pageElements: HTMLElement[] = []
      let currentPage = document.createElement('div')
      currentPage.className = 'resume-page'
      let currentHeight = 0

      sections.forEach((section) => {
        const sectionHeight = section.offsetHeight
        
        // If section fits in current page
        if (currentHeight + sectionHeight <= MAX_CONTENT_HEIGHT) {
          currentPage.appendChild(section.cloneNode(true))
          currentHeight += sectionHeight
        } else {
          // Start new page
          if (currentPage.children.length > 0) {
            pageElements.push(currentPage)
          }
          currentPage = document.createElement('div')
          currentPage.className = 'resume-page'
          currentPage.appendChild(section.cloneNode(true))
          currentHeight = sectionHeight
        }
      })

      if (currentPage.children.length > 0) {
        pageElements.push(currentPage)
      }

      return pageElements
    }

    setPages(splitIntoPages())
  }, [resume])

  return (
    <div ref={containerRef} className={`${className} space-y-6`}>
      <div ref={contentRef} className="hidden">
        {/* Original content for measurement */}
        <ResumeContent resume={resume} />
      </div>

      {/* Rendered pages */}
      {pages.map((page, index) => (
        <div
          key={index}
          className="bg-white shadow-2xl mx-auto relative"
          style={{
            width: `${794 * scale}px`, // A4 width at 96dpi
            minHeight: `${1122 * scale}px`, // A4 height
            padding: `${60 * scale}px`,
            transform: `scale(${Math.min(scale, autoScale)})`,
            transformOrigin: 'top center',
          }}
        >
          {/* Page number */}
          <div className="absolute bottom-4 right-4 text-xs text-gray-400">
            Page {index + 1} of {pages.length}
          </div>
          
          <div dangerouslySetInnerHTML={{ __html: page.innerHTML }} />
        </div>
      ))}

      {pages.length === 0 && (
        <div className="bg-white shadow-2xl mx-auto p-16 text-center" style={{ width: '794px', minHeight: '1122px' }}>
          <ResumeContent resume={resume} />
        </div>
      )}
    </div>
  )
}

function ResumeContent({ resume }: { resume: any }) {
  return (
    <>
      {resume.full_name && (
        <div className="mb-6">
          <h1 className="text-3xl font-bold">{resume.full_name}</h1>
          {resume.email && <p className="text-sm text-gray-600">{resume.email}</p>}
        </div>
      )}
      
      {resume.professional_summary && (
        <section className="mb-6">
          <h2 className="text-xl font-bold mb-2 border-b pb-1">Professional Summary</h2>
          <p className="text-sm">{resume.professional_summary}</p>
        </section>
      )}

      {resume.work_experiences?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold mb-2 border-b pb-1">Work Experience</h2>
          {resume.work_experiences.map((exp: any, i: number) => (
            <div key={i} className="mb-4">
              <h3 className="font-semibold">{exp.title}</h3>
              <p className="text-sm text-gray-600">{exp.company}</p>
            </div>
          ))}
        </section>
      )}

      {resume.education?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold mb-2 border-b pb-1">Education</h2>
          {resume.education.map((edu: any, i: number) => (
            <div key={i} className="mb-3">
              <h3 className="font-semibold">{edu.degree}</h3>
              <p className="text-sm text-gray-600">{edu.institution}</p>
            </div>
          ))}
        </section>
      )}

      {resume.skills?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold mb-2 border-b pb-1">Skills</h2>
          <div className="flex flex-wrap gap-2">
            {resume.skills.map((skill: any, i: number) => (
              <span key={i} className="px-3 py-1 bg-gray-100 rounded-full text-sm">
                {skill.name}
              </span>
            ))}
          </div>
        </section>
      )}
    </>
  )
}
