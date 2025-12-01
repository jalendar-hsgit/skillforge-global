import Head from 'next/head'
import Layout from '@/components/Layout'
import AdminHeader from '@/components/AdminHeader'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'

type Student = {
  student_id: number
  session_count: number
  total_amount: number
  last_session: string
}

export default function MentorStudents() {
  const router = useRouter()
  const [students, setStudents] = useState<Student[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStudents()
  }, [])

  async function loadStudents() {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/mentor-portal/dashboard/students`,
        { credentials: 'include' }
      )

      if (res.status === 401) {
        router.push('/login?redirect=/mentors/dashboard/students')
        return
      }

      if (res.ok) {
        const data = await res.json()
        setStudents(data.students || [])
        setTotal(data.total || 0)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getLastSessionText = (lastSession: string) => {
    const date = new Date(lastSession)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    return `${Math.floor(diffDays / 30)} months ago`
  }

  return (
    <Layout>
      <Head>
        <title>My Students – Mentor Dashboard</title>
      </Head>

      <AdminHeader title="My Students" backUrl="/mentors/dashboard" />

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 border border-blue-500/30 rounded-xl p-6">
            <div className="text-techGray text-sm mb-2">Total Students</div>
            <div className="text-4xl font-bold text-white mb-2">{total}</div>
            <div className="text-xs text-techGray">All time</div>
          </div>

          <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 border border-green-500/30 rounded-xl p-6">
            <div className="text-techGray text-sm mb-2">Total Sessions</div>
            <div className="text-4xl font-bold text-white mb-2">
              {students.reduce((sum, s) => sum + s.session_count, 0)}
            </div>
            <div className="text-xs text-techGray">Across all students</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 border border-purple-500/30 rounded-xl p-6">
            <div className="text-techGray text-sm mb-2">Total Revenue</div>
            <div className="text-4xl font-bold text-white mb-2">
              ${students.reduce((sum, s) => sum + s.total_amount, 0).toFixed(2)}
            </div>
            <div className="text-xs text-techGray">From all students</div>
          </div>
        </div>

        {/* Students List */}
        {loading ? (
          <div className="text-center py-12 text-techGray">Loading students...</div>
        ) : students.length === 0 ? (
          <div className="bg-white/5 border border-white/10 rounded-xl p-12 text-center">
            <div className="text-6xl mb-4">👥</div>
            <h3 className="text-xl font-semibold text-white mb-2">No students yet</h3>
            <p className="text-techGray">
              Complete sessions to build your student base
            </p>
          </div>
        ) : (
          <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-white/5 border-b border-white/10">
                  <tr>
                    <th className="text-left p-4 text-techGray font-medium text-sm">Student</th>
                    <th className="text-left p-4 text-techGray font-medium text-sm">Sessions</th>
                    <th className="text-left p-4 text-techGray font-medium text-sm">Revenue</th>
                    <th className="text-left p-4 text-techGray font-medium text-sm">Last Session</th>
                    <th className="text-left p-4 text-techGray font-medium text-sm">Avg/Session</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((student) => (
                    <tr
                      key={student.student_id}
                      className="border-b border-white/10 hover:bg-white/5 transition-colors"
                    >
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-techBlue to-forgePurple flex items-center justify-center text-white font-bold text-sm">
                            S{student.student_id}
                          </div>
                          <div>
                            <div className="text-white font-medium">Student #{student.student_id}</div>
                          </div>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="text-white font-medium">{student.session_count}</div>
                        <div className="text-xs text-techGray">completed</div>
                      </td>
                      <td className="p-4">
                        <div className="text-white font-medium">${student.total_amount.toFixed(2)}</div>
                        <div className="text-xs text-techGray">total</div>
                      </td>
                      <td className="p-4">
                        <div className="text-white">{getLastSessionText(student.last_session)}</div>
                        <div className="text-xs text-techGray">
                          {new Date(student.last_session).toLocaleDateString()}
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="text-white font-medium">
                          ${(student.total_amount / student.session_count).toFixed(2)}
                        </div>
                        <div className="text-xs text-techGray">per session</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}
