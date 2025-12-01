export async function exportResumePDFFromPreview(
  resumeId: number, 
  filename = 'resume.pdf',
  options: { dpi?: number; marginMM?: number } = {}
) {
  const dpi = options.dpi || 300
  const marginMM = options.marginMM || 10
  const scale = dpi / 96 // Convert DPI to canvas scale (96 is base DPI)
  
  // Open preview in a hidden iframe, capture it, then close
  return new Promise<void>((resolve, reject) => {
    const iframe = document.createElement('iframe')
    iframe.style.position = 'absolute'
    iframe.style.left = '-9999px'
    iframe.style.width = '1123px'  // A4 width in pixels (210mm at 96 DPI)
    iframe.style.height = '1587px' // A4 height in pixels (297mm at 96 DPI)
    document.body.appendChild(iframe)

    iframe.onload = async () => {
      try {
        // Inject Google Fonts and print styles for fidelity
        const doc = iframe.contentDocument || iframe.contentWindow?.document;
        if (!doc) throw new Error('Cannot access iframe document');

        // Inject Google Fonts
        const fontLink = doc.createElement('link');
        fontLink.rel = 'stylesheet';
        fontLink.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700;8..60,900&family=Poppins:wght@300;400;500;600;700;800&display=swap';
        doc.head.appendChild(fontLink);

        // Inject print styles
        const style = doc.createElement('style');
        style.innerHTML = `
          * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            color-adjust: exact !important;
          }
          html, body {
            margin: 0 !important;
            padding: 0 !important;
            width: 1123px;
            height: 1587px;
            overflow: hidden;
          }
          #resume-content {
            width: 1123px !important;
            max-width: 1123px !important;
            min-height: 1587px !important;
            margin: 0 !important;
            padding: 0 !important;
            font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
          }
          #resume-content .font-serif {
            font-family: "Source Serif 4", ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
          }
          /* Ensure all gradients, backgrounds, and colors are preserved */
          #resume-content *,
          #resume-content .bg-gradient-to-r,
          #resume-content .bg-gradient-to-br,
          #resume-content .bg-gradient-to-b,
          #resume-content .bg-blue-700,
          #resume-content .bg-blue-400,
          #resume-content header,
          #resume-content [class*="bg-"],
          #resume-content [class*="gradient"],
          #resume-content [style*="background"],
          #resume-content [style*="gradient"] {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            color-adjust: exact !important;
          }
          /* Preserve rounded corners, shadows, and borders */
          #resume-content .rounded-xl,
          #resume-content .rounded-full,
          #resume-content .shadow-lg,
          #resume-content [class*="border"] {
            border-radius: inherit !important;
            box-shadow: inherit !important;
            border-color: inherit !important;
          }
          /* Grid and flex layouts */
          #resume-content .grid {
            display: grid !important;
          }
          #resume-content .flex {
            display: flex !important;
          }
          /* Hide print-only hidden elements */
          .print\\:hidden {
            display: none !important;
          }
        `;
        doc.head.appendChild(style);

        // Wait for fonts and styles to load properly
        await new Promise(r => setTimeout(r, 2000));

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
          scale: scale, // Use DPI-based scale
          useCORS: true,
          backgroundColor: '#ffffff',
          windowWidth: 1123,
          windowHeight: 1587,
          logging: false,
          allowTaint: true,
          foreignObjectRendering: true,
        });

        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' });
        const pageWidthMM = 210;
        const pageHeightMM = 297;
        const usableWidth = pageWidthMM - (2 * marginMM);
        const usableHeight = pageHeightMM - (2 * marginMM);
        const imgWidth = usableWidth;
        const canvasHeightMM = (canvas.height * imgWidth) / canvas.width;
        
          // If content fits on one page, add directly
          if (canvasHeightMM <= usableHeight) {
            pdf.addImage(imgData, 'PNG', marginMM, marginMM, imgWidth, canvasHeightMM);
          } else {
            // Split across multiple pages
            const totalPages = Math.ceil(canvasHeightMM / usableHeight);
            console.log(`[PDF Export] Content height: ${canvasHeightMM}mm, generating ${totalPages} pages with ${marginMM}mm margins`);
          
            for (let page = 0; page < totalPages; page++) {
              if (page > 0) pdf.addPage();
            
              // Calculate the portion of the canvas for this page
              const sourceY = (page * usableHeight * canvas.width) / imgWidth;
              const sourceHeight = Math.min(
                (usableHeight * canvas.width) / imgWidth,
                canvas.height - sourceY
              );
            
              // Create a temporary canvas for this page slice
              const pageCanvas = document.createElement('canvas');
              pageCanvas.width = canvas.width;
              pageCanvas.height = sourceHeight;
              const ctx = pageCanvas.getContext('2d');
            
              if (ctx) {
                ctx.drawImage(
                  canvas,
                  0, sourceY,                  // source x, y
                  canvas.width, sourceHeight,  // source width, height
                  0, 0,                        // dest x, y
                  canvas.width, sourceHeight   // dest width, height
                );
              
                const pageImgData = pageCanvas.toDataURL('image/png');
                const pageImgHeight = (sourceHeight * imgWidth) / canvas.width;
                pdf.addImage(pageImgData, 'PNG', marginMM, marginMM, imgWidth, pageImgHeight);
              
                // Add page number
                pdf.setFontSize(8);
                pdf.setTextColor(150);
                pdf.text(`Page ${page + 1} of ${totalPages}`, pageWidthMM - marginMM - 20, pageHeightMM - marginMM - 5);
              }
            }
          }
        
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
