import { useEffect, useState } from 'react'
export type Me = { id:number; email:string } | null

export function useMe() {
  const [me, setMe] = useState<Me>(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    let mounted = true
    fetch('/api/session/me').then(async r=>{
      if (!mounted) return
      if (!r.ok) { setMe(null); setLoading(false); return }
      const d = await r.json()
      setMe(d); setLoading(false)
    }).catch(()=>{ setMe(null); setLoading(false) })
    return () => { mounted = false }
  }, [])
  return { me, loading }
}
