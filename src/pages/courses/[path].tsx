import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Button } from '@/components/Button';
import { useRouter } from 'next/router';
import { ShoppingCart, Star, ArrowLeft, AlertCircle, Book, Clock, Users } from 'lucide-react';
import Link from 'next/link';

interface CourseDetail {
  id: number;
  path: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  price: number;
  is_paid: boolean;
  is_premium: boolean;
  rating?: number | null;
  video_count: number;
  created_at?: string;
  updated_at?: string;
  is_purchased?: boolean;
  is_in_cart?: boolean;
}

export default function CourseDetailsPage() {
  const router = useRouter();
  const { path } = router.query;
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [addingToCart, setAddingToCart] = useState(false);
  const [addedSuccess, setAddedSuccess] = useState(false);

  useEffect(() => {
    if (!path) return;
    fetchCourse();
  }, [path]);

  const fetchCourse = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/courses?path=${path}`,
        { credentials: 'include' }
      );

      if (!response.ok) {
        setError('Course not found');
        return;
      }

      const data = await response.json();
      // API returns array, get first item matching path
      const courses = Array.isArray(data) ? data : data.courses || [];
      const courseData = courses.find((c: CourseDetail) => c.path === path);
      
      if (!courseData) {
        setError('Course not found');
        return;
      }

      setCourse(courseData);
    } catch (error) {
      console.error('Error fetching course:', error);
      setError('Failed to load course details');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!course) return;

    setAddingToCart(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/cart/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ course_id: course.id }),
      });

      if (response.status === 401) {
        localStorage.setItem('pendingCartCourseId', course.id.toString());
        router.push('/auth/login?redirect=/marketplace');
        return;
      }

      if (response.ok) {
        setAddedSuccess(true);
        setCourse({ ...course, is_in_cart: true });
        setTimeout(() => setAddedSuccess(false), 3000);
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to add to cart');
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
      setError('Network error. Please try again.');
    } finally {
      setAddingToCart(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-deepTech via-deepTech-900 to-deepTech flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-forgePurple border-t-transparent mx-auto mb-4"></div>
            <p className="text-techGray-400">Loading course details...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!course || error) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-deepTech via-deepTech-900 to-deepTech py-12">
          <div className="container">
            <div className="mb-8">
              <Link href="/marketplace" className="inline-flex items-center gap-2 text-techGray-400 hover:text-white transition-colors">
                <ArrowLeft className="w-5 h-5" />
                Back to Courses
              </Link>
            </div>
            <div className="bg-deepTech-800 rounded-2xl p-8 border border-red-500/20 text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-white mb-2">Course Not Found</h1>
              <p className="text-techGray-400 mb-6">{error || 'The course you are looking for does not exist.'}</p>
              <Link href="/marketplace">
                <Button>Browse Courses</Button>
              </Link>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-deepTech via-deepTech-900 to-deepTech py-12">
        <div className="container">
          {/* Back Button */}
          <Link href="/marketplace" className="inline-flex items-center gap-2 text-techGray-400 hover:text-white transition-colors mb-8">
            <ArrowLeft className="w-5 h-5" />
            Back to Courses
          </Link>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-2">
              {/* Header */}
              <div className="mb-8">
                <div className="inline-block mb-4 px-4 py-2 rounded-lg bg-forgePurple/20 border border-forgePurple/50">
                  <span className="text-forgePurple font-medium text-sm">{course.category}</span>
                </div>

                <h1 className="text-4xl font-bold text-white mb-4">{course.title}</h1>

                <div className="flex flex-wrap gap-6 mb-6">
                  <div className="flex items-center gap-2">
                    <Book className="w-5 h-5 text-aiElectric" />
                    <span className="text-techGray-300">{course.video_count || 'Multiple'} Videos</span>
                  </div>
                  {course.difficulty && (
                    <div className="flex items-center gap-2">
                      <Clock className="w-5 h-5 text-neuralBlue" />
                      <span className="text-techGray-300">{course.difficulty} Level</span>
                    </div>
                  )}
                  {course.rating && (
                    <div className="flex items-center gap-2">
                      <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                      <span className="text-techGray-300">{course.rating.toFixed(1)} Rating</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Description */}
              <div className="bg-deepTech-800/50 rounded-xl p-8 border border-techGray-700/30 mb-8">
                <h2 className="text-xl font-semibold text-white mb-4">About This Course</h2>
                <p className="text-techGray-300 leading-relaxed">{course.description}</p>
              </div>

              {/* Course Benefits */}
              <div className="bg-deepTech-800/50 rounded-xl p-8 border border-techGray-700/30">
                <h2 className="text-xl font-semibold text-white mb-4">What You'll Learn</h2>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-forgePurple mt-2 flex-shrink-0"></div>
                    <span className="text-techGray-300">Comprehensive training on core concepts</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-forgePurple mt-2 flex-shrink-0"></div>
                    <span className="text-techGray-300">Hands-on practical experience</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-forgePurple mt-2 flex-shrink-0"></div>
                    <span className="text-techGray-300">Industry-best practices and techniques</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-forgePurple mt-2 flex-shrink-0"></div>
                    <span className="text-techGray-300">Certificate of completion</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Sidebar - Pricing & CTA */}
            <div className="lg:col-span-1">
              <div className="sticky top-24 bg-gradient-to-br from-forgePurple/10 to-neuralBlue/10 rounded-2xl p-8 border border-forgePurple/30">
                {/* Price */}
                <div className="mb-8">
                  {course.is_paid ? (
                    <>
                      <p className="text-techGray-400 text-sm mb-2">Course Price</p>
                      <div className="flex items-baseline gap-2">
                        <span className="text-4xl font-bold text-forgePurple">${course.price.toFixed(2)}</span>
                        {course.is_premium && (
                          <span className="text-sm px-2 py-1 rounded bg-aiElectric/20 text-aiElectric">Premium</span>
                        )}
                      </div>
                    </>
                  ) : (
                    <p className="text-2xl font-bold text-green-400">FREE</p>
                  )}
                </div>

                {/* Status Messages */}
                {error && (
                  <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/50">
                    <p className="text-red-400 text-sm">{error}</p>
                  </div>
                )}

                {addedSuccess && (
                  <div className="mb-4 p-3 rounded-lg bg-green-500/10 border border-green-500/50">
                    <p className="text-green-400 text-sm">✓ Added to cart successfully!</p>
                  </div>
                )}

                {/* Buttons */}
                <div className="space-y-3">
                  {course.is_purchased ? (
                    <div className="w-full py-3 rounded-lg bg-green-600/20 border border-green-500 text-green-400 font-medium text-center">
                      ✓ Already Purchased
                    </div>
                  ) : course.is_in_cart ? (
                    <Link href="/marketplace/cart" className="w-full block">
                      <Button className="w-full bg-gradient-to-r from-forgePurple to-neuralBlue">
                        View in Cart
                      </Button>
                    </Link>
                  ) : (
                    <button
                      onClick={handleAddToCart}
                      disabled={addingToCart}
                      className="w-full py-3 rounded-lg font-semibold text-white transition-all duration-200 bg-gradient-to-r from-forgePurple to-neuralBlue hover:shadow-lg hover:shadow-forgePurple/50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      <ShoppingCart className="w-5 h-5" />
                      {addingToCart ? 'Adding...' : 'Add to Cart'}
                    </button>
                  )}

                  <Link href="/marketplace" className="w-full block">
                    <Button variant="outline" className="w-full border border-techGray-700 text-white hover:border-forgePurple hover:bg-forgePurple/10">
                      Browse More Courses
                    </Button>
                  </Link>
                </div>

                {/* Info */}
                <div className="mt-8 pt-8 border-t border-techGray-700/30 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-techGray-400 text-sm">Difficulty</span>
                    <span className="text-white font-medium">{course.difficulty || 'Intermediate'}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-techGray-400 text-sm">Category</span>
                    <span className="text-white font-medium">{course.category}</span>
                  </div>
                  {course.video_count > 0 && (
                    <div className="flex items-center justify-between">
                      <span className="text-techGray-400 text-sm">Total Videos</span>
                      <span className="text-white font-medium">{course.video_count}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
