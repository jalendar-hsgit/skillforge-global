import { useEffect } from 'react'

export default function Logout() {
  useEffect(() => {
    (async () => {
      await fetch('/api/session/logout')
      window.location.href = '/'
    })()
  }, [])
  return null
}
