import { useEffect } from 'react'
import { useRouter } from 'next/router'
import Layout from '@/components/Layout'
import { useMe } from '@/lib/useMe'

export default function Dashboard() {
  const { me, loading } = useMe()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !me) router.replace('/login')
  }, [loading, me, router])

  if (loading) return <div className="px-6 pt-24">Loading...</div>

  return (
    <Layout>
      <main className="mx-auto max-w-3xl px-6 pt-24 pb-20">
        <h1 className="text-3xl font-semibold">Dashboard</h1>
        <p className="text-gray-500 mt-2">Welcome, {me?.email}</p>
      </main>
    </Layout>
  )
}
