export async function exportResumePDFFromPreview(
  resumeId: number, 
  filename = 'resume.pdf',
  options: { dpi?: number; marginMM?: number } = {}
) {
  const dpi = options.dpi || 300
  const marginMM = options.marginMM || 10
  const scale = dpi / 96 // Convert DPI to canvas scale (96 is base DPI)
  
  console.log('[PDF Export] Starting export with DPI=' + dpi + ', margin=' + marginMM + 'mm, scale=' + scale)
  
  // Open preview in a hidden iframe, capture it, then close
  return new Promise<void>((resolve, reject) => {
    const iframe = document.createElement('iframe')
    iframe.style.position = 'absolute'
    iframe.style.left = '-9999px'
    iframe.style.width = '1123px'  // A4 width in pixels (210mm at 96 DPI)
    iframe.style.height = 'auto'  // Let height be auto to capture all content
    iframe.setAttribute('data-export', 'true')
    document.body.appendChild(iframe)

    iframe.onload = async () => {
      try {
        // Inject Google Fonts and print styles for fidelity
        const doc = iframe.contentDocument || iframe.contentWindow?.document;
        if (!doc) throw new Error('Cannot access iframe document');

        console.log('[PDF Export] Iframe loaded, injecting fonts and styles')

        // Inject Google Fonts with all typography weights
        const fontLink = doc.createElement('link');
        fontLink.rel = 'stylesheet';
        fontLink.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700;8..60,900&family=Poppins:wght@100;200;300;400;500;600;700;800;900&family=Roboto:wght@100;300;400;500;700;900&family=Georgia:wght@400;700&family=Garamond:wght@400;700&display=swap';
        doc.head.appendChild(fontLink);

        // Inject comprehensive print styles
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
            width: 1123px !important;
            background: white !important;
            overflow: visible !important;
          }
          #resume-content {
            width: 1123px !important;
            max-width: 1123px !important;
            margin: 0 !important;
            padding: 0 !important;
            background: white !important;
            font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
          }
          /* Preserve all font families */
          #resume-content .font-serif {
            font-family: "Source Serif 4", Georgia, Cambria, "Times New Roman", Times, serif !important;
          }
          #resume-content .font-garamond {
            font-family: "Garamond", Georgia, serif !important;
          }
          /* Ensure all colors and backgrounds are exact */
          #resume-content * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          /* Preserve gradients */
          #resume-content .bg-gradient-to-r,
          #resume-content .bg-gradient-to-br,
          #resume-content .bg-gradient-to-b,
          #resume-content [class*="bg-gradient"],
          #resume-content [style*="background"] {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          /* Preserve text colors */
          #resume-content {
            color: inherit !important;
          }
          #resume-content p, #resume-content span, #resume-content div, #resume-content h1, 
          #resume-content h2, #resume-content h3, #resume-content h4, #resume-content h5,
          #resume-content h6 {
            color: inherit !important;
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
          /* Page break styles */
          @page {
            margin: 0;
            padding: 0;
          }
          .page-break {
            page-break-after: always;
          }
        `;
        doc.head.appendChild(style);

        console.log('[PDF Export] Fonts and styles injected, waiting for content...')

        // Wait for fonts and styles to load properly
        await new Promise(r => setTimeout(r, 3000));

        // Wait until resume-content is present and fully loaded
        let content = doc.getElementById('resume-content');
        let tries = 0;
        while ((!content || !content.textContent || content.textContent.trim().length === 0) && tries < 15) {
          await new Promise(r => setTimeout(r, 400));
          content = doc.getElementById('resume-content');
          tries++;
        }
        if (!content) {
          console.error('[PDF Export] Resume content element not found. Document body HTML:', doc.body.innerHTML.substring(0, 500))
          throw new Error('Resume content not found in document')
        }

        console.log('[PDF Export] Content found after ' + tries + ' tries, content size: ' + (content?.textContent?.length || 0) + ' chars')

        const html2canvas = (await import('html2canvas')).default;
        const { jsPDF } = await import('jspdf');

        console.log('[PDF Export] Capturing canvas with scale=' + scale)
        const canvas = await html2canvas(content, {
          scale: scale, // Use DPI-based scale
          useCORS: true,
          backgroundColor: '#ffffff',
          windowWidth: 1123,
          allowTaint: true,
          foreignObjectRendering: true,
          logging: false,
        });

        console.log('[PDF Export] Canvas generated: ' + canvas.width + 'x' + canvas.height + ' pixels')
        const imgData = canvas.toDataURL('image/png', 1.0);
        const pdf = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' });
        const pageWidthMM = 210;
        const pageHeightMM = 297;
        const usableWidth = pageWidthMM - (2 * marginMM);
        const usableHeight = pageHeightMM - (2 * marginMM);
        const imgWidth = usableWidth;
        const canvasHeightMM = (canvas.height * imgWidth) / canvas.width;
        
        console.log('[PDF Export] Canvas height: ' + canvasHeightMM + 'mm, usable page height: ' + usableHeight + 'mm')
        
          // If content fits on one page, add directly
          if (canvasHeightMM <= usableHeight) {
            console.log('[PDF Export] Single page PDF, height fits')
            pdf.addImage(imgData, 'PNG', marginMM, marginMM, imgWidth, canvasHeightMM);
          } else {
            // Split across multiple pages
            const totalPages = Math.ceil(canvasHeightMM / usableHeight);
            console.log(`[PDF Export] Multi-page PDF: ${totalPages} pages, content height ${canvasHeightMM}mm`);
          
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
        console.log('[PDF Export] PDF saved successfully: ' + filename)

        document.body.removeChild(iframe);
        resolve();
      } catch (e) {
        console.error('[PDF Export] Error during export:', e)
        document.body.removeChild(iframe);
        reject(e);
      }
    }

    iframe.onerror = () => {
      console.error('[PDF Export] iframe failed to load from /resumes/' + resumeId + '/preview')
      document.body.removeChild(iframe)
      reject(new Error('Failed to load preview from /resumes/' + resumeId + '/preview'))
    }

    console.log('[PDF Export] Setting iframe src to /resumes/' + resumeId + '/preview')
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
