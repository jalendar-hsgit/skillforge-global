import { useState, useEffect, useCallback } from 'react';
import Layout from '@/components/Layout';
import { Button } from '@/components/Button';
import { ShoppingCart, Search, Filter, Star, Clock, PlayCircle, Zap } from 'lucide-react';
import Link from 'next/link';

interface Course {
  id: number;
  path: string;
  title: string;
  description: string;
  category: string;
  is_paid: boolean;
  price: number | null;
  video_count: number;
  is_purchased: boolean;
  is_in_cart: boolean;
  rating?: number;
}

export default function MarketplacePage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [freeOnly, setFreeOnly] = useState(false);
  const [cartCount, setCartCount] = useState(0);
  const [addingToCart, setAddingToCart] = useState<number | null>(null);

  const categories = ['All', 'Web Development', 'Data Science', 'Mobile Development', 'Cloud Computing', 'AI/ML', 'Business', 'Design'];

  useEffect(() => {
    fetchCourses();
    fetchCartCount();
  }, [selectedCategory, freeOnly]);

  // Check if there's a pending course to add after login redirect
  useEffect(() => {
    const pendingCourseId = localStorage.getItem('pendingCartCourseId');
    if (pendingCourseId) {
      console.log('[Marketplace] Found pending course to add:', pendingCourseId);
      localStorage.removeItem('pendingCartCourseId');
      
      // Wait a bit for the page to fully load, then add to cart
      setTimeout(() => {
        addToCart(parseInt(pendingCourseId));
      }, 500);
    }
  }, []);

  const fetchCourses = async () => {
    setLoading(true);
    try {
      let url = `/api/session/v1x/marketplace/courses?`;
      if (selectedCategory && selectedCategory !== 'All') {
        url += `category=${encodeURIComponent(selectedCategory)}&`;
      }
      if (freeOnly) {
        url += `free_only=true&`;
      }
      if (searchQuery) {
        url += `search=${encodeURIComponent(searchQuery)}&`;
      }

      const response = await fetch(url, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setCourses(data);
      } else {
        console.error('Failed to fetch courses:', response.status);
      }
    } catch (error) {
      console.error('Error fetching courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCartCount = async () => {
    try {
      const response = await fetch(`/api/session/v1x/marketplace/cart`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setCartCount(data.items.length);
      }
    } catch (error) {
      // User might not be logged in
      setCartCount(0);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCourses();
  };

  const addToCart = useCallback(async (courseId: number) => {
    setAddingToCart(courseId);
    console.log('[Add to Cart] Starting...', { courseId });
    
    try {
      // Use Next.js API proxy to ensure cookies are sent correctly
      const url = '/api/session/v1x/marketplace/cart/add';
      console.log('[Add to Cart] Fetching:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ course_id: courseId })
      });

      console.log('[Add to Cart] Response:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok
      });

      if (response.ok) {
        // Success - show temporary success message
        const tempMsg = document.createElement('div');
        tempMsg.textContent = '✓ Course added to cart!';
        tempMsg.className = 'fixed top-20 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce';
        document.body.appendChild(tempMsg);
        setTimeout(() => tempMsg.remove(), 3000);
        
        fetchCartCount();
        fetchCourses(); // Refresh to update button states
      } else if (response.status === 401) {
        // User not logged in - save course ID and redirect
        console.log('[Add to Cart] 401 - Not authenticated');
        if (confirm('You need to login first. Go to login page?')) {
          // Store the course ID in localStorage so we can add it after login
          localStorage.setItem('pendingCartCourseId', courseId.toString());
          window.location.href = '/login?redirect=/marketplace';
        }
      } else if (response.status === 400) {
        const error = await response.json();
        console.log('[Add to Cart] 400 error:', error);
        
        // Show specific error messages
        let message = error.detail || 'Cannot add to cart. Please check your selection.';
        if (error.detail === 'Course already in cart') {
          message = 'This course is already in your cart. Check your cart to proceed to checkout.';
        } else if (error.detail === 'Course already purchased') {
          message = 'You already purchased this course. Go to your courses to continue.';
        } else if (error.detail === 'Free courses cannot be added to cart') {
          message = 'This free course can be accessed directly without adding to cart.';
        }
        
        alert(message);
        // Refresh course list to update button states in case something changed
        fetchCourses();
      } else if (response.status >= 500) {
        console.log('[Add to Cart] Server error:', response.status);
        alert('Server error. Please try again later.');
      } else {
        const error = await response.json();
        console.log('[Add to Cart] Error:', error);
        alert(error.detail || 'Failed to add to cart. Please try again.');
      }
    } catch (error) {
      console.error('[Add to Cart] Exception:', error);
      alert('Network error. Please check your connection and try again.');
    } finally {
      console.log('[Add to Cart] Finished');
      setAddingToCart(null);
    }
  }, [fetchCartCount, fetchCourses]);

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-deepTech via-deepTech-900 to-deepTech">
        {/* Header */}
        <div className="bg-gradient-to-r from-forgePurple via-neuralBlue to-aiElectric py-12">
          <div className="container">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-display font-black text-white mb-2">Course Marketplace</h1>
                <p className="text-white/90 text-lg">Invest in your future. Learn at your own pace.</p>
              </div>
              
              <Link href="/marketplace/cart" className="relative inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-forgePurple text-white hover:bg-forgePurple/90 transition-colors">
                <ShoppingCart className="w-5 h-5" />
                Cart
                {cartCount > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
                    {cartCount}
                  </span>
                )}
              </Link>
            </div>
          </div>
        </div>

        <div className="container py-8">
          {/* Search and Filters */}
          <div className="bg-deepTech-800 rounded-2xl p-6 mb-8 shadow-glow">
            <form onSubmit={handleSearch} className="mb-6">
              <div className="flex gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-techGray-400 w-5 h-5" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search courses..."
                    className="w-full pl-12 pr-4 py-3 bg-deepTech-900 border-2 border-techGray-700 rounded-xl text-white focus:border-forgePurple focus:outline-none transition-colors"
                  />
                </div>
                <Button type="submit">Search</Button>
              </div>
            </form>

            <div className="flex items-center gap-4 flex-wrap">
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-techGray-400" />
                <span className="text-techGray-300 font-semibold">Filter:</span>
              </div>
              
              {categories.map(cat => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat === 'All' ? '' : cat)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    (cat === 'All' && !selectedCategory) || selectedCategory === cat
                      ? 'bg-forgePurple text-white shadow-glow'
                      : 'bg-deepTech-900 text-techGray-300 hover:bg-deepTech-700'
                  }`}
                >
                  {cat}
                </button>
              ))}

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={freeOnly}
                  onChange={(e) => setFreeOnly(e.target.checked)}
                  className="w-5 h-5 rounded text-forgePurple focus:ring-forgePurple"
                />
                <span className="text-techGray-300 font-medium">Free Only</span>
              </label>
            </div>
          </div>

          {/* Course Grid */}
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-forgePurple border-t-transparent"></div>
              <p className="mt-4 text-techGray-400">Loading courses...</p>
            </div>
          ) : courses.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-techGray-400 text-lg">No courses found matching your criteria.</p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {courses.map(course => (
                <div
                  key={course.id}
                  className="bg-deepTech-800 rounded-2xl overflow-hidden shadow-lg hover:shadow-glowCyan transition-all duration-300 border border-techGray-800 hover:border-forgePurple group"
                >
                  {/* Course Image Placeholder */}
                  <div className="h-48 bg-gradient-to-br from-forgePurple/20 to-neuralBlue/20 flex items-center justify-center">
                    <PlayCircle className="w-16 h-16 text-white/50 group-hover:text-white transition-colors" />
                  </div>

                  <div className="p-6">
                    {/* Category Badge */}
                    {course.category && (
                      <span className="inline-block px-3 py-1 bg-neuralBlue/20 text-neuralBlue text-xs font-semibold rounded-full mb-3">
                        {course.category}
                      </span>
                    )}

                    {/* Title */}
                    <h3 className="text-xl font-bold text-white mb-2 line-clamp-2 group-hover:text-forgePurple transition-colors">
                      {course.title}
                    </h3>

                    {/* Description */}
                    <p className="text-techGray-400 text-sm mb-4 line-clamp-3">
                      {course.description}
                    </p>

                    {/* Meta Info */}
                    <div className="flex items-center gap-4 mb-4 text-sm text-techGray-500">
                      <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        <span>{course.video_count} videos</span>
                      </div>
                      {course.rating && (
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 fill-yellow-500 text-yellow-500" />
                          <span>{course.rating.toFixed(1)}</span>
                        </div>
                      )}
                    </div>

                    {/* Price and Action */}
                    <div className="flex items-center justify-between pt-4 border-t border-techGray-700">
                      <div>
                        {course.is_paid ? (
                          <span className="text-2xl font-black text-forgePurple">
                            ${course.price?.toFixed(2)}
                          </span>
                        ) : (
                          <span className="text-lg font-bold text-green-500">FREE</span>
                        )}
                      </div>

                      {course.is_purchased ? (
                        <Link href={`/courses/${course.path}`} className="inline-flex items-center justify-center px-3 py-1.5 text-sm font-medium rounded-lg bg-deepTech-700 text-techGray-200 hover:bg-deepTech-600 transition-colors">
                          View Course
                        </Link>
                      ) : course.is_in_cart ? (
                        <Link href="/marketplace/cart" className="inline-flex items-center justify-center px-3 py-1.5 text-sm font-medium rounded-lg bg-neuralBlue/50 text-neuralBlue border border-neuralBlue hover:bg-neuralBlue/70 transition-colors">
                          In Cart
                        </Link>
                      ) : course.is_paid ? (
                        <Button
                          size="sm"
                          onClick={() => addToCart(course.id)}
                          disabled={addingToCart === course.id}
                          className="bg-gradient-to-r from-forgePurple to-neuralBlue disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {addingToCart === course.id ? (
                            <span className="flex items-center gap-2">
                              <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                              Adding...
                            </span>
                          ) : (
                            'Add to Cart'
                          )}
                        </Button>
                      ) : (
                        <Link href={`/courses/${course.path}`} className="inline-flex items-center justify-center px-3 py-1.5 text-sm font-medium rounded-lg bg-forgePurple text-white hover:bg-forgePurple/90 transition-colors">
                          Start Learning
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

// Enable SSR to avoid static export issues with authenticated endpoints
export async function getServerSideProps() {
  return { props: {} };
}
