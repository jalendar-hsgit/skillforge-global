import { useEffect, useState } from 'react'

interface Options {
  targetWidth?: number // native width of content in px
  min?: number
  max?: number
}

export default function useAutoScale(containerWidth: number | null, options: Options = {}) {
  const { targetWidth = 794, min = 0.4, max = 1 } = options
  const [scale, setScale] = useState<number>(1)

  useEffect(() => {
    if (!containerWidth) return
    const computed = Math.min(max, Math.max(min, containerWidth / targetWidth))
    setScale(Number(computed.toFixed(3)))
  }, [containerWidth, targetWidth, min, max])

  return scale
}
