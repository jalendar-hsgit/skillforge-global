import { useState, useEffect } from 'react';
import { Trash2, Loader2, Heart } from 'lucide-react';
import Link from 'next/link';

interface WishlistItem {
  id: number;
  product_id: number;
  product_name: string;
  product_slug: string;
  product_price: number;
  product_type: string;
  seller_id: number;
  seller_name: string;
  created_at: string;
}

const sortOptions = [
  { value: 'newest', label: 'Newest First' },
  { value: 'oldest', label: 'Oldest First' },
  { value: 'price_low', label: 'Price: Low to High' },
  { value: 'price_high', label: 'Price: High to Low' }
];

export default function WishlistPage() {
  const [items, setItems] = useState<WishlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const [removing, setRemoving] = useState<number | null>(null);
  const [isClient, setIsClient] = useState(false);

  const limit = 10;

  // Check if authenticated - client-side only
  useEffect(() => {
    setIsClient(true);
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Please login to view your wishlist');
      }
    }
  }, []);

  useEffect(() => {
    fetchWishlist();
  }, [page, sortBy]);

  const fetchWishlist = async () => {
    try {
      setLoading(true);
      setError('');

      const token = localStorage.getItem('token');
      if (!token) {
        setError('Please login to view your wishlist');
        setLoading(false);
        return;
      }

      const response = await fetch(
        `http://localhost:8001/api/v1x/marketplace/wishlist?skip=${page * limit}&limit=${limit}&sort_by=${sortBy}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch wishlist');
      }

      const data = await response.json();
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading wishlist');
    } finally {
      setLoading(false);
    }
  };

  const removeFromWishlist = async (productId: number) => {
    try {
      setRemoving(productId);

      const token = localStorage.getItem('token');
      if (!token) {
        alert('Please login to manage your wishlist');
        return;
      }

      const response = await fetch(
        `http://localhost:8001/api/v1x/marketplace/wishlist/${productId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to remove from wishlist');
      }

      // Remove item from list
      setItems(items.filter(item => item.product_id !== productId));
      setTotal(total - 1);
    } catch (err) {
      alert('Error removing from wishlist');
    } finally {
      setRemoving(null);
    }
  };

  const totalPages = Math.ceil(total / limit);

  // Don't render login message on server
  if (!isClient) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto" />
          </div>
        </div>
      </div>
    );
  }

  if (error && error.includes('login')) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Login Required</h1>
            <p className="text-gray-600 mb-8">Please login to view your wishlist</p>
            <Link
              href="/login"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
            >
              Login
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Wishlist</h1>
          <p className="text-gray-600">
            {total} item{total !== 1 ? 's' : ''} saved
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Sort Controls */}
        {items.length > 0 && (
          <div className="mb-6 flex items-center gap-4">
            <label className="flex items-center gap-2 text-gray-700">
              <span className="font-medium">Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value);
                  setPage(0);
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        )}

        {/* Empty State */}
        {!loading && items.length === 0 && (
          <div className="text-center py-12">
            <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">No items in your wishlist</h2>
            <p className="text-gray-600 mb-8">
              Start saving products you'd like to purchase later
            </p>
            <Link
              href="/marketplace"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
            >
              Explore Marketplace
            </Link>
          </div>
        )}

        {/* Items Grid */}
        {!loading && items.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
              {items.map(item => (
                <div
                  key={item.id}
                  className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow overflow-hidden"
                >
                  {/* Product Image Placeholder */}
                  <div className="bg-gradient-to-br from-blue-400 to-blue-600 h-40 flex items-center justify-center">
                    <span className="text-white text-sm font-medium capitalize">
                      {item.product_type}
                    </span>
                  </div>

                  {/* Product Details */}
                  <div className="p-4">
                    <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                      {item.product_name}
                    </h3>

                    <p className="text-sm text-gray-600 mb-3">
                      by <span className="font-medium">{item.seller_name}</span>
                    </p>

                    <div className="flex items-end justify-between mb-4">
                      <div>
                        <p className="text-2xl font-bold text-gray-900">
                          ${item.product_price.toFixed(2)}
                        </p>
                        <p className="text-xs text-gray-500">
                          Added {new Date(item.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <Link
                        href={`/marketplace/${item.product_slug}`}
                        className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-center text-sm font-medium hover:bg-blue-700 transition-colors"
                      >
                        View
                      </Link>
                      <button
                        onClick={() => removeFromWishlist(item.product_id)}
                        disabled={removing === item.product_id}
                        className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50"
                      >
                        {removing === item.product_id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 0}
                  className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 hover:bg-gray-50"
                >
                  Previous
                </button>
                <div className="flex items-center gap-1">
                  {Array.from({ length: totalPages }, (_, i) => (
                    <button
                      key={i}
                      onClick={() => setPage(i)}
                      className={`w-10 h-10 rounded-lg font-medium ${
                        page === i
                          ? 'bg-blue-600 text-white'
                          : 'border border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      {i + 1}
                    </button>
                  ))}
                </div>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page >= totalPages - 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 hover:bg-gray-50"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
