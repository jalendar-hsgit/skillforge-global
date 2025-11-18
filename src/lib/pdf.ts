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
        // Inject Google Fonts and print styles for fidelity
        const doc = iframe.contentDocument || iframe.contentWindow?.document;
        if (!doc) throw new Error('Cannot access iframe document');

        // Inject Google Fonts
        const fontLink = doc.createElement('link');
        fontLink.rel = 'stylesheet';
        fontLink.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap';
        doc.head.appendChild(fontLink);

        // Inject print styles
        const style = doc.createElement('style');
        style.innerHTML = `@media print { * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; } html, body { margin: 0 !important; padding: 0 !important; background: white !important; width: 210mm; height: 297mm; } #resume-content { width: 210mm !important; max-width: 210mm !important; min-height: auto !important; margin: 0 !important; padding: 0 !important; box-shadow: none !important; border-radius: 0 !important; background: white !important; } #resume-content > div { page-break-after: auto; } #resume-content section { page-break-inside: avoid; break-inside: avoid; } #resume-content h2 { page-break-after: avoid; break-after: avoid; } #resume-content ul, #resume-content ol { page-break-inside: avoid; break-inside: avoid; } #resume-content a { text-decoration: underline; color: #2563eb !important; } .print\\:hidden { display: none !important; } } #resume-content { font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; text-rendering: optimizeLegibility; } #resume-content .font-serif { font-family: "Source Serif 4", ui-serif, Georgia, Cambria, "Times New Roman", Times, serif; } #resume-content .bg-gradient-to-r, #resume-content .bg-gradient-to-br, #resume-content header, #resume-content [style*="printColorAdjust"] { -webkit-print-color-adjust: exact; print-color-adjust: exact; color-adjust: exact; } #resume-content h2 { filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.05)); }`;
        doc.head.appendChild(style);

        // Wait for fonts/styles to load
        await new Promise(r => setTimeout(r, 1200));

        // Wait until resume-content is present and not loading
        let content = doc.getElementById('resume-content');
        let tries = 0;
        while ((!content || content.innerText.trim().length === 0) && tries < 10) {
          await new Promise(r => setTimeout(r, 300));
          content = doc.getElementById('resume-content');
          tries++;
        }
        if (!content) throw new Error('Resume content not found');

        const html2canvas = (await import('html2canvas')).default;
        const { jsPDF } = await import('jspdf');

        const canvas = await html2canvas(content, {
          scale: 2,
          useCORS: true,
          backgroundColor: '#ffffff',
          windowWidth: 794, // A4 width in pixels at 96 DPI
          windowHeight: 1123, // A4 height
        });

        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' });
        const imgWidth = 210;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;

        pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
        pdf.save(filename);

        document.body.removeChild(iframe);
        resolve();
      } catch (e) {
        document.body.removeChild(iframe);
        reject(e);
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
