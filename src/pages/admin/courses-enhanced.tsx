import Head from 'next/head'
import Layout from '@/components/Layout'
import AdminHeader from '@/components/AdminHeader'
import { useState, useEffect } from 'react'
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth'

type Course = {
  id: string
  path: string
  title: string
  youtubeId: string
  duration?: string
  featured?: boolean
  enrollments?: number
  completion_rate?: number
  published?: boolean
}

export default function AdminCoursesEnhanced({ me }: AdminSSRProps) {
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedCourses, setSelectedCourses] = useState<Set<string>>(new Set())
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingCourse, setEditingCourse] = useState<Course | null>(null)
  
  // Form state
  const [formData, setFormData] = useState({
    id: '',
    path: '',
    title: '',
    youtubeId: '',
    duration: ''
  })

  useEffect(() => {
    loadCourses()
  }, [])

  async function loadCourses() {
    setLoading(true)
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/courses`,
        { credentials: 'include' }
      )

      if (!res.ok) throw new Error('Failed to load courses')

      const data = await res.json()
      setCourses(data)
    } catch (err) {
      console.error(err)
      setError('Failed to load courses')
    } finally {
      setLoading(false)
    }
  }

  async function handleCreate() {
    if (!formData.title || !formData.path || !formData.youtubeId) {
      alert('Please fill in all required fields')
      return
    }

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/courses`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            id: formData.id || `course-${Date.now()}`,
            path: formData.path,
            title: formData.title,
            youtubeId: formData.youtubeId,
            duration: formData.duration || null
          })
        }
      )

      if (!res.ok) {
        const err = await res.json()
        alert(`Failed to create course: ${err.detail || 'Unknown error'}`)
        return
      }

      alert('Course created successfully!')
      setShowCreateModal(false)
      resetForm()
      loadCourses()
    } catch (err) {
      console.error(err)
      alert('An error occurred')
    }
  }

  async function handleUpdate() {
    if (!editingCourse) return

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/courses/${editingCourse.id}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(formData)
        }
      )

      if (!res.ok) {
        const err = await res.json()
        alert(`Failed to update course: ${err.detail || 'Unknown error'}`)
        return
      }

      alert('Course updated successfully!')
      setEditingCourse(null)
      resetForm()
      loadCourses()
    } catch (err) {
      console.error(err)
      alert('An error occurred')
    }
  }

  async function handleDelete(courseId: string) {
    if (!confirm('Are you sure you want to delete this course?')) return

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/courses/${courseId}`,
        {
          method: 'DELETE',
          credentials: 'include'
        }
      )

      if (!res.ok) throw new Error('Failed to delete')

      alert('Course deleted successfully!')
      loadCourses()
    } catch (err) {
      console.error(err)
      alert('Failed to delete course')
    }
  }

  async function handleBulkDelete() {
    if (selectedCourses.size === 0) {
      alert('No courses selected')
      return
    }

    if (!confirm(`Delete ${selectedCourses.size} selected courses?`)) return

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/courses/bulk-delete`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(Array.from(selectedCourses))
        }
      )

      if (!res.ok) throw new Error('Failed to delete')

      const data = await res.json()
      alert(data.message)
      setSelectedCourses(new Set())
      loadCourses()
    } catch (err) {
      console.error(err)
      alert('Failed to delete courses')
    }
  }

  async function toggleFeatured(courseId: string) {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/courses/${courseId}/toggle-featured`,
        {
          method: 'POST',
          credentials: 'include'
        }
      )

      if (!res.ok) throw new Error('Failed to toggle')

      loadCourses()
    } catch (err) {
      console.error(err)
      alert('Failed to toggle featured status')
    }
  }

  function resetForm() {
    setFormData({
      id: '',
      path: '',
      title: '',
      youtubeId: '',
      duration: ''
    })
  }

  function openEditModal(course: Course) {
    setEditingCourse(course)
    setFormData({
      id: course.id,
      path: course.path,
      title: course.title,
      youtubeId: course.youtubeId,
      duration: course.duration || ''
    })
  }

  function toggleCourseSelection(courseId: string) {
    const newSet = new Set(selectedCourses)
    if (newSet.has(courseId)) {
      newSet.delete(courseId)
    } else {
      newSet.add(courseId)
    }
    setSelectedCourses(newSet)
  }

  function exportToCSV() {
    const headers = ['ID', 'Path', 'Title', 'YouTube ID', 'Duration', 'Enrollments', 'Featured']
    const rows = courses.map(c => [
      c.id,
      c.path,
      c.title,
      c.youtubeId,
      c.duration || '',
      c.enrollments || 0,
      c.featured ? 'Yes' : 'No'
    ])

    const csv = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `courses_export_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  return (
    <Layout>
      <Head>
        <title>Course Management – Admin – SkillForge Global</title>
      </Head>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Course Management</h1>
          <p className="text-techGray">Create, edit, and manage course content</p>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/30 p-4 bg-red-500/10 text-red-300">
            {error}
          </div>
        )}

        {/* Action Buttons */}
        <div className="mb-6 flex flex-wrap gap-3">
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-forgePurple hover:bg-forgePurple/80 rounded-lg font-medium transition-colors"
          >
            ➕ Create Course
          </button>
          <button
            onClick={handleBulkDelete}
            disabled={selectedCourses.size === 0}
            className="px-6 py-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
          >
            🗑️ Delete Selected ({selectedCourses.size})
          </button>
          <button
            onClick={exportToCSV}
            disabled={courses.length === 0}
            className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
          >
            📥 Export CSV
          </button>
          <button
            onClick={loadCourses}
            className="px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg font-medium transition-colors"
          >
            🔄 Refresh
          </button>
        </div>

        {/* Courses Table */}
        {loading ? (
          <div className="text-center py-12 text-gray-400">Loading courses...</div>
        ) : courses.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400 mb-4">No courses found</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-forgePurple hover:bg-forgePurple/80 rounded-lg font-medium transition-colors"
            >
              Create Your First Course
            </button>
          </div>
        ) : (
          <div className="rounded-xl border border-white/10 bg-white/5 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-sm text-gray-400 border-b border-white/10 bg-white/5">
                    <th className="p-4">
                      <input
                        type="checkbox"
                        checked={selectedCourses.size === courses.length && courses.length > 0}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedCourses(new Set(courses.map(c => c.id)))
                          } else {
                            setSelectedCourses(new Set())
                          }
                        }}
                        className="w-4 h-4"
                      />
                    </th>
                    <th className="p-4">Title</th>
                    <th className="p-4">Path</th>
                    <th className="p-4">YouTube ID</th>
                    <th className="p-4">Duration</th>
                    <th className="p-4">Enrollments</th>
                    <th className="p-4">Status</th>
                    <th className="p-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {courses.map((course) => (
                    <tr key={course.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                      <td className="p-4">
                        <input
                          type="checkbox"
                          checked={selectedCourses.has(course.id)}
                          onChange={() => toggleCourseSelection(course.id)}
                          className="w-4 h-4"
                        />
                      </td>
                      <td className="p-4">
                        <div className="text-white font-medium">{course.title}</div>
                        {course.featured && (
                          <span className="text-xs bg-yellow-500/20 text-yellow-300 px-2 py-0.5 rounded-full">
                            ⭐ Featured
                          </span>
                        )}
                      </td>
                      <td className="p-4 text-gray-300">/{course.path}</td>
                      <td className="p-4 text-gray-400 font-mono text-sm">{course.youtubeId}</td>
                      <td className="p-4 text-gray-400">{course.duration || 'N/A'}</td>
                      <td className="p-4 text-gray-300">{course.enrollments || 0}</td>
                      <td className="p-4">
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          course.published 
                            ? 'bg-green-500/20 text-green-300'
                            : 'bg-gray-500/20 text-gray-400'
                        }`}>
                          {course.published ? 'Published' : 'Draft'}
                        </span>
                      </td>
                      <td className="p-4">
                        <div className="flex gap-2">
                          <button
                            onClick={() => openEditModal(course)}
                            className="text-blue-400 hover:text-blue-300 text-sm"
                            title="Edit"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => toggleFeatured(course.id)}
                            className="text-yellow-400 hover:text-yellow-300 text-sm"
                            title="Toggle Featured"
                          >
                            ⭐
                          </button>
                          <button
                            onClick={() => handleDelete(course.id)}
                            className="text-red-400 hover:text-red-300 text-sm"
                            title="Delete"
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Create/Edit Modal */}
        {(showCreateModal || editingCourse) && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold text-white mb-6">
                {editingCourse ? 'Edit Course' : 'Create New Course'}
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Course Title *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white"
                    placeholder="e.g., Python for AI & Machine Learning"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    URL Path (Slug) *
                  </label>
                  <input
                    type="text"
                    value={formData.path}
                    onChange={(e) => setFormData({ ...formData, path: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white font-mono"
                    placeholder="e.g., python-ai"
                  />
                  <p className="text-xs text-gray-500 mt-1">Will be: /paths/{formData.path || 'slug'}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    YouTube Video ID *
                  </label>
                  <input
                    type="text"
                    value={formData.youtubeId}
                    onChange={(e) => setFormData({ ...formData, youtubeId: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white font-mono"
                    placeholder="e.g., dQw4w9WgXcQ"
                  />
                  <p className="text-xs text-gray-500 mt-1">From: youtube.com/watch?v=<strong>dQw4w9WgXcQ</strong></p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Duration (Optional)
                  </label>
                  <input
                    type="text"
                    value={formData.duration}
                    onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white"
                    placeholder="e.g., 8 hours"
                  />
                </div>

                {!editingCourse && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Course ID (Optional - auto-generated if empty)
                    </label>
                    <input
                      type="text"
                      value={formData.id}
                      onChange={(e) => setFormData({ ...formData, id: e.target.value })}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white font-mono"
                      placeholder="Auto-generated"
                    />
                  </div>
                )}
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={editingCourse ? handleUpdate : handleCreate}
                  className="flex-1 px-6 py-3 bg-forgePurple hover:bg-forgePurple/80 rounded-lg font-medium transition-colors"
                >
                  {editingCourse ? 'Update Course' : 'Create Course'}
                </button>
                <button
                  onClick={() => {
                    setShowCreateModal(false)
                    setEditingCourse(null)
                    resetForm()
                  }}
                  className="px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg font-medium transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

export const getServerSideProps = requireAdminSSR
