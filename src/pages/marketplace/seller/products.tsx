import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { useRouter } from 'next/router';
import { Plus, Edit2, Trash2, Eye, Archive, Search } from 'lucide-react';
import Link from 'next/link';
import { useAuthCheck } from '@/lib/protectedRoute';

interface Product {
  id: number;
  name: string;
  slug: string;
  product_type: string;
  category: string;
  price: number;
  status: string;
  sales_count: number;
  average_rating: number;
  created_at: string;
}

export default function SellerProducts() {
  const router = useRouter();
  const { isAuthorized, loading: authLoading } = useAuthCheck('seller');
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  useEffect(() => {
    if (!authLoading && isAuthorized) {
      fetchProducts();
    }
  }, [filterStatus, authLoading, isAuthorized]);

  const fetchProducts = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login?redirect=/marketplace/seller/products');
        return;
      }

      const url = new URL(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/seller/products`);
      if (filterStatus !== 'all') {
        url.searchParams.append('status', filterStatus);
      }

      const res = await fetch(url.toString(), {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        const data = await res.json();
        setProducts(data.products || []);
      } else if (res.status === 401) {
        router.push('/login');
      }
    } catch (err) {
      setError('Failed to load products');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const deleteProduct = async (id: number) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/seller/products/${id}`,
        {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (res.ok) {
        setProducts(products.filter(p => p.id !== id));
        setDeleteConfirm(null);
      }
    } catch (err) {
      console.error('Failed to delete product:', err);
    }
  };

  const filteredProducts = products.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (authLoading || loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!isAuthorized) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 text-yellow-800 dark:text-yellow-200">
            You must be a seller to access this page. Please contact support if you need seller access.
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Products</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your digital products</p>
          </div>
          <Link href="/marketplace/seller/create-product">
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Add Product
            </button>
          </Link>
        </div>

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-800 dark:text-red-200 mb-6">
            {error}
          </div>
        )}

        {/* Search and Filter */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search products..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
          >
            <option value="all">All Status</option>
            <option value="draft">Draft</option>
            <option value="published">Published</option>
            <option value="archived">Archived</option>
          </select>
        </div>

        {/* Products Table */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          {filteredProducts.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-600 dark:text-gray-400">
                {searchQuery ? 'No products found.' : 'No products yet. Create your first product!'}
              </p>
              {!searchQuery && (
                <Link href="/marketplace/seller/create-product" className="text-blue-600 dark:text-blue-400 hover:underline mt-2 block">
                  Create Product
                </Link>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50">
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Product</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Price</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Sales</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Status</th>
                    <th className="px-6 py-3 text-center text-xs font-semibold text-gray-700 dark:text-gray-300">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProducts.map((product) => (
                    <tr key={product.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{product.name}</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{product.category}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                          {product.product_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm font-semibold text-gray-900 dark:text-white">
                        ${product.price.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
                        {product.sales_count}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`text-xs font-semibold px-3 py-1 rounded-full ${
                          product.status === 'published' ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300' :
                          product.status === 'draft' ? 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300' :
                          'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
                        }`}>
                          {product.status}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex justify-center gap-2">
                          {product.status === 'published' && (
                            <button
                              title="View"
                              className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition"
                            >
                              <Eye className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                            </button>
                          )}
                          <Link href={`/marketplace/seller/create-product?productId=${product.id}`}>
                            <button
                              title="Edit"
                              className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition"
                            >
                              <Edit2 className="w-4 h-4 text-green-600 dark:text-green-400" />
                            </button>
                          </Link>
                          <button
                            title="Delete"
                            onClick={() => setDeleteConfirm(product.id)}
                            className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition"
                          >
                            <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Delete Confirmation Modal */}
        {deleteConfirm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-sm">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Delete Product</h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Are you sure you want to delete this product? This action cannot be undone.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setDeleteConfirm(null)}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  onClick={() => deleteProduct(deleteConfirm)}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
