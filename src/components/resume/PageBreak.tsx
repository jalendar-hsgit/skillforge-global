import React from 'react';

interface PageBreakProps {
  pageNumber?: number;
  showInPreview?: boolean;
}

/**
 * PageBreak component - indicates where a new page starts
 * Visible in editor preview, hidden in PDF export
 */
export default function PageBreak({ pageNumber, showInPreview = true }: PageBreakProps) {
  if (!showInPreview) return null;
  
  return (
    <div className="page-break print:hidden my-8 relative">
      <div className="h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent" />
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white px-3">
        <span className="text-xs text-gray-400 font-medium">
          {pageNumber ? `Page ${pageNumber}` : 'Page Break'}
        </span>
      </div>
    </div>
  );
}

/**
 * Hook to calculate where page breaks should occur
 * Based on A4 page height (297mm ≈ 1122px at 96dpi)
 */
export function usePageBreaks(contentRef: React.RefObject<HTMLElement>) {
  const [pageBreaks, setPageBreaks] = React.useState<number[]>([]);
  
  React.useEffect(() => {
    if (!contentRef.current) return;
    
    const A4_HEIGHT_PX = 1122; // 297mm at 96dpi
    const MARGIN_PX = 60; // Top + bottom margins
    const USABLE_HEIGHT = A4_HEIGHT_PX - MARGIN_PX;
    
    const sections = Array.from(contentRef.current.children) as HTMLElement[];
    const breaks: number[] = [];
    let currentHeight = 0;
    let currentPage = 1;
    
    sections.forEach((section, index) => {
      const sectionHeight = section.offsetHeight;
      
      // If adding this section exceeds page height, insert page break
      if (currentHeight + sectionHeight > USABLE_HEIGHT && currentHeight > 0) {
        breaks.push(index);
        currentPage++;
        currentHeight = sectionHeight;
      } else {
        currentHeight += sectionHeight;
      }
    });
    
    setPageBreaks(breaks);
  }, [contentRef]);
  
  return pageBreaks;
}
