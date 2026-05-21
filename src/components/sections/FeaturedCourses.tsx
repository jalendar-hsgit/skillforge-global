import { useEffect, useState } from 'react'
import Link from 'next/link'
import { PageSection } from '@/components/PageLayout'

interface Course {
  id: string
  slug: string
  title: string
  description: string
  instructor?: string
  duration?: string
  level?: string
}

export default function FeaturedCourses() {
  const [featuredSlugs, setFeaturedSlugs] = useState<string[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchFeaturedCourses() {
      try {
        // Fetch featured course slugs from settings (public endpoint)
        const settingsRes = await fetch('/api/v1x/admin/settings/public')
        if (settingsRes.ok) {
          const settings = await settingsRes.json()
          const featured = settings.featured_courses || []
          
          if (featured.length === 0) {
            setLoading(false)
            return
          }
          
          setFeaturedSlugs(featured)
          
          // Fetch all courses
          const coursesRes = await fetch('/api/v1/courses')
          if (coursesRes.ok) {
            const allCourses = await coursesRes.json()
            // Filter to only featured courses
            const featuredCourses = allCourses.filter((c: Course) => 
              featured.includes(c.slug)
            )
            setCourses(featuredCourses)
          }
        }
      } catch (error) {
        console.error('Error fetching featured courses:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchFeaturedCourses()
  }, [])

  // Don't render if no featured courses
  if (!loading && courses.length === 0) {
    return null
  }

  return (
    <PageSection icon="⭐" title="Featured Courses" subtitle="Hand-picked courses to accelerate your learning journey">
      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading featured courses...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <Link 
              key={course.id} 
              href={`/courses/${course.slug}`}
              className="group relative bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
            >
              <div className="absolute top-4 right-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  ⭐ Featured
                </span>
              </div>
              
              <div className="mb-3">
                <h3 className="text-xl font-semibold text-gray-900 group-hover:text-purple-600 transition-colors mb-2">
                  {course.title}
                </h3>
                <p className="text-gray-600 text-sm line-clamp-3">
                  {course.description}
                </p>
              </div>
              
              <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
                {course.instructor && (
                  <span className="flex items-center gap-1">
                    <span className="text-gray-400">👤</span>
                    {course.instructor}
                  </span>
                )}
                {course.duration && (
                  <span className="flex items-center gap-1">
                    <span className="text-gray-400">⏱️</span>
                    {course.duration}
                  </span>
                )}
                {course.level && (
                  <span className="flex items-center gap-1">
                    <span className={`inline-block w-2 h-2 rounded-full ${
                      course.level === 'beginner' ? 'bg-green-500' :
                      course.level === 'intermediate' ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}></span>
                    {course.level}
                  </span>
                )}
              </div>
              
              <div className="mt-4 text-purple-600 font-medium text-sm group-hover:underline">
                View Course →
              </div>
            </Link>
          ))}
        </div>
      )}
    </PageSection>
  )
}
