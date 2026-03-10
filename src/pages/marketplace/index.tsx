import { useState, useEffect, useCallback } from 'react';
import Layout from '@/components/Layout';
import { Button } from '@/components/Button';
import { ShoppingCart, Search, Filter, Star, Clock, PlayCircle } from 'lucide-react';
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
      let url = `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/marketplace/courses?`;
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
        credentials: 'include',
      });

      if (!response.ok) {
        console.error('Failed to fetch courses:', response.status);
        return;
      }

      const data = await response.json();
      setCourses(Array.isArray(data) ? data : data.courses || []);
    } catch (error) {
      console.error('Error fetching courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCartCount = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/cart`, {
        credentials: 'include',
      });

      if (!response.ok) return;

      const data = await response.json();
      setCartCount(data.items?.length || 0);
    } catch (error) {
      console.error('Error fetching cart count:', error);
    }
  };

  const addToCart = useCallback(
    async (courseId: number) => {
      setAddingToCart(courseId);
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/cart/add`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            course_id: courseId,
          }),
        });

        if (response.status === 401) {
          // Not authenticated - redirect to login
          localStorage.setItem('pendingCartCourseId', courseId.toString());
          window.location.href = '/auth/login?redirect=/marketplace';
          return;
        }

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          alert(errorData.detail || 'Failed to add to cart');
          return;
        }

        // Update cart count
        await fetchCartCount();
        
        // Update local state
        setCourses(courses.map(c =>
          c.id === courseId ? { ...c, is_in_cart: true } : c
        ));

        alert('Added to cart!');
      } catch (error) {
        console.error('Error adding to cart:', error);
        alert('Error adding to cart. Please try again.');
      } finally {
        setAddingToCart(null);
      }
    },
    [courses]
  );

  const handleSearch = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  }, []);

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-deepTech via-deepTech-900 to-deepTech py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-12">
            <h1 className="text-4xl font-bold text-white mb-4">Courses Marketplace</h1>
            <p className="text-lg text-techGray-300">Discover and learn from expert-created courses</p>
          </div>

          {/* Cart Link */}
          <div className="flex justify-end mb-6">
            <Link href="/marketplace/cart">
              <Button className="flex items-center gap-2 bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90">
                <ShoppingCart size={20} />
                Cart {cartCount > 0 && <span className="bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">{cartCount}</span>}
              </Button>
            </Link>
          </div>

          {/* Search and Filters */}
          <div className="bg-deepTech-800 rounded-2xl shadow-lg p-6 mb-8 border border-techGray-800">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
              {/* Search */}
              <div className="lg:col-span-2">
                <div className="relative">
                  <Search className="absolute left-3 top-3 text-techGray-500" size={20} />
                  <input
                    type="text"
                    placeholder="Search courses..."
                    value={searchQuery}
                    onChange={handleSearch}
                    className="w-full pl-10 pr-4 py-3 bg-deepTech-900 border border-techGray-700 rounded-lg text-white placeholder-techGray-500 focus:ring-2 focus:ring-forgePurple focus:border-transparent"
                  />
                </div>
              </div>

              {/* Free Only Toggle */}
              <div className="flex items-center gap-3 justify-end">
                <input
                  type="checkbox"
                  id="freeOnly"
                  checked={freeOnly}
                  onChange={(e) => setFreeOnly(e.target.checked)}
                  className="w-4 h-4"
                />
                <label htmlFor="freeOnly" className="text-sm font-medium text-white">
                  Free Only
                </label>
              </div>
            </div>

            {/* Categories */}
            <div className="flex flex-wrap gap-2">
              <span className="text-sm font-medium text-techGray-300 flex items-center gap-2">
                <Filter size={16} /> Categories:
              </span>
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-4 py-2 rounded-full font-medium transition ${
                    selectedCategory === cat
                      ? 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white'
                      : 'bg-deepTech-900 text-techGray-300 border border-techGray-700 hover:border-forgePurple'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-forgePurple border-t-transparent"></div>
            </div>
          )}

          {/* Courses Grid */}
          {!loading && (
            <>
              {courses.length === 0 ? (
                <div className="text-center py-12 bg-deepTech-800 rounded-2xl border border-techGray-800">
                  <p className="text-techGray-300 text-lg">No courses found. Try adjusting your filters.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {courses.map((course) => (
                    <div
                      key={course.id}
                      className="bg-deepTech-800 rounded-2xl shadow-lg hover:shadow-xl transition border border-techGray-800 hover:border-forgePurple overflow-hidden"
                    >
                      {/* Course Header */}
                      <div className="bg-gradient-to-r from-forgePurple to-neuralBlue p-6 text-white">
                        <h3 className="text-xl font-bold mb-2">{course.title}</h3>
                        <p className="text-white/80 text-sm line-clamp-2">{course.description}</p>
                      </div>

                      {/* Course Info */}
                      <div className="p-6">
                        <div className="space-y-3 mb-6">
                          {/* Category */}
                          <div className="flex items-center gap-2 text-sm">
                            <span className="bg-forgePurple/20 text-forgePurple px-3 py-1 rounded-full font-medium">
                              {course.category}
                            </span>
                          </div>

                          {/* Video Count */}
                          {course.video_count > 0 && (
                            <div className="flex items-center gap-2 text-sm text-techGray-300">
                              <PlayCircle size={16} className="text-forgePurple" />
                              {course.video_count} videos
                            </div>
                          )}

                          {/* Rating */}
                          {course.rating && (
                            <div className="flex items-center gap-2 text-sm text-techGray-300">
                              <Star size={16} className="text-yellow-400" />
                              {course.rating.toFixed(1)} rating
                            </div>
                          )}

                          {/* Price */}
                          <div className="text-2xl font-black text-forgePurple">
                            {course.is_paid ? `$${course.price?.toFixed(2)}` : 'Free'}
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="space-y-2">
                          <Link href={`/courses/${course.path}`} className="w-full block">
                            <Button className="w-full variant-outline border border-techGray-700 text-white hover:border-forgePurple hover:bg-forgePurple/10">
                              View Details
                            </Button>
                          </Link>

                          {course.is_purchased ? (
                            <div className="text-center py-2 bg-green-600/20 text-green-400 rounded-lg font-medium text-sm">
                              ✓ Purchased
                            </div>
                          ) : course.is_in_cart ? (
                            <div className="text-center py-2 bg-forgePurple/20 text-forgePurple rounded-lg font-medium text-sm">
                              In Cart
                            </div>
                          ) : (
                            <Button
                              onClick={() => addToCart(course.id)}
                              disabled={addingToCart === course.id}
                              className="w-full bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90 text-white font-bold flex items-center justify-center gap-2"
                            >
                              <ShoppingCart size={18} />
                              {addingToCart === course.id ? 'Adding...' : 'Add to Cart'}
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
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
