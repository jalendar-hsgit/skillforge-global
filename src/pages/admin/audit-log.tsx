import Head from 'next/head'
import Layout from '@/components/Layout'
import AdminHeader from '@/components/AdminHeader'
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth'

export default function AuditLogPage({ me }: AdminSSRProps) {
  return (
    <>
      <Head>
        <title>Audit Log - Admin Panel</title>
      </Head>
      <Layout>
        <AdminHeader user={me} />
        <main className="mx-auto max-w-7xl px-4 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Audit Log</h1>
          <p className="text-gray-600 mb-6">Track all administrative actions and security events</p>
          <div className="bg-white rounded-lg shadow border p-6">
            <p className="text-gray-600">Audit log interface coming soon</p>
          </div>
        </main>
      </Layout>
    </>
  )
}

export const getServerSideProps = requireAdminSSR
