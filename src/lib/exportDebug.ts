/**
 * Resume Export Debug Helper
 * Quick test to verify export functionality is working
 */

export async function testExportModal() {
  console.log('[Export Test] Opening export modal...')
  
  // Test 1: Verify modal can be triggered
  const exportButton = document.querySelector('[data-testid="btn-export"]')
  if (exportButton) {
    console.log('[Export Test] ✅ Export button found')
    (exportButton as HTMLElement).click()
  } else {
    console.error('[Export Test] ❌ Export button not found')
  }
}

export async function testTemplatePreview(resumeId: number) {
  console.log(`[Template Test] Testing preview for resume ${resumeId}...`)
  
  try {
    const response = await fetch(`/resumes/${resumeId}/preview`)
    if (response.ok) {
      const html = await response.text()
      console.log('[Template Test] ✅ Preview endpoint working')
      console.log('[Template Test] HTML length:', html.length)
      console.log('[Template Test] Contains resume-content:', html.includes('resume-content'))
      return html
    } else {
      console.error(`[Template Test] ❌ Preview failed with status ${response.status}`)
    }
  } catch (error) {
    console.error('[Template Test] Error:', error)
  }
}

export async function testPDFExport(resumeId: number) {
  console.log(`[PDF Test] Testing PDF export for resume ${resumeId}...`)
  
  try {
    // Load the export function
    const { exportResumePDFFromPreview } = await import('./pdf')
    
    // Try export with default settings
    await exportResumePDFFromPreview(
      resumeId,
      `resume-${resumeId}.pdf`,
      { dpi: 300, marginMM: 10 }
    )
    
    console.log('[PDF Test] ✅ PDF export completed')
  } catch (error) {
    console.error('[PDF Test] ❌ PDF export failed:', error)
  }
}

// Run tests when module loads
if (typeof window !== 'undefined') {
  (window as any).testExportModal = testExportModal
  (window as any).testTemplatePreview = testTemplatePreview
  (window as any).testPDFExport = testPDFExport
  
  console.log('[Export Debug] Test functions available:')
  console.log('  - window.testExportModal()')
  console.log('  - window.testTemplatePreview(resumeId)')
  console.log('  - window.testPDFExport(resumeId)')
}
