import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { requireAdminSSR, type AdminSSRProps } from '@/lib/adminAuth'

type AuditLog = {
  id: number
  admin_user_id: number | null
  admin_email: string | null
  action: string
  resource_type: string
  resource_id: number | null
  details: string | null
  ip_address: string | null
  created_at: string
}

export const getServerSideProps = requireAdminSSR

export default function AdminLogs({ me }: AdminSSRProps) {
  const router = useRouter()
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [filterAction, setFilterAction] = useState('')
  const [filterResource, setFilterResource] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [total, setTotal] = useState(0)

  useEffect(() => {
    loadLogs()
  }, [filterAction, filterResource])

  async function loadLogs() {
    setLoading(true)
    try {
      const params = new URLSearchParams({ limit: '50' })
      if (filterAction) params.append('action', filterAction)
      if (filterResource) params.append('resource_type', filterResource)

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/logs?${params}`,
        { credentials: 'include' }
      )

      if (res.status === 403) {
        setError('Access denied. Admin privileges required.')
        return
      }

      if (res.status === 401) {
        router.push('/login?redirect=/admin/logs')
        return
      }

      if (!res.ok) throw new Error('Failed to fetch logs')

      const data = await res.json()
      setLogs(data.logs || [])
      setTotal(data.total || 0)
    } catch (err) {
      console.error(err)
      setError('Failed to load audit logs')
    } finally {
      setLoading(false)
    }
  }

  const actionColors: Record<string, string> = {
    update_user_role: 'bg-purple-500/20 text-purple-300',
    delete_user: 'bg-red-500/20 text-red-300',
    update_mentor_status: 'bg-blue-500/20 text-blue-300',
    update_session_status: 'bg-yellow-500/20 text-yellow-300',
    update_platform_settings: 'bg-green-500/20 text-green-300'
  }

  return (
    <Layout>
      <Head><title>{`Admin – Audit Logs`}</title></Head>
      <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
        <h1 className="text-3xl font-semibold mb-2">Audit Logs</h1>
        <p className="text-techGray mb-6">Track all administrative actions and changes</p>
        <div className="mb-8 text-sm text-techGray">
          Signed in as <span className="font-medium text-white">{me.email}</span> ({me.role})
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/30 p-4 bg-red-500/10 text-red-300">
            {error}
          </div>
        )}

        <div className="mb-6 flex flex-col md:flex-row gap-4">
          <select
            className="h-12 rounded-md bg-white/5 border border-white/10 px-4"
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
          >
            <option value="">All Actions</option>
            <option value="update_user_role">Update User Role</option>
            <option value="delete_user">Delete User</option>
            <option value="update_mentor_status">Update Mentor Status</option>
            <option value="update_session_status">Update Session Status</option>
            <option value="update_platform_settings">Update Settings</option>
          </select>
          <select
            className="h-12 rounded-md bg-white/5 border border-white/10 px-4"
            value={filterResource}
            onChange={(e) => setFilterResource(e.target.value)}
          >
            <option value="">All Resources</option>
            <option value="user">User</option>
            <option value="mentor">Mentor</option>
            <option value="session">Session</option>
            <option value="settings">Settings</option>
          </select>
          <button
            onClick={loadLogs}
            className="h-12 px-6 rounded-md bg-white/5 border border-white/10 hover:bg-white/10 transition"
          >
            🔄 Refresh
          </button>
        </div>

        {loading ? (
          <div className="text-techGray">Loading audit logs...</div>
        ) : logs.length === 0 ? (
          <div className="rounded-xl border border-white/10 p-8 bg-white/[0.06] text-center text-techGray">
            No audit logs found
          </div>
        ) : (
          <div className="space-y-3">
            {logs.map((log) => (
              <div
                key={log.id}
                className="rounded-xl border border-white/10 p-6 bg-white/[0.06] hover:bg-white/[0.08] transition"
              >
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                      <span className={`text-xs px-3 py-1 rounded-full ${actionColors[log.action] || 'bg-gray-500/20 text-gray-300'}`}>
                        {log.action.replace(/_/g, ' ')}
                      </span>
                      <span className="text-xs px-3 py-1 rounded-full bg-white/5 border border-white/10">
                        {log.resource_type}
                        {log.resource_id && ` #${log.resource_id}`}
                      </span>
                    </div>
                    <div className="text-sm mb-2">
                      <span className="text-neuralBlue font-semibold">
                        {log.admin_email || `Admin #${log.admin_user_id}` || 'Unknown'}
                      </span>
                      {log.details && (
                        <>
                          {' · '}
                          <span className="text-techGray">{log.details}</span>
                        </>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-4 text-xs text-techGray">
                      <span>🕒 {new Date(log.created_at).toLocaleString()}</span>
                      {log.ip_address && <span>🌐 {log.ip_address}</span>}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-6 text-sm text-techGray">
          Showing {logs.length} of {total} total log{total !== 1 ? 's' : ''}
        </div>
      </section>
    </Layout>
  )
}
