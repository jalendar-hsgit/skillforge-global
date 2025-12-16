import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import Button from '../components/Button';
import Card from '../components/Card';
import { API_BASE } from '../lib/apiBase';

export default function Marketplace() {
  const [products, setProducts] = useState([]);
  const [sellers, setSellers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [category, setCategory] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [sortBy, setSortBy] = useState('popularity');
  const [activeTab, setActiveTab] = useState('browse');
  const [sellerAccount, setSellerAccount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState(null);

  useEffect(() => {
    fetchProducts();
    fetchTopSellers();
    fetchSellerAccount();
  }, [searchQuery, category, minPrice, maxPrice, sortBy]);

  const fetchProducts = async () => {
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      if (category) params.append('category', category);
      if (minPrice) params.append('min_price', minPrice);
      if (maxPrice) params.append('max_price', maxPrice);
      params.append('sort_by', sortBy);

      const response = await fetch(`${API_BASE}/api/v1x/marketplace/digital-products?${params}`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setProducts(data.products);
      }
    } catch (error) {
      console.error('Failed to fetch products:', error);
    }
  };

  const fetchTopSellers = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1x/marketplace/top-sellers`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setSellers(data);
      }
    } catch (error) {
      console.error('Failed to fetch sellers:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSellerAccount = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1x/marketplace/seller/account`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setSellerAccount(data);
      }
    } catch (error) {
      // User is not a seller, which is fine
    }
  };

  const handlePurchase = async (productId) => {
    try {
      const response = await fetch(
        `${API_BASE}/api/v1x/marketplace/digital-products/${productId}/purchase`,
        {
          method: 'POST',
          credentials: 'include',
        }
      );
      if (response.ok) {
        alert('Purchase successful!');
        setSelectedProduct(null);
      }
    } catch (error) {
      console.error('Purchase failed:', error);
    }
  };

  const categories = ['Programming', 'Design', 'Data Science', 'Business', 'Marketing'];

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Marketplace</h1>
          <p className="text-xl text-gray-600">Discover and purchase digital products from expert creators</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b border-gray-200">
          {['browse', 'sellers', 'my-purchases', 'become-seller'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-medium capitalize transition ${
                activeTab === tab
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.replace('-', ' ')}
            </button>
          ))}
        </div>

        {/* Browse Tab */}
        {activeTab === 'browse' && (
          <div className="grid lg:grid-cols-4 gap-8">
            {/* Sidebar Filters */}
            <div className="lg:col-span-1">
              <Card className="sticky top-20">
                <div className="p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-6">Filters</h2>

                  {/* Search */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search products..."
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                    />
                  </div>

                  {/* Category */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-3">Category</label>
                    <div className="space-y-2">
                      {categories.map((cat) => (
                        <label key={cat} className="flex items-center">
                          <input
                            type="radio"
                            name="category"
                            value={cat}
                            checked={category === cat}
                            onChange={(e) => setCategory(e.target.value)}
                            className="rounded"
                          />
                          <span className="ml-2 text-gray-700">{cat}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Price Range */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Price Range</label>
                    <div className="flex gap-2">
                      <input
                        type="number"
                        value={minPrice}
                        onChange={(e) => setMinPrice(e.target.value)}
                        placeholder="Min"
                        className="w-1/2 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                      <input
                        type="number"
                        value={maxPrice}
                        onChange={(e) => setMaxPrice(e.target.value)}
                        placeholder="Max"
                        className="w-1/2 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                  </div>

                  {/* Sort */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                    >
                      <option value="popularity">Most Popular</option>
                      <option value="newest">Newest</option>
                      <option value="price_low">Price: Low to High</option>
                      <option value="price_high">Price: High to Low</option>
                      <option value="rating">Highest Rated</option>
                    </select>
                  </div>
                </div>
              </Card>
            </div>

            {/* Products Grid */}
            <div className="lg:col-span-3">
              {products.length > 0 ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {products.map((product) => (
                    <Card
                      key={product.id}
                      className="cursor-pointer hover:shadow-lg transition"
                      onClick={() => setSelectedProduct(product)}
                    >
                      <div className="h-full flex flex-col">
                        {/* Thumbnail */}
                        <div className="w-full h-40 bg-gradient-to-br from-blue-400 to-purple-500 relative">
                          {product.is_featured && (
                            <div className="absolute top-2 right-2 bg-yellow-400 text-gray-900 px-3 py-1 rounded-full text-xs font-bold">
                              Featured
                            </div>
                          )}
                        </div>

                        {/* Content */}
                        <div className="p-4 flex-1 flex flex-col">
                          <h3 className="font-bold text-gray-900 line-clamp-2 mb-2">{product.name}</h3>
                          <p className="text-sm text-gray-600 line-clamp-2 mb-3 flex-1">{product.description}</p>

                          {/* Category and Rating */}
                          <div className="flex justify-between items-center mb-4">
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                              {product.category}
                            </span>
                            <div className="flex items-center gap-1">
                              <span className="text-yellow-500">★</span>
                              <span className="text-sm font-medium text-gray-700">
                                {product.average_rating.toFixed(1)}
                              </span>
                            </div>
                          </div>

                          {/* Price and Sales */}
                          <div className="flex justify-between items-center mb-4">
                            <p className="text-2xl font-bold text-blue-600">${product.price}</p>
                            <p className="text-xs text-gray-500">{product.sales_count} sold</p>
                          </div>

                          {/* Purchase Button */}
                          <Button
                            onClick={(e) => {
                              e.stopPropagation();
                              handlePurchase(product.id);
                            }}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition"
                          >
                            Purchase
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card>
                  <div className="p-12 text-center">
                    <p className="text-gray-600 text-lg">No products found</p>
                  </div>
                </Card>
              )}
            </div>
          </div>
        )}

        {/* Sellers Tab */}
        {activeTab === 'sellers' && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sellers.map((seller) => (
              <Card key={seller.id}>
                <div className="p-6">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 mb-4"></div>
                  <h3 className="text-xl font-bold text-gray-900 mb-1">{seller.store_name}</h3>
                  <p className={`text-sm font-medium mb-4 ${
                    seller.seller_tier === 'platinum' ? 'text-purple-600' :
                    seller.seller_tier === 'gold' ? 'text-yellow-600' :
                    seller.seller_tier === 'silver' ? 'text-gray-400' :
                    'text-amber-600'
                  }`}>
                    {seller.seller_tier.charAt(0).toUpperCase() + seller.seller_tier.slice(1)}
                  </p>

                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Products:</span>
                      <span className="font-semibold text-gray-900">{seller.products_count}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Total Sales:</span>
                      <span className="font-semibold text-gray-900">{seller.total_sales}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Rating:</span>
                      <span className="font-semibold text-gray-900">
                        ★ {seller.average_rating.toFixed(1)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Revenue:</span>
                      <span className="font-semibold text-green-600">${seller.total_revenue.toFixed(2)}</span>
                    </div>
                  </div>

                  <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition">
                    Visit Store
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* My Purchases Tab */}
        {activeTab === 'my-purchases' && (
          <Card>
            <div className="p-12 text-center">
              <p className="text-gray-600 text-lg mb-4">Your purchases will appear here</p>
              <Button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition">
                Browse Products
              </Button>
            </div>
          </Card>
        )}

        {/* Become Seller Tab */}
        {activeTab === 'become-seller' && (
          <div className="max-w-2xl mx-auto">
            {sellerAccount ? (
              <Card>
                <div className="p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Your Seller Account</h2>
                  <div className="space-y-4">
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-gray-600 text-sm mb-1">Store Name</p>
                      <p className="text-xl font-semibold text-gray-900">{sellerAccount.store_name}</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-gray-600 text-sm mb-1">Total Revenue</p>
                      <p className="text-xl font-semibold text-green-600">${sellerAccount.total_revenue.toFixed(2)}</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-gray-600 text-sm mb-1">Seller Tier</p>
                      <p className="text-xl font-semibold text-gray-900">
                        {sellerAccount.seller_tier.charAt(0).toUpperCase() + sellerAccount.seller_tier.slice(1)}
                      </p>
                    </div>
                  </div>
                  <Button className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition">
                    Create New Product
                  </Button>
                </div>
              </Card>
            ) : (
              <Card>
                <div className="p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Start Selling Today</h2>
                  <p className="text-gray-600 mb-6">
                    Join thousands of creators earning money by selling digital products on our marketplace.
                  </p>

                  <div className="grid md:grid-cols-3 gap-4 mb-8">
                    <div className="p-4 border border-gray-200 rounded-lg">
                      <p className="font-semibold text-gray-900 mb-2">✓ Easy Setup</p>
                      <p className="text-sm text-gray-600">Create your seller account in minutes</p>
                    </div>
                    <div className="p-4 border border-gray-200 rounded-lg">
                      <p className="font-semibold text-gray-900 mb-2">✓ Keep 70%</p>
                      <p className="text-sm text-gray-600">We take only 30% platform fee</p>
                    </div>
                    <div className="p-4 border border-gray-200 rounded-lg">
                      <p className="font-semibold text-gray-900 mb-2">✓ Global Reach</p>
                      <p className="text-sm text-gray-600">Sell to customers worldwide</p>
                    </div>
                  </div>

                  <Button className="w-full bg-green-600 hover:bg-green-700 text-white py-3 text-lg rounded-lg transition">
                    Create Seller Account
                  </Button>
                </div>
              </Card>
            )}
          </div>
        )}

        {/* Product Detail Modal */}
        {selectedProduct && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <Card className="max-w-2xl w-full max-h-96 overflow-y-auto">
              <div className="p-8">
                <button
                  onClick={() => setSelectedProduct(null)}
                  className="float-right text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">{selectedProduct.name}</h2>
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-yellow-500">★</span>
                  <span className="font-medium text-gray-700">{selectedProduct.average_rating.toFixed(1)}</span>
                  <span className="text-gray-500">({selectedProduct.review_count} reviews)</span>
                </div>

                <p className="text-gray-600 mb-6">{selectedProduct.description}</p>

                {selectedProduct.features && selectedProduct.features.length > 0 && (
                  <div className="mb-6">
                    <h3 className="font-semibold text-gray-900 mb-3">Features</h3>
                    <ul className="space-y-2">
                      {selectedProduct.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center text-gray-700">
                          <span className="text-green-600 mr-2">✓</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="border-t border-gray-200 pt-6 flex justify-between items-center">
                  <p className="text-3xl font-bold text-blue-600">${selectedProduct.price}</p>
                  <Button
                    onClick={() => {
                      handlePurchase(selectedProduct.id);
                    }}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg transition"
                  >
                    Purchase Now
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </Layout>
  );
}
