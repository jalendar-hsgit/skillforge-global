import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Button } from '@/components/Button';
import { useRouter } from 'next/router';
import { ShoppingCart, Star, Download, ArrowLeft, Share2, AlertCircle } from 'lucide-react';
import Link from 'next/link';

interface DigitalProductDetail {
  id: number;
  name: string;
  slug: string;
  description: string;
  detailed_description?: string;
  price: number;
  category: string;
  product_type: string;
  status: string;
  sales_count: number;
  average_rating: number;
  seller_id: number;
  seller_name?: string;
  seller_email?: string;
  thumbnail_url?: string;
  file_size?: string;
  download_count?: number;
  created_at?: string;
  updated_at?: string;
  file_url?: string;
  preview_url?: string;
}

export default function ProductDetailsPage() {
  const router = useRouter();
  const { id } = router.query;
  const [product, setProduct] = useState<DigitalProductDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [addingToCart, setAddingToCart] = useState(false);
  const [addedSuccess, setAddedSuccess] = useState(false);

  useEffect(() => {
    if (!id) return;
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/digital-products/${id}`,
        { credentials: 'include' }
      );

      if (!response.ok) {
        setError('Product not found');
        return;
      }

      const data = await response.json();
      setProduct(data);
    } catch (error) {
      console.error('Error fetching product:', error);
      setError('Failed to load product details');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!product) return;

    setAddingToCart(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/cart/add-digital-product`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          product_id: product.id,
        }),
      });

      if (response.status === 401) {
        localStorage.setItem('pendingCartProductId', product.id.toString());
        router.push('/auth/login?redirect=/marketplace/digital-products');
        return;
      }

      if (response.ok) {
        setAddedSuccess(true);
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
            <p className="text-techGray-400">Loading product details...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!product || error) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-deepTech via-deepTech-900 to-deepTech py-12">
          <div className="container">
            <div className="mb-8">
              <Link href="/marketplace/digital-products" className="inline-flex items-center gap-2 text-techGray-400 hover:text-white transition-colors">
                <ArrowLeft className="w-5 h-5" />
                Back to Products
              </Link>
            </div>
            <div className="bg-deepTech-800 rounded-2xl p-8 border border-red-500/20 text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-white mb-2">Product Not Found</h1>
              <p className="text-techGray-400 mb-6">{error || 'The product you are looking for does not exist.'}</p>
              <Link href="/marketplace/digital-products">
                <Button>Browse Products</Button>
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
          <Link href="/marketplace/digital-products" className="inline-flex items-center gap-2 text-techGray-400 hover:text-white transition-colors mb-8">
            <ArrowLeft className="w-5 h-5" />
            Back to Digital Products
          </Link>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Product Image */}
            <div className="lg:col-span-2">
              <div className="bg-gradient-to-br from-forgePurple/20 to-neuralBlue/20 rounded-2xl aspect-video flex items-center justify-center mb-8 border border-techGray-800">
                {product.thumbnail_url ? (
                  <img src={product.thumbnail_url} alt={product.name} className="w-full h-full object-cover rounded-2xl" />
                ) : (
                  <div className="text-center">
                    <div className="text-6xl mb-4">📄</div>
                    <p className="text-techGray-400 uppercase font-bold">{product.product_type}</p>
                  </div>
                )}
              </div>

              {/* Description */}
              <div className="bg-deepTech-800 rounded-2xl p-8 border border-techGray-800">
                <h2 className="text-2xl font-bold text-white mb-4">About this product</h2>
                <p className="text-techGray-300 leading-relaxed whitespace-pre-wrap mb-6">
                  {product.detailed_description || product.description}
                </p>

                {/* Product Details */}
                <div className="grid sm:grid-cols-2 gap-6 pt-6 border-t border-techGray-700">
                  <div>
                    <p className="text-techGray-400 text-sm mb-2">Category</p>
                    <p className="text-white font-semibold">{product.category}</p>
                  </div>
                  <div>
                    <p className="text-techGray-400 text-sm mb-2">Type</p>
                    <p className="text-white font-semibold capitalize">{product.product_type}</p>
                  </div>
                  {product.file_size && (
                    <div>
                      <p className="text-techGray-400 text-sm mb-2">File Size</p>
                      <p className="text-white font-semibold">{product.file_size}</p>
                    </div>
                  )}
                  <div>
                    <p className="text-techGray-400 text-sm mb-2">Downloads</p>
                    <p className="text-white font-semibold flex items-center gap-2">
                      <Download className="w-4 h-4" />
                      {product.download_count || product.sales_count || 0}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1">
              {/* Price Card */}
              <div className="bg-gradient-to-br from-forgePurple to-neuralBlue rounded-2xl p-8 mb-8 shadow-glow">
                <div className="text-white">
                  <p className="text-techGray-200 text-sm mb-2">Price</p>
                  <p className="text-4xl font-black mb-6">${product.price.toFixed(2)}</p>

                  {addedSuccess ? (
                    <div className="w-full py-3 px-4 rounded-lg bg-green-500/20 text-green-400 text-center font-semibold flex items-center justify-center gap-2 mb-4">
                      ✓ Added to cart!
                    </div>
                  ) : (
                    <Button
                      onClick={handleAddToCart}
                      disabled={addingToCart}
                      className="w-full bg-white text-forgePurple font-bold hover:bg-gray-100 disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {addingToCart ? (
                        <>
                          <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                          Adding...
                        </>
                      ) : (
                        <>
                          <ShoppingCart className="w-5 h-5" />
                          Add to Cart
                        </>
                      )}
                    </Button>
                  )}
                </div>
              </div>

              {/* Seller Info */}
              {product.seller_name && (
                <div className="bg-deepTech-800 rounded-2xl p-6 border border-techGray-800 mb-8">
                  <p className="text-techGray-400 text-sm mb-2">Seller</p>
                  <p className="text-white font-bold text-lg mb-2">{product.seller_name}</p>
                  {product.seller_email && (
                    <p className="text-techGray-400 text-sm">{product.seller_email}</p>
                  )}
                </div>
              )}

              {/* Rating */}
              {product.average_rating > 0 && (
                <div className="bg-deepTech-800 rounded-2xl p-6 border border-techGray-800 mb-8">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="flex items-center">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-5 h-5 ${i < Math.round(product.average_rating) ? 'fill-yellow-500 text-yellow-500' : 'text-techGray-600'}`}
                        />
                      ))}
                    </div>
                    <span className="text-white font-bold">{product.average_rating.toFixed(1)}</span>
                  </div>
                  <p className="text-techGray-400 text-sm">{product.sales_count} customers</p>
                </div>
              )}

              {/* Share Button */}
              <Button
                variant="outline"
                className="w-full flex items-center justify-center gap-2"
              >
                <Share2 className="w-5 h-5" />
                Share
              </Button>
            </div>
          </div>

          {/* Related Products */}
          <div className="mt-16 border-t border-techGray-800 pt-12">
            <h2 className="text-2xl font-bold text-white mb-8">More from {product.category}</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <p className="text-techGray-400">More products in this category coming soon...</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
