import { useState, useEffect, useCallback } from 'react';
import Layout from '@/components/Layout';
import { Button } from '@/components/Button';
import { Search, Filter, Star, ShoppingCart, Download, Eye } from 'lucide-react';
import Link from 'next/link';

interface DigitalProduct {
  id: number;
  name: string;
  slug: string;
  description: string;
  price: number;
  category: string;
  product_type: string;
  status: string;
  sales_count: number;
  average_rating: number;
  seller_id: number;
  seller_name?: string;
  thumbnail_url?: string;
  file_size?: string;
  download_count?: number;
}

export default function DigitalProductsPage() {
  const [products, setProducts] = useState<DigitalProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [sortBy, setSortBy] = useState('popularity');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [cartCount, setCartCount] = useState(0);

  const categories = ['All', 'Programming', 'Design', 'Business', 'Marketing', 'Education', 'Development'];
  const productTypes = ['All', 'Template', 'Guide', 'Cheatsheet', 'Course', 'Resource'];
  const sortOptions = [
    { value: 'popularity', label: 'Most Popular' },
    { value: 'newest', label: 'Newest First' },
    { value: 'price_low', label: 'Price: Low to High' },
    { value: 'price_high', label: 'Price: High to Low' },
    { value: 'rating', label: 'Highest Rated' },
  ];

  useEffect(() => {
    fetchProducts();
    fetchCartCount();
  }, [searchQuery, selectedCategory, selectedType, sortBy, page]);

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

  const fetchProducts = async () => {
    setLoading(true);
    try {
      let url = `${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/digital-products?`;
      
      if (selectedCategory && selectedCategory !== 'All') {
        url += `category=${encodeURIComponent(selectedCategory)}&`;
      }
      if (selectedType && selectedType !== 'All') {
        url += `type=${encodeURIComponent(selectedType)}&`;
      }
      if (searchQuery) {
        url += `search=${encodeURIComponent(searchQuery)}&`;
      }
      if (sortBy) {
        url += `sort_by=${encodeURIComponent(sortBy)}&`;
      }
      url += `page=${page}&per_page=12`;

      const response = await fetch(url, {
        credentials: 'include',
      });

      if (!response.ok) {
        console.error('Failed to fetch products:', response.status);
        return;
      }

      const data = await response.json();
      setProducts(data.products || []);
      setTotalPages(data.total_pages || 1);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setPage(1);
  }, []);

  const [addingToCart, setAddingToCart] = useState<number | null>(null);

  const addToCart = useCallback(
    async (productId: number) => {
      setAddingToCart(productId);
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/cart/add-digital-product`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            product_id: productId,
          }),
        });

        if (response.status === 401) {
          localStorage.setItem('pendingCartProductId', productId.toString());
          window.location.href = '/auth/login?redirect=/marketplace/digital-products';
          return;
        }

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          console.error('Add to cart error:', errorData);
          alert(errorData.detail || 'Failed to add to cart');
          return;
        }

        setProducts(products.map(p => p.id === productId ? { ...p, sales_count: p.sales_count + 1 } : p));
        await fetchCartCount();
        alert('✓ Added to cart!');
      } catch (error) {
        console.error('Error adding to cart:', error);
        alert('Error adding to cart. Please try again.');
      } finally {
        setAddingToCart(null);
      }
    },
    [products]
  );

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-deepTech via-deepTech-900 to-deepTech py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header with Cart Icon */}
          <div className="mb-12 flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold text-white mb-4">Digital Products</h1>
              <p className="text-lg text-techGray-300">Templates, guides, and resources from expert creators</p>
            </div>
            <Link href="/marketplace/cart">
              <Button className="flex items-center gap-2 bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90">
                <ShoppingCart size={20} />
                Cart {cartCount > 0 && <span className="bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">{cartCount}</span>}
              </Button>
            </Link>
          </div>

          {/* Filters Section */}
          <div className="bg-deepTech-800 rounded-2xl shadow-lg p-6 mb-8 border border-techGray-800">
            {/* Search */}
            <div className="mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-3 text-techGray-500" size={20} />
                <input
                  type="text"
                  placeholder="Search products..."
                  value={searchQuery}
                  onChange={handleSearch}
                  className="w-full pl-10 pr-4 py-3 bg-deepTech-900 border border-techGray-700 rounded-lg text-white placeholder-techGray-500 focus:ring-2 focus:ring-forgePurple focus:border-transparent"
                />
              </div>
            </div>

            {/* Filter Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium text-white mb-2 flex items-center gap-2">
                  <Filter size={16} /> Category
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => {
                    setSelectedCategory(e.target.value);
                    setPage(1);
                  }}
                  className="w-full px-3 py-2 bg-deepTech-900 border border-techGray-700 rounded-lg text-white focus:ring-2 focus:ring-forgePurple focus:border-transparent"
                >
                  {categories.map((cat) => (
                    <option key={cat} value={cat === 'All' ? '' : cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              {/* Product Type Filter */}
              <div>
                <label className="block text-sm font-medium text-white mb-2 flex items-center gap-2">
                  <Filter size={16} /> Product Type
                </label>
                <select
                  value={selectedType}
                  onChange={(e) => {
                    setSelectedType(e.target.value);
                    setPage(1);
                  }}
                  className="w-full px-3 py-2 bg-deepTech-900 border border-techGray-700 rounded-lg text-white focus:ring-2 focus:ring-forgePurple focus:border-transparent"
                >
                  {productTypes.map((type) => (
                    <option key={type} value={type === 'All' ? '' : type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>

              {/* Sort */}
              <div>
                <label className="block text-sm font-medium text-white mb-2 flex items-center gap-2">
                  <Filter size={16} /> Sort By
                </label>
                <select
                  value={sortBy}
                  onChange={(e) => {
                    setSortBy(e.target.value);
                    setPage(1);
                  }}
                  className="w-full px-3 py-2 bg-deepTech-900 border border-techGray-700 rounded-lg text-white focus:ring-2 focus:ring-forgePurple focus:border-transparent"
                >
                  {sortOptions.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Active Filters Display */}
            {(selectedCategory || selectedType || searchQuery) && (
              <div className="flex flex-wrap gap-2">
                {searchQuery && (
                  <span className="bg-forgePurple/20 text-forgePurple px-3 py-1 rounded-full text-sm">
                    Search: {searchQuery}
                  </span>
                )}
                {selectedCategory && (
                  <span className="bg-neuralBlue/20 text-neuralBlue px-3 py-1 rounded-full text-sm">
                    Category: {selectedCategory}
                  </span>
                )}
                {selectedType && (
                  <span className="bg-aiElectric/20 text-aiElectric px-3 py-1 rounded-full text-sm">
                    Type: {selectedType}
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-forgePurple border-t-transparent"></div>
            </div>
          )}

          {/* Products Grid */}
          {!loading && (
            <>
              {products.length === 0 ? (
                <div className="text-center py-12 bg-deepTech-800 rounded-2xl border border-techGray-800">
                  <p className="text-techGray-300 text-lg">No products found. Try adjusting your filters.</p>
                </div>
              ) : (
                <>
                  {/* Product Count */}
                  <div className="mb-4 text-techGray-300">
                    Showing {products.length} products
                  </div>

                  {/* Products Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
                    {products.map((product) => (
                      <div
                        key={product.id}
                        className="bg-deepTech-800 rounded-2xl shadow-lg hover:shadow-xl transition overflow-hidden flex flex-col border border-techGray-800 hover:border-forgePurple"
                      >
                        {/* Product Image/Header */}
                        <div className="h-40 bg-gradient-to-br from-forgePurple to-neuralBlue p-4 flex items-center justify-center relative">
                          {product.thumbnail_url ? (
                            <img
                              src={product.thumbnail_url}
                              alt={product.name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="text-white text-center">
                              <div className="text-3xl mb-2">📄</div>
                              <div className="text-xs uppercase font-bold">{product.product_type}</div>
                            </div>
                          )}
                          {/* Price Badge */}
                          <div className="absolute top-2 right-2 bg-red-600 text-white px-3 py-1 rounded-full text-sm font-bold">
                            ${product.price.toFixed(2)}
                          </div>
                        </div>

                        {/* Product Info */}
                        <div className="p-4 flex-grow flex flex-col">
                          {/* Category Badge */}
                          <div className="mb-2">
                            <span className="inline-block bg-forgePurple/20 text-forgePurple text-xs px-2 py-1 rounded-full font-medium">
                              {product.category}
                            </span>
                          </div>

                          {/* Product Name */}
                          <h3 className="text-sm font-bold text-white mb-2 line-clamp-2">
                            {product.name}
                          </h3>

                          {/* Description */}
                          <p className="text-xs text-techGray-400 mb-3 line-clamp-2">
                            {product.description}
                          </p>

                          {/* Seller Info */}
                          {product.seller_name && (
                            <p className="text-xs text-techGray-500 mb-2">
                              by <span className="font-medium text-techGray-300">{product.seller_name}</span>
                            </p>
                          )}

                          {/* Rating & Stats */}
                          <div className="flex items-center justify-between text-xs text-techGray-400 mb-3">
                            <div className="flex items-center gap-1">
                              <Star size={14} className="text-yellow-400 fill-yellow-400" />
                              <span>{product.average_rating?.toFixed(1) || 'N/A'}</span>
                            </div>
                            {product.sales_count > 0 && (
                              <div className="flex items-center gap-1">
                                <Download size={14} />
                                <span>{product.sales_count} sold</span>
                              </div>
                            )}
                          </div>

                          {/* Actions */}
                          <div className="space-y-2 mt-auto">
                            <Link href={`/marketplace/digital-products/${product.id}`} className="w-full block">
                              <Button className="w-full text-white border border-techGray-700 hover:border-forgePurple hover:bg-forgePurple/10 font-medium" size="sm">
                                <Eye size={16} className="mr-1" />
                                View Details
                              </Button>
                            </Link>
                            <Button
                              onClick={() => addToCart(product.id)}
                              disabled={addingToCart === product.id}
                              className="w-full bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90 text-white font-bold flex items-center justify-center gap-2 text-sm disabled:opacity-50"
                              size="sm"
                            >
                              <ShoppingCart size={16} />
                              {addingToCart === product.id ? 'Adding...' : 'Add to Cart'}
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="flex justify-center items-center gap-2 mt-8">
                      <Button
                        onClick={() => setPage(Math.max(1, page - 1))}
                        disabled={page === 1}
                        variant="outline"
                      >
                        Previous
                      </Button>

                      <div className="flex items-center gap-1">
                        {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
                          <button
                            key={pageNum}
                            onClick={() => setPage(pageNum)}
                            className={`px-3 py-2 rounded ${
                              page === pageNum
                                ? 'bg-blue-600 text-white'
                                : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                            }`}
                          >
                            {pageNum}
                          </button>
                        ))}
                      </div>

                      <Button
                        onClick={() => setPage(Math.min(totalPages, page + 1))}
                        disabled={page === totalPages}
                        variant="outline"
                      >
                        Next
                      </Button>
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}
