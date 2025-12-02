import Head from 'next/head'
import Layout from '@/components/Layout'
import AdminHeader from '@/components/AdminHeader'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth'

type User = {
  id: number
  email: string
  role: 'USER' | 'MENTOR' | 'ADMIN' | 'SUPERADMIN'
  created_at: string
}

export default function AdminUsers({ me }: AdminSSRProps) {
  const router = useRouter()
  const [users, setUsers] = useState<User[]>([])
  const [filter, setFilter] = useState<'all' | 'user' | 'mentor' | 'admin' | 'superadmin'>('all')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadUsers()
  }, [filter])

  async function loadUsers() {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (filter !== 'all') params.append('role', filter)
      if (search) params.append('search', search)

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/users?${params}`,
        { credentials: 'include' }
      )

      if (res.status === 403) {
        setError('Access denied. Admin privileges required.')
        return
      }

      if (res.status === 401) {
        router.push('/login?redirect=/admin/users')
        return
      }

      if (!res.ok) throw new Error('Failed to fetch users')

      const data = await res.json()
      setUsers(data)
    } catch (err) {
      console.error(err)
      setError('Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  async function updateUserRole(userId: number, newRole: string) {
    if (!confirm(`Are you sure you want to change this user's role to ${newRole}?`)) {
      return
    }

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/users/${userId}/role`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ role: newRole })
        }
      )

      if (!res.ok) {
        const err = await res.text()
        alert(`Failed to update role: ${err}`)
        return
      }

      alert('Role updated successfully')
      loadUsers()
    } catch (err) {
      console.error(err)
      alert('An error occurred')
    }
  }

  function exportToCSV() {
    const headers = ['ID', 'Email', 'Role', 'Created At']
    const rows = users.map(u => [
      u.id,
      u.email,
      u.role,
      new Date(u.created_at).toLocaleString()
    ])

    const csv = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `users_export_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  async function deleteUser(userId: number, email: string) {
    if (!confirm(`⚠️ PERMANENT ACTION ⚠️\n\nAre you sure you want to delete user ${email}?\n\nThis cannot be undone.`)) {
      return
    }

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/users/${userId}`,
        {
          method: 'DELETE',
          credentials: 'include'
        }
      )

      if (!res.ok) {
        const err = await res.text()
        alert(`Failed to delete user: ${err}`)
        return
      }

      alert('User deleted successfully')
      loadUsers()
    } catch (err) {
      console.error(err)
      alert('Error deleting user')
    }
  }

  const roleColors = {
    user: 'bg-gray-500/20 text-gray-300 border-gray-500/30',
    mentor: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    admin: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    superadmin: 'bg-red-500/20 text-red-300 border-red-500/30'
  }

  return (
    <Layout>
      <Head><title>{`Admin – User Management`}</title></Head>
      <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
        <h1 className="text-3xl font-semibold mb-2">User Management</h1>
        <p className="text-techGray mb-2">Manage user accounts, roles, and permissions</p>
        <div className="flex items-center gap-3 mb-6">
          <span className="text-sm text-gray-400">Signed in as:</span>
          <span className="text-sm font-medium text-white">{me.email}</span>
          <span className={`text-xs px-2 py-1 rounded-full ${me.role === 'SUPERADMIN' ? 'bg-red-500/20 text-red-300' : 'bg-purple-500/20 text-purple-300'}`}>
            {me.role}
          </span>
        </div>
        
        {me.role === 'SUPERADMIN' && (
          <div className="mb-6 rounded-xl border border-blue-500/30 p-4 bg-blue-500/10">
            <div className="flex items-start gap-3">
              <span className="text-2xl">ℹ️</span>
              <div className="text-sm text-blue-200">
                <strong>Superadmin Powers:</strong> You can promote users to Admin or Superadmin roles.
                All actions are logged in the audit trail. Regular signups create "user" role accounts only.
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/30 p-4 bg-red-500/10 text-red-300">
            {error}
          </div>
        )}

        <div className="mb-6 flex flex-col md:flex-row gap-4">
          <input
            className="h-12 rounded-md bg-white/5 border border-white/10 px-4 flex-1"
            placeholder="Search by email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && loadUsers()}
          />
          <select
            className="h-12 rounded-md bg-white/5 border border-white/10 px-4"
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
          >
            <option value="all">All Roles</option>
            <option value="user">Users</option>
            <option value="mentor">Mentors</option>
            <option value="admin">Admins</option>
            <option value="superadmin">Superadmins</option>
          </select>
          <button
            onClick={loadUsers}
            className="h-12 rounded-md bg-forgePurple hover:bg-forgePurple/80 px-6 font-medium transition-colors"
          >
            Search
          </button>
          <button
            onClick={exportToCSV}
            disabled={users.length === 0}
            className="h-12 rounded-md bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed px-6 font-medium transition-colors"
            title="Export users to CSV"
          >
            📥 Export CSV
          </button>
        </div>

        {loading ? (
          <div className="text-techGray">Loading users...</div>
        ) : users.length === 0 ? (
          <div className="rounded-xl border border-white/10 p-8 bg-white/[0.06] text-center text-techGray">
            No users found
          </div>
        ) : (
          <div className="space-y-3">
            {users.map((user) => (
              <div
                key={user.id}
                className="rounded-xl border border-white/10 p-6 bg-white/[0.06] hover:bg-white/[0.08] transition"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold">{user.email}</h3>
                      <span className={`text-xs px-3 py-1 rounded-full border ${roleColors[user.role]}`}>
                        {user.role}
                      </span>
                    </div>
                    <div className="text-sm text-techGray">
                      User ID: {user.id} · Joined {new Date(user.created_at).toLocaleDateString()}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <select
                      className="h-10 rounded-md bg-white/5 border border-white/10 px-3 text-sm"
                      defaultValue={user.role}
                      onChange={(e) => updateUserRole(user.id, e.target.value)}
                    >
                      <option value="user">User</option>
                      <option value="mentor">Mentor</option>
                      <option value="admin">Admin</option>
                      <option value="superadmin">Superadmin</option>
                    </select>
                    <button
                      onClick={() => deleteUser(user.id, user.email)}
                      className="h-10 px-4 rounded-md bg-red-600 hover:bg-red-700 text-sm font-semibold transition"
                      title="Delete user (permanent)"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-6 text-sm text-techGray">
          Showing {users.length} user{users.length !== 1 ? 's' : ''}
        </div>
      </section>
    </Layout>
  )
}

export const getServerSideProps = requireAdminSSR
