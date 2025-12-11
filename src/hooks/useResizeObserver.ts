import { useEffect, useState, RefObject } from 'react'

export default function useResizeObserver(refOrElement: RefObject<HTMLElement> | HTMLElement | null) {
  const [width, setWidth] = useState<number | null>(null)

  useEffect(() => {
    let el: HTMLElement | null = null
    if (!refOrElement) return
    if ('current' in (refOrElement as any)) el = (refOrElement as any).current
    else el = refOrElement as HTMLElement

    if (!el) return

    const ro = new ResizeObserver(entries => {
      for (const entry of entries) {
        const w = entry.contentRect.width
        setWidth(w)
      }
    })

    ro.observe(el)

    // initial
    setWidth(el.getBoundingClientRect().width)

    return () => ro.disconnect()
  }, [refOrElement])

  return width
}
