export async function exportResumePDFFromPreview(resumeId: number, filename = 'resume.pdf') {
  // Open preview in a hidden iframe, capture it, then close
  return new Promise<void>((resolve, reject) => {
    const iframe = document.createElement('iframe')
    iframe.style.position = 'absolute'
    iframe.style.left = '-9999px'
    iframe.style.width = '210mm'
    iframe.style.height = '297mm'
    document.body.appendChild(iframe)

    iframe.onload = async () => {
      try {
        await new Promise(r => setTimeout(r, 1500)) // Wait for content to render
        const doc = iframe.contentDocument || iframe.contentWindow?.document
        if (!doc) throw new Error('Cannot access iframe document')

        const content = doc.getElementById('resume-content')
        if (!content) throw new Error('Resume content not found')

        const html2canvas = (await import('html2canvas')).default
        const { jsPDF } = await import('jspdf')

        const canvas = await html2canvas(content, {
          scale: 2,
          useCORS: true,
          backgroundColor: '#ffffff',
          windowWidth: 794, // A4 width in pixels at 96 DPI
          windowHeight: 1123, // A4 height
        })

        const imgData = canvas.toDataURL('image/png')
        const pdf = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })
        const imgWidth = 210
        const imgHeight = (canvas.height * imgWidth) / canvas.width

        pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight)
        pdf.save(filename)

        document.body.removeChild(iframe)
        resolve()
      } catch (e) {
        document.body.removeChild(iframe)
        reject(e)
      }
    }

    iframe.onerror = () => {
      document.body.removeChild(iframe)
      reject(new Error('Failed to load preview'))
    }

    iframe.src = `/resumes/${resumeId}/preview`
  })
}

// Keep the original function for backward compatibility
export async function exportResumePDF(el: HTMLElement, filename = 'resume.pdf') {
  if (!el) throw new Error('No element to export')

  const html2canvas = (await import('html2canvas')).default
  const { jsPDF } = await import('jspdf')

  // Render the element to canvas with higher scale for better quality
  const canvas = await html2canvas(el, { scale: 2, useCORS: true, backgroundColor: '#ffffff' })
  const imgData = canvas.toDataURL('image/png')

  // Use points (pt) for easier scaling
  const pdf = new jsPDF({ orientation: 'p', unit: 'pt', format: 'a4' })
  const pageWidth = pdf.internal.pageSize.getWidth()
  const pageHeight = pdf.internal.pageSize.getHeight()

  // Calculate dimensions to fit within a single page while preserving aspect ratio
  const ratio = Math.min(pageWidth / canvas.width, pageHeight / canvas.height)
  const imgWidth = canvas.width * ratio
  const imgHeight = canvas.height * ratio
  const marginTop = 24

  pdf.addImage(imgData, 'PNG', (pageWidth - imgWidth) / 2, marginTop, imgWidth, imgHeight)
  pdf.save(filename)
}
